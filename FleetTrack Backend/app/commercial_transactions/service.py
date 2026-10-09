import calendar
import hashlib
import json
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException
from sqlalchemy import select, func, text, and_, or_
from app.contra_vouchers import repository as common
from app.payment_vouchers import repository as payments
from . import repository as r

ZERO = Decimal('0')


def money(value):
    return Decimal(value or 0).quantize(Decimal('0.00001'), rounding=ROUND_HALF_UP)


def digest(value):
    return hashlib.sha256(json.dumps(value, default=str, sort_keys=True).encode()).hexdigest()


def require(db, table, key, value, label):
    found = r.row(db, table, key, value) if value is not None else None
    if found is None:
        raise HTTPException(422, f'{label} must be selected from existing records')
    return found


def lock_family(db, kind):
    cfg = r.config(kind)
    if db.bind.dialect.name == 'mssql':
        # All writes in a document family share a lock, including empty-table numbering.
        result = db.execute(text("DECLARE @result int; EXEC @result=sys.sp_getapplock @Resource=:resource, @LockMode='Exclusive', @LockOwner='Transaction', @LockTimeout=10000; SELECT @result"), {'resource': 'FleetTrack:transactions:' + kind}).scalar()
        if result is None or result < 0:
            raise HTTPException(409, 'Transaction is busy. Please retry')
    return cfg


def get_document(db, kind, identity, lock=False):
    cfg = r.config(kind)
    master = r.row(db, cfg.master, cfg.key, identity, lock)
    if master is None:
        raise HTTPException(404, 'Transaction not found')
    master = dict(master)
    lines = r.children(db, cfg, identity)
    allocations = []
    if kind == 'debit-notes':
        balance = r.T['tbl_PartyBalance']
        allocations = [dict(row) for row in db.execute(select(balance.c.ledgerId,
            balance.c.voucherTypeId, balance.c.voucherNo,
            (func.coalesce(balance.c.debit, 0) + func.coalesce(balance.c.credit, 0)).label('amount')
        ).where(balance.c.againstVoucherTypeId == master['voucherTypeId'],
            balance.c.againstVoucherNo == master['voucherNo'], balance.c.referenceType == 'Against')).mappings()]
    version = digest({'header': master, 'lines': lines, 'allocations': allocations})
    if cfg.tax:
        tax = r.T[cfg.tax]
        taxes = [dict(x) for x in db.execute(select(tax).where(tax.c[cfg.key] == identity)).mappings()]
    else:
        taxes = []
    for line in lines:
        line['id'] = int(line[cfg.detail_key])
    if 'ledgerId' in master and master['ledgerId']:
        ledger = r.row(db, 'tbl_AccountLedger', 'ledgerId', master['ledgerId'])
        master['partyName'] = ledger['ledgerName'] if ledger else None
    return {'id': identity, 'header': master, 'lines': lines, 'taxes': taxes, 'allocations': allocations, 'version': version}


def numbering(db, cfg, date, manual):
    vt = r.T['tbl_VoucherType']
    voucher = db.execute(select(vt).where(vt.c.voucherTypeName == cfg.voucher_name, vt.c.isActive == True)).mappings().first()
    if voucher is None:
        raise HTTPException(422, 'Voucher type is not configured or active')
    type_id = int(voucher['voucherTypeId'])
    common.lock_numbering_scope(db, type_id)
    rule = common.get_suffix_prefix(db, type_id, date)
    m = r.T[cfg.master]
    if voucher['methodOfVoucherNumbering'] == 'Manual':
        if not manual:
            raise HTTPException(422, 'Voucher number is required')
        internal = manual
        display = manual
    elif voucher['methodOfVoucherNumbering'] == 'Automatic':
        # TRY_CONVERT preserves nonnumeric historical numbers without breaking the sequence.
        if db.bind.dialect.name == 'mssql':
            current = db.execute(text(f'SELECT MAX(TRY_CONVERT(bigint,voucherNo)) FROM [{cfg.master}] WHERE voucherTypeId=:vt'), {'vt': type_id}).scalar()
        else:
            numbers = db.execute(select(m.c.voucherNo).where(m.c.voucherTypeId == type_id)).scalars().all()
            current = max([int(n) for n in numbers if str(n).isdigit()] or [0])
        internal = str(max(int(current or 0) + 1, int(rule['startIndex'] or 1) if rule else 1))
        if rule and rule['prefillWithZero']:
            internal = internal.zfill(int(rule['widthOfNumericalPart'] or 0))
        display = f"{rule['prefix'] or ''}{internal}{rule['suffix'] or ''}" if rule else internal
    else:
        raise HTTPException(422, 'Unsupported voucher numbering configuration')
    if db.execute(select(m.c[cfg.key]).where(m.c.voucherTypeId == type_id, m.c.invoiceNo == display)).first():
        raise HTTPException(409, 'Voucher number already exists')
    return dict(voucherTypeId=type_id, voucherNo=internal, invoiceNo=display, suffixPrefixId=rule['suffixprefixId'] if rule else 0)


def check_editable(db, kind, doc):
    h, cfg = doc['header'], r.config(kind)
    if h.get('isPosted'):
        raise HTTPException(409, 'Posted transactions are read-only')
    if kind == 'purchase-orders':
        p = r.T['tbl_PurchaseMaster']
        if db.execute(select(p.c.purchaseMasterId).where(p.c.purchaseOrderMasterId == doc['id']).limit(1)).first():
            raise HTTPException(409, 'An invoiced purchase order cannot be changed or deleted')
    if kind == 'sales-quotations':
        d = r.T['tbl_DeliveryNoteDetails']
        ids = [line['id'] for line in doc['lines']]
        if ids and db.execute(select(d.c.deliveryNoteDetailsId).where(d.c.quotationDetails1Id.in_(ids)).limit(1)).first():
            raise HTTPException(409, 'Quotation is referenced by a delivery note')
    if kind == 'vehicle-finance' and any(line.get('PDCId') or line.get('isPaid') for line in doc['lines']):
        raise HTTPException(409, 'Finance schedule has linked or paid installments')
    if h.get('voucherTypeId'):
        if payments.has_bank_reconciliation(db, h['voucherTypeId'], h['voucherNo']) or payments.has_external_party_reference(db, h['voucherTypeId'], h['voucherNo']):
            raise HTTPException(409, 'Transaction has reconciliations or downstream allocations')


def validate_party(db, kind, ledger_id):
    ledger = require(db, 'tbl_AccountLedger', 'ledgerId', ledger_id, 'Party')
    group = require(db, 'tbl_AccountGroup', 'accountGroupId', ledger['accountGroupId'], 'Account group')
    allowed = {'sundry creditors'} if kind in ('purchase-orders', 'purchase-invoices') else {'sundry debtors', 'cash-in hand'}
    if kind == 'vehicle-finance':
        if int(ledger['accountGroupId']) != 54:
            raise HTTPException(422, 'Select a financing-party account')
    elif str(group['accountGroupName']).lower() not in allowed:
        raise HTTPException(422, 'Party account is not eligible for this transaction')
    return ledger


def build_lines(db, kind, payload):
    if not payload.lines:
        raise HTTPException(422, 'At least one line is required')
    result, taxes = [], defaultdict(lambda: ZERO)
    for index, line in enumerate(payload.lines, 1):
        if not line.description or line.qty <= 0:
            raise HTTPException(422, 'Each line requires a description and positive quantity')
        require(db, 'tbl_Unit', 'unitId', line.unitId, 'Unit')
        if line.vehicleId:
            require(db, 'VT_Veh_VehicleMaster', 'VehicleId', line.vehicleId, 'Vehicle')
        values = dict(qty=line.qty, rate=line.rate, unitId=line.unitId, amount=money(line.qty * line.rate))
        if kind in ('purchase-orders', 'sales-quotations'):
            values.update(itemDescription=line.description)
            values['slno' if kind == 'sales-quotations' else 'slNo'] = index
            if kind == 'purchase-orders':
                values['vehicleId'] = line.vehicleId
        else:
            tax = require(db, 'tbl_Tax', 'taxId', line.taxId, 'Tax')
            if tax['isActive'] is False:
                raise HTTPException(422, 'Tax is inactive')
            gross = values['amount']
            tax_amount = money(gross * Decimal(tax['rate'] or 0) / 100)
            taxes[line.taxId] += tax_amount
            values.update(description=line.description, vehicleId=line.vehicleId, taxId=line.taxId,
                taxAmount=tax_amount, grossAmount=gross, amount=money(gross + tax_amount), slNo=index)
            if kind == 'purchase-invoices':
                if line.productId:
                    table, key = ('tbl_FixedAssetMaster', 'fixedAssetId') if payload.purchaseMode == 'asset' else ('tbl_Product', 'productId')
                    require(db, table, key, line.productId, 'Item')
                elif payload.purchaseMode != 'misc':
                    raise HTTPException(422, 'Select an item for asset or inventory purchases')
                values.update(productId=line.productId or 0, orderDetailsId=line.sourceLineId or 0)
            else:
                item = require(db, 'tbl_SalesDetailItemType', 'ItemType', line.itemTypeId, 'Item type')
                if item['IsActive'] is False:
                    raise HTTPException(422, 'Item type is inactive')
                values.update(itemTypeId=line.itemTypeId, netAmount=gross, discount=ZERO, salesDetailsId=line.sourceLineId or 0)
        result.append(values)
    total = money(sum(line['amount'] for line in result))
    if payload.discount > total or (kind in ('purchase-orders', 'sales-quotations') and payload.discount):
        raise HTTPException(422, 'Invalid bill discount')
    return result, taxes, total


def validate_source(db, kind, payload, identity):
    if kind == 'purchase-invoices':
        if not payload.sourceId:
            if any(line.sourceLineId for line in payload.lines):
                raise HTTPException(422, 'Source lines require a purchase order')
            return
        source = r.row(db, 'tbl_PurchaseOrderMaster', 'purchaseOrderMasterId', payload.sourceId, True)
        if not source or source['cancelled'] or int(source['ledgerId']) != payload.ledgerId or int(source['exchangeRateId']) != payload.exchangeRateId:
            raise HTTPException(422, 'Order must be open and match supplier and currency')
        requested = defaultdict(lambda: ZERO)
        pd = r.T['tbl_PurchaseDetails']
        for line in payload.lines:
            source_line = require(db, 'tbl_PurchaseOrderDetails', 'purchaseOrderDetailsId', line.sourceLineId, 'Order line')
            if int(source_line['purchaseOrderMasterId']) != payload.sourceId or source_line['unitId'] != line.unitId:
                raise HTTPException(422, 'Order line or unit does not match the selected order')
            requested[line.sourceLineId] += line.qty
            used_query = select(func.coalesce(func.sum(pd.c.qty), 0)).where(pd.c.orderDetailsId == line.sourceLineId)
            if identity:
                used_query = used_query.where(pd.c.purchaseMasterId != identity)
            used = db.execute(used_query).scalar_one()
            if requested[line.sourceLineId] + used > source_line['qty']:
                raise HTTPException(409, 'Purchase quantity exceeds the remaining order quantity')
    elif kind == 'credit-notes':
        if not payload.sourceId:
            if any(line.sourceLineId for line in payload.lines):
                raise HTTPException(422, 'Source lines require a sales invoice')
            return
        source = r.row(db, 'tbl_SalesMaster', 'salesMasterId', payload.sourceId, True)
        if not source or not source['isPosted'] or source['ledgerId'] != payload.ledgerId or source['exchangeRateId'] != payload.exchangeRateId:
            raise HTTPException(422, 'Select a posted invoice for the same customer and currency')
        details = r.T['tbl_SalesReturnDetails']
        requested = defaultdict(lambda: ZERO)
        for line in payload.lines:
            original = require(db, 'tbl_SalesDetails', 'salesDetailsId', line.sourceLineId, 'Invoice line')
            if original['salesMasterId'] != payload.sourceId or original['unitId'] != line.unitId or original['taxId'] != line.taxId or line.rate > original['rate']:
                raise HTTPException(422, 'Credit line must match its source invoice')
            requested[line.sourceLineId] += line.qty
            used = select(func.coalesce(func.sum(details.c.qty), 0)).where(details.c.salesDetailsId == line.sourceLineId)
            if identity:
                used = used.where(details.c.salesReturnMasterId != identity)
            if db.execute(used).scalar_one() + requested[line.sourceLineId] > original['qty']:
                raise HTTPException(409, 'Credit quantity exceeds the remaining invoice quantity')


def finance_schedule(payload):
    if payload.loanAmount <= 0 or payload.monthlyAmount <= 0 or not payload.chequeDateFrom or not payload.chequeNoFrom.isdigit():
        raise HTTPException(422, 'Positive loan and monthly amounts, first cheque number and date are required')
    last = money(payload.loanAmount - payload.monthlyAmount * (payload.installments - 1))
    if last <= 0 or last > payload.monthlyAmount:
        raise HTTPException(422, 'Installment count and monthly amount must cover the loan exactly, with a final remainder')
    start, rows = payload.chequeDateFrom, []
    for index in range(payload.installments):
        month_index = start.year * 12 + start.month - 1 + index
        year, month = divmod(month_index, 12)
        month += 1
        date = start.replace(year=year, month=month, day=min(start.day, calendar.monthrange(year, month)[1]))
        rows.append(dict(EMIno=index + 1, PDCId=0, bankId=payload.bankId, EMIamount=last if index == payload.installments - 1 else payload.monthlyAmount,
            chequeNo=str(int(payload.chequeNoFrom) + index).zfill(len(payload.chequeNoFrom)), EMIDate=date, isPaid=False))
    return rows


def save_document(db, kind, payload, user_id, identity=None):
    try:
        cfg = lock_family(db, kind)
        m, d = r.T[cfg.master], r.T[cfg.detail]
        existing = get_document(db, kind, identity, True) if identity else None
        request_hash = digest(payload.model_dump(exclude={'expectedVersion'}))
        if existing:
            check_editable(db, kind, existing)
            if payload.expectedVersion != existing['version']:
                raise HTTPException(409, 'Transaction changed. Refresh before saving')
            owned = {line['id'] for line in existing['lines']}
            if any(line.id is not None and line.id not in owned for line in payload.lines):
                raise HTTPException(422, 'Line does not belong to this transaction')
        elif 'extra1' in m.c:
            duplicate = db.execute(select(m).where(m.c.extra1 == 'fttx:' + payload.idempotencyKey)).mappings().first()
            if duplicate:
                if duplicate['extra2'] != request_hash:
                    raise HTTPException(409, 'Save key was already used with different contents')
                return get_document(db, kind, int(duplicate[cfg.key]))
        year = common.get_financial_year(db, payload.date)
        if year is None:
            raise HTTPException(422, 'Date is outside configured financial years')
        header = {cfg.date_key: payload.date, 'narration': payload.narration}
        if kind != 'debit-notes':
            validate_party(db, kind, payload.ledgerId)
            header['ledgerId'] = payload.ledgerId
        if kind not in ('vehicle-finance', 'debit-notes'):
            rate = common.get_exchange_rate(db, payload.exchangeRateId, payload.date)
            if not rate or rate['rate'] <= 0:
                raise HTTPException(422, 'Select a valid date-appropriate exchange rate')
            header.update(exchangeRateId=payload.exchangeRateId, financialYearId=year['financialYearId'])
        if kind == 'vehicle-finance':
            if not payload.manualNumber:
                raise HTTPException(422, 'Finance number is required')
            duplicate = db.execute(select(m.c.financeHeaderId).where(m.c.financeNo == payload.manualNumber, m.c.financeHeaderId != (identity or 0))).first()
            if duplicate:
                raise HTTPException(409, 'Finance number already exists')
            source = r.row(db, 'tbl_PurchaseMaster', 'purchaseMasterId', payload.sourceId, True)
            source_line = require(db, 'tbl_PurchaseDetails', 'purchaseDetailsId', payload.purchaseDetailId, 'Purchased asset line')
            if not source or not source['isPosted'] or not source['isFaPurchase'] or source_line['purchaseMasterId'] != payload.sourceId or source_line['productId'] != payload.assetId:
                raise HTTPException(422, 'Select an asset from a posted fixed-asset purchase')
            if db.execute(select(m.c.financeHeaderId).where(m.c.assetID == payload.assetId, m.c.financeHeaderId != (identity or 0))).first():
                raise HTTPException(409, 'Asset is already financed')
            bank = require(db, 'tbl_AccountLedger', 'ledgerId', payload.bankId, 'Bank')
            if bank['accountGroupId'] != 28:
                raise HTTPException(422, 'Select a bank account')
            header.update(financeNo=payload.manualNumber, purchaseMasterId=payload.sourceId, purchaseDetailId=payload.purchaseDetailId,
                assetID=payload.assetId, purchasedAmount=source_line['amount'], loanAmount=payload.loanAmount, monthlyAmount=payload.monthlyAmount,
                NoOfInstallments=payload.installments, bankId=payload.bankId, chequeNoFrom=payload.chequeNoFrom, chequeDateFrom=payload.chequeDateFrom)
            if not existing:
                header.update(isPosted=False, createdBy=user_id, createdDate=datetime.now())
            lines, taxes = finance_schedule(payload), {}
            for line in lines:
                line.update(createdBy=user_id, createdDate=datetime.now())
        elif kind == 'debit-notes':
            if not payload.lines:
                raise HTTPException(422, 'At least two balanced ledger lines are required')
            if not existing:
                header.update(numbering(db, cfg, payload.date, payload.manualNumber), userId=user_id,
                    extra1='fttx:' + payload.idempotencyKey, extra2=request_hash, extraDate=datetime.now())
            header['financialYearId'] = year['financialYearId']
            lines, taxes = [], {}
            debit, credit = ZERO, ZERO
            ledger_ids = set()
            for line in payload.lines:
                require(db, 'tbl_AccountLedger', 'ledgerId', line.ledgerId, 'Account ledger')
                if line.ledgerId in ledger_ids or line.amount <= 0:
                    raise HTTPException(422, 'Use distinct account ledgers with positive amounts')
                ledger_ids.add(line.ledgerId)
                exchange = common.get_exchange_rate(db, line.exchangeRateId, payload.date)
                if not exchange or exchange['rate'] != 1:
                    raise HTTPException(422, 'Debit notes currently require a base-currency exchange rate of one')
                if bool(line.chequeNo) != bool(line.chequeDate):
                    raise HTTPException(422, 'Cheque number and date must be supplied together')
                dr, cr = (line.amount, ZERO) if line.direction == 'Dr' else (ZERO, line.amount)
                debit, credit = debit + dr, credit + cr
                lines.append(dict(ledgerId=line.ledgerId, debit=dr, credit=cr, exchangeRateId=line.exchangeRateId,
                    chequeNo=line.chequeNo, chequeDate=line.chequeDate))
            if debit != credit or debit <= 0:
                raise HTTPException(422, 'Debit and credit totals must balance')
            header['totalAmount'] = debit
        else:
            if existing:
                if existing['header']['date'].date() != payload.date.date():
                    # Keep saved identity and numbering, while still validating the new period.
                    header['financialYearId'] = year['financialYearId']
            else:
                header.update(numbering(db, cfg, payload.date, payload.manualNumber), userId=user_id,
                    extra1='fttx:' + payload.idempotencyKey, extra2=request_hash, extraDate=datetime.now())
            lines, taxes, total = build_lines(db, kind, payload)
            header['totalAmount'] = total
            if kind == 'purchase-orders':
                if not payload.dueDate or payload.dueDate.date() < payload.date.date():
                    raise HTTPException(422, 'Due date must be on or after order date')
                header.update(dueDate=payload.dueDate, cancelled=payload.cancelled, employeeId=payload.employeeId or 0)
            if kind == 'sales-quotations':
                if payload.employeeId:
                    require(db, 'tbl_Employee', 'employeeId', payload.employeeId, 'Salesperson')
                if payload.pricingLevelId:
                    require(db, 'tbl_PricingLevel', 'pricinglevelId', payload.pricingLevelId, 'Pricing level')
                header.update(employeeId=payload.employeeId or 0, pricinglevelId=payload.pricingLevelId or 0, approved=payload.approved)
            if kind in ('purchase-invoices', 'credit-notes'):
                require(db, 'tbl_AccountLedger', 'ledgerId', payload.accountId, 'Posting account')
                if payload.accountId == payload.ledgerId:
                    raise HTTPException(422, 'Posting account must differ from party account')
                validate_source(db, kind, payload, identity)
                header.update(grandTotal=money(total - payload.discount))
                if not existing:
                    header['isPosted'] = False
                if kind == 'purchase-invoices':
                    header.update(purchaseAccount=payload.accountId, purchaseOrderMasterId=payload.sourceId or 0,
                        vendorInvoiceNo=payload.vendorInvoiceNo, vendorInvoiceDate=payload.invoiceDate or payload.date,
                        creditPeriod=str(payload.creditPeriod), billDiscount=payload.discount, totalTax=money(sum(taxes.values())),
                        isMiscPurchase=payload.purchaseMode == 'misc', isFaPurchase=payload.purchaseMode == 'asset', isInvPurchase=payload.purchaseMode == 'inventory',
                        transportationCompany=payload.transportationCompany, lrNo=payload.lrNo)
                    if payload.vendorInvoiceNo and db.execute(select(m.c.purchaseMasterId).where(m.c.ledgerId == payload.ledgerId,
                        m.c.vendorInvoiceNo == payload.vendorInvoiceNo, m.c.purchaseMasterId != (identity or 0))).first():
                        raise HTTPException(409, 'Vendor invoice number already exists for this supplier')
                else:
                    header.update(salesAccount=payload.accountId, salesMasterId=payload.sourceId or 0, employeeId=payload.employeeId or 0,
                        discount=payload.discount, taxAmount=money(sum(taxes.values())))
        if identity:
            db.execute(m.update().where(m.c[cfg.key] == identity).values(**header))
        else:
            identity = r.insert(db, cfg.master, header)
        # Preserve existing line identities so source references remain stable.
        kept = set()
        for index, line in enumerate(lines):
            line_id = payload.lines[index].id if index < len(payload.lines) and kind != 'vehicle-finance' else None
            values = {**line, cfg.key: identity}
            if line_id:
                db.execute(d.update().where(d.c[cfg.detail_key] == line_id, d.c[cfg.key] == identity).values(**values))
                kept.add(line_id)
            else:
                kept.add(r.insert(db, cfg.detail, values))
        db.execute(d.delete().where(d.c[cfg.key] == identity, d.c[cfg.detail_key].not_in(kept)))
        if cfg.tax:
            t = r.T[cfg.tax]
            db.execute(t.delete().where(t.c[cfg.key] == identity))
            for tax_id, amount in taxes.items():
                db.execute(t.insert().values(**{cfg.key: identity, 'taxId': tax_id, 'taxAmount': amount}))
        if kind == 'debit-notes':
            saved = get_document(db, kind, identity)
            master = saved['header']
            if existing:
                payments.delete_postings(db, master['voucherTypeId'], master['voucherNo'])
                payments.delete_active_allocations(db, master['voucherTypeId'], master['voucherNo'])
            input_by_ledger = {line.ledgerId: line for line in payload.lines}
            for line in saved['lines']:
                source_line = input_by_ledger[int(line['ledgerId'])]
                ledger = require(db, 'tbl_AccountLedger', 'ledgerId', line['ledgerId'], 'Account')
                post_row(db, master, line['ledgerId'], line['debit'], line['credit'], line['id'], line['chequeNo'], line['chequeDate'])
                if source_line.allocations:
                    if sum(a.amount for a in source_line.allocations) != source_line.amount:
                        raise HTTPException(422, 'Against allocations must equal the line amount')
                    seen = set()
                    for allocation in source_line.allocations:
                        key = (allocation.voucherTypeId, allocation.voucherNo)
                        if key in seen:
                            raise HTTPException(422, 'Duplicate Against reference')
                        seen.add(key)
                        reference = open_reference(db, line['ledgerId'], allocation.voucherTypeId, allocation.voucherNo, source_line.direction, True)
                        if not reference or allocation.amount > reference['pendingAmount']:
                            raise HTTPException(409, 'Against amount exceeds the current reference balance')
                        if reference['exchangeRateId'] != source_line.exchangeRateId:
                            raise HTTPException(422, 'Against reference currency must match the ledger line')
                        party_row(db, master, line['ledgerId'], allocation.amount if source_line.direction == 'Dr' else ZERO,
                            allocation.amount if source_line.direction == 'Cr' else ZERO, source_line.exchangeRateId, reference)
                elif ledger['billByBill']:
                    party_row(db, master, line['ledgerId'], line['debit'], line['credit'], source_line.exchangeRateId)
            check_posting_balance(db, master)
        result = get_document(db, kind, identity)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def delete_document(db, kind, identity, version):
    try:
        cfg = lock_family(db, kind)
        doc = get_document(db, kind, identity, True)
        if doc['version'] != version:
            raise HTTPException(409, 'Transaction changed. Refresh before deleting')
        check_editable(db, kind, doc)
        if kind == 'debit-notes':
            master = doc['header']
            payments.delete_postings(db, master['voucherTypeId'], master['voucherNo'])
            payments.delete_active_allocations(db, master['voucherTypeId'], master['voucherNo'])
        for table_name in [cfg.tax, cfg.detail, cfg.master]:
            if table_name:
                table = r.T[table_name]
                db.execute(table.delete().where(table.c[cfg.key] == identity))
        db.commit()
    except Exception:
        db.rollback()
        raise


def source_lines(db, kind, identity):
    if kind == 'purchase-orders':
        doc = get_document(db, kind, identity)
        pd = r.T['tbl_PurchaseDetails']
        for line in doc['lines']:
            used = db.execute(select(func.coalesce(func.sum(pd.c.qty), 0)).where(pd.c.orderDetailsId == line['id'])).scalar_one()
            line['remainingQuantity'] = max(ZERO, line['qty'] - used)
        return doc
    if kind == 'purchases':
        return get_document(db, 'purchase-invoices', identity)
    if kind == 'sales':
        master = require(db, 'tbl_SalesMaster', 'salesMasterId', identity, 'Sales invoice')
        detail = r.T['tbl_SalesDetails']
        lines = [dict(row) for row in db.execute(select(detail).where(detail.c.salesMasterId == identity)).mappings()]
        return {'header': dict(master), 'lines': lines}
    raise HTTPException(404, 'Unknown source')


def post_row(db, master, ledger_id, debit, credit, detail_id=0, cheque_no='', cheque_date=None):
    db.execute(r.T['tbl_LedgerPosting'].insert().values(date=master['date'], voucherTypeId=master['voucherTypeId'],
        voucherNo=master['voucherNo'], invoiceNo=master['invoiceNo'], ledgerId=ledger_id, debit=money(debit), credit=money(credit),
        detailsId=detail_id, yearId=master['financialYearId'], chequeNo=cheque_no, chequeDate=cheque_date, extraDate=datetime.now()))


def open_reference(db, ledger_id, voucher_type, voucher_no, direction, lock=False):
    p = r.T['tbl_PartyBalance']
    condition = and_(p.c.ledgerId == ledger_id, p.c.voucherTypeId == voucher_type, p.c.voucherNo == voucher_no)
    if lock:
        db.execute(r.lock_query(db, select(p.c.partyBalanceId).where(condition), p)).all()
    delta = func.coalesce(func.sum(p.c.credit - p.c.debit), 0) if direction == 'Dr' else func.coalesce(func.sum(p.c.debit - p.c.credit), 0)
    result = db.execute(select(p.c.voucherTypeId, p.c.voucherNo, func.max(p.c.invoiceNo).label('invoiceNo'),
        func.max(p.c.exchangeRateId).label('exchangeRateId'), delta.label('pendingAmount')).where(condition)
        .group_by(p.c.voucherTypeId, p.c.voucherNo)).mappings().first()
    return result


def references(db, ledger_id, direction):
    p = r.T['tbl_PartyBalance']
    delta = func.coalesce(func.sum(p.c.credit - p.c.debit), 0) if direction == 'Dr' else func.coalesce(func.sum(p.c.debit - p.c.credit), 0)
    return [dict(row) for row in db.execute(select(p.c.voucherTypeId, p.c.voucherNo, func.max(p.c.invoiceNo).label('invoiceNo'),
        func.max(p.c.exchangeRateId).label('exchangeRateId'), delta.label('pendingAmount')).where(p.c.ledgerId == ledger_id)
        .group_by(p.c.voucherTypeId, p.c.voucherNo).having(delta > 0).order_by(p.c.voucherTypeId, p.c.voucherNo)).mappings()]


def party_row(db, master, ledger_id, debit, credit, rate_id, reference=None, new=False):
    values = dict(date=master['date'], ledgerId=ledger_id, voucherTypeId=master['voucherTypeId'], voucherNo=master['voucherNo'],
        invoiceNo=master['invoiceNo'], againstVoucherTypeId=0, againstVoucherNo='0', againstInvoiceNo='',
        referenceType='New' if new else 'OnAccount', debit=money(debit), credit=money(credit),
        exchangeRateId=rate_id, financialYearId=master['financialYearId'], creditPeriod=int(master.get('creditPeriod') or 0), extraDate=datetime.now())
    if reference:
        values.update(voucherTypeId=reference['voucherTypeId'], voucherNo=reference['voucherNo'], invoiceNo=reference['invoiceNo'],
            againstVoucherTypeId=master['voucherTypeId'], againstVoucherNo=master['voucherNo'], againstInvoiceNo=master['invoiceNo'], referenceType='Against')
    db.execute(r.T['tbl_PartyBalance'].insert().values(**values))


def check_posting_balance(db, master):
    totals = payments.posting_totals(db, master['voucherTypeId'], master['voucherNo'])
    if totals['rowCount'] < 2 or money(totals['debit']) != money(totals['credit']):
        raise HTTPException(409, 'Accounting entries are not balanced')


def create_asset_schedules(db, doc):
    h = doc['header']
    schedule, detail, purchase = r.T['tbl_FixedAssetDeprSchedule'], r.T['tbl_PurchaseDetails'], r.T['tbl_PurchaseMaster']
    seen = set()
    for line in doc['lines']:
        asset_id = line['productId']
        asset = r.row(db, 'tbl_FixedAssetMaster', 'fixedAssetId', asset_id, True)
        if not asset or not asset['isActive'] or asset_id in seen or line['qty'] != 1:
            raise HTTPException(422, 'Asset purchases require distinct active assets with quantity one')
        seen.add(asset_id)
        category = require(db, 'tbl_FixedAssetCategory', 'faCategoryId', asset['fixedAssetCategory'], 'Asset category')
        if category['assetLedgerId'] != h['purchaseAccount']:
            raise HTTPException(422, 'Purchase account must match the asset category ledger')
        if asset['fixedAssetDeprMethod'] != 1 or asset['fixedAssetDeprPeriod'] != 48:
            raise HTTPException(422, 'Only the verified method-1, 48-month asset schedule is enabled')
        for key in ('deprLedgerId', 'accDeprLedgerId'):
            require(db, 'tbl_AccountLedger', 'ledgerId', category[key], 'Depreciation account')
        other = select(detail.c.purchaseDetailsId).select_from(detail.join(purchase, purchase.c.purchaseMasterId == detail.c.purchaseMasterId)).where(
            purchase.c.isFaPurchase == True, detail.c.productId == asset_id, purchase.c.purchaseMasterId != doc['id'])
        if db.execute(other.limit(1)).first() or db.execute(select(schedule.c.depreciationSchedule).where(schedule.c.fixedAssetId == asset_id).limit(1)).first():
            raise HTTPException(409, 'Asset already has an acquisition or depreciation schedule')
        disposal = r.T['tbl_FixedAssetDisposalDetails']
        if db.execute(select(disposal.c.DisposalId).where(disposal.c.FixedAssetId == asset_id).limit(1)).first():
            raise HTTPException(409, 'Disposed assets cannot be acquired again')
        start = h['date']
        end_year = start.year + 4
        end = start.replace(year=end_year, day=min(start.day, calendar.monthrange(end_year, start.month)[1]))
        # All 117 inspected acquisition schedules use the tax-inclusive line amount.
        db.execute(schedule.insert().values(voucherNo=h['voucherNo'], voucherTypeId=h['voucherTypeId'], fixedAssetId=asset_id,
            deprLedgerId=category['deprLedgerId'], accDeprLedgerId=category['accDeprLedgerId'],
            periodFrom=start, periodTo=end, totalAmount=Decimal(line['amount']).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP),
            deprAmount=ZERO, balanceAmount=ZERO, createdDate=datetime.now()))


def remove_asset_schedules(db, doc):
    h = doc['header']
    schedule, depreciation, disposal = r.T['tbl_FixedAssetDeprSchedule'], r.T['tbl_FixedAssetDepreciationHeader'], r.T['tbl_FixedAssetDisposalDetails']
    condition = and_(schedule.c.voucherTypeId == h['voucherTypeId'], schedule.c.voucherNo == h['voucherNo'])
    rows = db.execute(r.lock_query(db, select(schedule).where(condition), schedule)).mappings().all()
    for row in rows:
        used = db.execute(r.lock_query(db, select(depreciation.c.depreciationHeader).where(depreciation.c.depreciationSchedule == row['depreciationSchedule']), depreciation)).first()
        disposed = db.execute(select(disposal.c.DisposalId).where(disposal.c.FixedAssetId == row['fixedAssetId']).limit(1)).first()
        if used or disposed or row['deprAmount'] or row['balanceAmount']:
            raise HTTPException(409, 'Asset has depreciation or disposal activity; acquisition cannot be reversed')
    db.execute(schedule.delete().where(condition))


def change_posting(db, kind, identity, posted, version):
    try:
        cfg = lock_family(db, kind)
        doc = get_document(db, kind, identity, True)
        h = doc['header']
        if kind not in ('purchase-invoices', 'credit-notes', 'vehicle-finance'):
            raise HTTPException(422, 'This transaction has no separate posting action')
        if doc['version'] != version:
            raise HTTPException(409, 'Transaction changed. Refresh before posting')
        if bool(h['isPosted']) == posted:
            return doc
        if kind == 'credit-notes':
            raise HTTPException(422, 'Credit-note posting and reversal await verification of legacy accounting rules')
        year = common.get_financial_year(db, h[cfg.date_key])
        if year is None:
            raise HTTPException(422, 'Transaction date is outside configured financial years')
        if kind == 'vehicle-finance':
            # FinanceHeaderPost only finalizes the schedule. It does not create PDCs.
            if not posted:
                raise HTTPException(409, 'Finalized finance schedules cannot be reopened')
            if not doc['lines'] or money(sum(line['EMIamount'] for line in doc['lines'])) != money(h['loanAmount']):
                raise HTTPException(409, 'Installments do not equal the loan amount')
        elif not posted:
            if payments.has_external_party_reference(db, h['voucherTypeId'], h['voucherNo']) or payments.has_bank_reconciliation(db, h['voucherTypeId'], h['voucherNo']):
                raise HTTPException(409, 'Unposting is blocked by settlement or reconciliation')
            if kind == 'purchase-invoices':
                finance = r.T['tbl_FinanceHeader']
                if db.execute(select(finance.c.financeHeaderId).where(finance.c.purchaseMasterId == identity).limit(1)).first():
                    raise HTTPException(409, 'Purchase is linked to vehicle finance')
                if h['isInvPurchase']:
                    raise HTTPException(409, 'Inventory reversal requires legacy stock-effect verification')
                if h['isFaPurchase']:
                    remove_asset_schedules(db, doc)
            payments.delete_postings(db, h['voucherTypeId'], h['voucherNo'])
            payments.delete_active_allocations(db, h['voucherTypeId'], h['voucherNo'])
        else:
            if h['isInvPurchase']:
                raise HTTPException(422, 'Inventory posting requires verification of stock effects; the invoice is saved as a draft')
            exchange = common.get_exchange_rate(db, h['exchangeRateId'], h['date'])
            if not exchange or exchange['rate'] != 1:
                raise HTTPException(422, 'Posting currently supports verified base-currency purchases only')
            if payments.posting_totals(db, h['voucherTypeId'], h['voucherNo'])['rowCount']:
                raise HTTPException(409, 'Draft already has accounting entries; review legacy state')
            tax_total = money(sum(line['taxAmount'] or 0 for line in doc['lines']))
            gross_total = money(sum(line['grossAmount'] or 0 for line in doc['lines']))
            discount = money(h['billDiscount'])
            if money(gross_total + tax_total - discount) != money(h['grandTotal']):
                raise HTTPException(409, 'Saved purchase totals are inconsistent')
            post_row(db, h, h['ledgerId'], ZERO, h['grandTotal'])
            post_row(db, h, h['purchaseAccount'], gross_total, ZERO)
            if discount:
                discount_ledger = require(db, 'tbl_AccountLedger', 'ledgerId', 9, 'Verified discount ledger')
                if discount_ledger['ledgerName'] != 'Discount Received':
                    raise HTTPException(422, 'Discount account differs from verified legacy configuration')
                post_row(db, h, 9, ZERO, discount)
            if tax_total:
                tax_ledger = require(db, 'tbl_AccountLedger', 'ledgerId', 41, 'Verified VAT ledger')
                if tax_ledger['ledgerName'] != 'VAT @ 5%' or any(line['taxId'] != 2 for line in doc['lines'] if line['taxAmount']):
                    raise HTTPException(422, 'Tax posting configuration differs from verified legacy VAT')
                post_row(db, h, 41, tax_total, ZERO)
            party = require(db, 'tbl_AccountLedger', 'ledgerId', h['ledgerId'], 'Supplier')
            if party['billByBill']:
                party_row(db, h, h['ledgerId'], ZERO, h['grandTotal'], h['exchangeRateId'], new=True)
            if h['isFaPurchase']:
                create_asset_schedules(db, doc)
            check_posting_balance(db, h)
        db.execute(r.T[cfg.master].update().where(r.T[cfg.master].c[cfg.key] == identity).values(isPosted=posted))
        result = get_document(db, kind, identity)
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise
