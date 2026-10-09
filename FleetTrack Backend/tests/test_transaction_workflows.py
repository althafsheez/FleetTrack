"""Transactional regression tests in isolated SQLite; never writes to MSSQL."""
import unittest
from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Numeric, select, func
from sqlalchemy.dialects.mssql import MONEY
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.commercial_transactions import service as s, repository as r
from app.commercial_transactions import sales_register
from app.commercial_transactions import exports
from io import BytesIO
from xml.etree import ElementTree
from pypdf import PdfReader
from app.commercial_transactions.schemas import DocumentInput
from app.transaction_operations import service as ops
from app.transaction_operations.schemas import FineInput, ReconciliationInput

DATE = datetime(2026, 10, 9)


class TransactionTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://')
        connection = self.engine.raw_connection()
        connection.create_collation('SQL_Latin1_General_CP1_CI_AS', lambda a, b: (a.lower() > b.lower()) - (a.lower() < b.lower()))
        connection.close()
        metadata = MetaData()
        tables = {cfg.master for cfg in r.DOCUMENTS.values()} | {cfg.detail for cfg in r.DOCUMENTS.values()} | {cfg.tax for cfg in r.DOCUMENTS.values() if cfg.tax}
        tables.update(['tbl_AccountLedger', 'tbl_AccountGroup', 'tbl_FinancialYear', 'tbl_VoucherType', 'tbl_SuffixPrefix', 'tbl_ExchangeRate',
            'tbl_Currency', 'tbl_Unit', 'tbl_Tax', 'tbl_Employee', 'tbl_PricingLevel', 'tbl_Product', 'tbl_FixedAssetMaster', 'tbl_SalesDetailItemType',
            'tbl_SalesMaster', 'tbl_SalesDetails', 'tbl_PartyBalance', 'tbl_PartyBalance_Unposted', 'tbl_LedgerPosting', 'tbl_BankReconciliation',
            'VT_Veh_VehicleMaster', 'VT_Veh_TCNoMaster', 'Traffic_Fine', 'tbl_DeliveryNoteDetails', 'Salik_Toll',
            'tbl_FixedAssetCategory', 'tbl_FixedAssetDeprSchedule', 'tbl_FixedAssetDepreciationHeader', 'tbl_FixedAssetDisposalDetails'])
        for name in tables:
            cols = []
            for col in r.T[name].columns:
                numeric_pk = col.primary_key and name not in ('Traffic_Fine', 'Salik_Toll')
                column_type = Integer() if numeric_pk else Numeric(19, 4) if isinstance(col.type, MONEY) else col.type.copy()
                cols.append(Column(col.name, column_type, primary_key=col.primary_key, nullable=not col.primary_key))
            Table(name, metadata, *cols)
        metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.add('tbl_AccountGroup', accountGroupId=28, accountGroupName='Bank Account')
        self.add('tbl_AccountGroup', accountGroupId=22, accountGroupName='Sundry Creditors')
        self.add('tbl_AccountGroup', accountGroupId=26, accountGroupName='Sundry Debtors')
        self.add('tbl_AccountGroup', accountGroupId=54, accountGroupName='Financing Party')
        for identity, name, group in [(1, 'Test supplier', 22), (2, 'Test customer', 26), (3, 'Test expense', 99), (4, 'Test bank', 28), (5, 'Test financier', 54), (41, 'VAT @ 5%', 99)]:
            self.add('tbl_AccountLedger', ledgerId=identity, ledgerName=name, accountGroupId=group, openingBalance=0, crOrDr='Dr', billByBill=group in (22, 26))
        self.add('tbl_FinancialYear', financialYearId=1, fromDate=datetime(2026, 1, 1), toDate=datetime(2026, 12, 31, 23, 59, 59))
        self.add('tbl_Currency', currencyId=1, currencyName='Dirham', currencySymbol='AED', noOfDecimalPlaces=2)
        self.add('tbl_ExchangeRate', exchangeRateId=1, currencyId=1, rate=1, date=datetime(2026, 1, 1))
        self.add('tbl_Unit', unitId=1, unitName='No')
        self.add('tbl_Tax', taxId=1, taxName='NA', rate=0, isActive=True)
        self.add('tbl_Tax', taxId=2, taxName='VAT @ 5%', rate=5, isActive=True)
        self.add('tbl_AccountLedger', ledgerId=9, ledgerName='Discount Received', accountGroupId=14)
        self.add('VT_Veh_VehicleMaster', VehicleId=1, PlateNo='TEST')
        self.add('VT_Veh_TCNoMaster', TCNoId=1, TCNo='TEST-FILE')
        self.add('tbl_SalesDetailItemType', ItemType=1, ItemTypeName='Test item', IsActive=True, VoucherType=39, TaxId=2)
        for identity, name in [(10, 'Purchase Order'), (13, 'Purchase Invoice'), (15, 'Sales Quotation'), (23, 'Debit Note'), (39, 'Credit Note (Invoice)')]:
            self.add('tbl_VoucherType', voucherTypeId=identity, voucherTypeName=name, isActive=True, methodOfVoucherNumbering='Automatic')
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def add(self, table, **values):
        self.db.execute(r.T[table].insert().values(**values))

    def count(self, table):
        return self.db.execute(select(func.count()).select_from(r.T[table])).scalar_one()

    def payload(self, **changes):
        values = dict(date=DATE, ledgerId=1, exchangeRateId=1, accountId=3, dueDate=DATE, idempotencyKey=str(uuid4()),
            lines=[dict(description='Test service', unitId=1, qty='2', rate='50', taxId=2)])
        values.update(changes)
        return DocumentInput.model_validate(values)

    def save(self, kind='purchase-orders', payload=None):
        return s.save_document(self.db, kind, payload or self.payload(), 1)

    def assert_http(self, code, action):
        with self.assertRaises(HTTPException) as error:
            action()
        self.assertEqual(error.exception.status_code, code, error.exception.detail)

    def test_order_create_retry_and_edit_preserves_line_identity(self):
        payload = self.payload()
        doc = self.save(payload=payload)
        self.assertEqual(self.save(payload=payload)['id'], doc['id'])
        line_id = doc['lines'][0]['id']
        updated = self.payload(expectedVersion=doc['version'], lines=[dict(id=line_id, description='Edited service', unitId=1, qty=3, rate=50)])
        result = s.save_document(self.db, 'purchase-orders', updated, 1, doc['id'])
        self.assertEqual(result['lines'][0]['id'], line_id)
        self.assertEqual(result['header']['totalAmount'], Decimal('150'))
        self.assert_http(409, lambda: s.save_document(self.db, 'purchase-orders', updated, 1, doc['id']))
        self.assertEqual(self.count('tbl_LedgerPosting'), 0)

    def test_save_key_cannot_be_reused_with_changed_contents(self):
        payload = self.payload()
        self.save(payload=payload)
        self.assert_http(409, lambda: self.save(payload=payload.model_copy(update={'narration': 'different'})))

    def test_bad_unit_rolls_back_entire_order(self):
        self.assert_http(422, lambda: self.save(payload=self.payload(lines=[dict(description='Bad', unitId=999, qty=1, rate=50)])))
        self.assertEqual(self.count('tbl_PurchaseOrderMaster'), 0)

    def test_quotation_approval_and_delete_have_no_accounting_effect(self):
        doc = self.save('sales-quotations', self.payload(ledgerId=2, approved=True))
        self.assertTrue(doc['header']['approved'])
        s.delete_document(self.db, 'sales-quotations', doc['id'], doc['version'])
        self.assertEqual(self.count('tbl_SalesQuotationMaster'), 0)
        self.assertEqual(self.count('tbl_LedgerPosting'), 0)

    def test_source_quantity_and_invoiced_order_protection(self):
        order = self.save()
        line = dict(description='Service', sourceLineId=order['lines'][0]['id'], unitId=1, qty=2, rate=50, taxId=2)
        self.save('purchase-invoices', self.payload(sourceId=order['id'], lines=[line]))
        self.assert_http(409, lambda: self.save('purchase-invoices', self.payload(sourceId=order['id'], lines=[line])))
        self.assertEqual(self.count('tbl_PurchaseMaster'), 1)
        self.assert_http(409, lambda: s.delete_document(self.db, 'purchase-orders', order['id'], order['version']))

    def test_purchase_post_balances_vat_and_supplier_and_unposts(self):
        doc = self.save('purchase-invoices')
        self.assertEqual(self.count('tbl_LedgerPosting'), 0)
        posted = s.change_posting(self.db, 'purchase-invoices', doc['id'], True, doc['version'])
        self.assertTrue(posted['header']['isPosted'])
        self.assertEqual(self.count('tbl_LedgerPosting'), 3)
        self.assertEqual(self.count('tbl_PartyBalance'), 1)
        s.check_posting_balance(self.db, posted['header'])
        s.change_posting(self.db, 'purchase-invoices', doc['id'], False, posted['version'])
        self.assertEqual(self.count('tbl_LedgerPosting'), 0)
        self.assertEqual(self.count('tbl_PartyBalance'), 0)

    def test_settled_purchase_cannot_be_unposted(self):
        doc = self.save('purchase-invoices')
        posted = s.change_posting(self.db, 'purchase-invoices', doc['id'], True, doc['version'])
        self.add('tbl_PartyBalance', ledgerId=1, voucherTypeId=13, voucherNo=posted['header']['voucherNo'], referenceType='Against', againstVoucherTypeId=35, againstVoucherNo='1', debit=10, credit=0)
        self.db.commit()
        self.assert_http(409, lambda: s.change_posting(self.db, 'purchase-invoices', doc['id'], False, posted['version']))
        self.assertEqual(self.count('tbl_LedgerPosting'), 3)

    def test_discounted_purchase_posts_verified_discount_account(self):
        doc = self.save('purchase-invoices', self.payload(discount=5))
        posted = s.change_posting(self.db, 'purchase-invoices', doc['id'], True, doc['version'])
        self.assertEqual(posted['header']['grandTotal'], 100)
        ledger = r.T['tbl_LedgerPosting']
        credit = self.db.execute(select(ledger.c.credit).where(ledger.c.ledgerId == 9)).scalar_one()
        self.assertEqual(credit, 5)
        s.check_posting_balance(self.db, posted['header'])

    def asset_purchase(self):
        self.add('tbl_FixedAssetCategory', faCategoryId=1, assetLedgerId=3, deprLedgerId=3, accDeprLedgerId=4)
        self.add('tbl_FixedAssetMaster', fixedAssetId=100, fixedAssetCategory=1, fixedAssetDeprMethod=1, fixedAssetDeprPeriod=48, isActive=True)
        self.db.commit()
        return self.save('purchase-invoices', self.payload(purchaseMode='asset', lines=[dict(description='Test asset', productId=100, unitId=1, qty=1, rate=100, taxId=2)]))

    def test_asset_post_creates_schedule_and_unpost_removes_unused_schedule(self):
        doc = self.asset_purchase()
        posted = s.change_posting(self.db, 'purchase-invoices', doc['id'], True, doc['version'])
        table = r.T['tbl_FixedAssetDeprSchedule']
        row = self.db.execute(select(table)).mappings().one()
        self.assertEqual(row['totalAmount'], 105)
        self.assertEqual(row['periodTo'], datetime(2030, 10, 9))
        s.change_posting(self.db, 'purchase-invoices', doc['id'], False, posted['version'])
        self.assertEqual(self.count('tbl_FixedAssetDeprSchedule'), 0)
        self.assertEqual(self.count('tbl_LedgerPosting'), 0)

    def test_asset_depreciation_blocks_unpost(self):
        doc = self.asset_purchase()
        posted = s.change_posting(self.db, 'purchase-invoices', doc['id'], True, doc['version'])
        schedule = self.db.execute(select(r.T['tbl_FixedAssetDeprSchedule'].c.depreciationSchedule)).scalar_one()
        self.add('tbl_FixedAssetDepreciationHeader', depreciationSchedule=schedule, date=DATE, totalAmount=5)
        self.db.commit()
        self.assert_http(409, lambda: s.change_posting(self.db, 'purchase-invoices', doc['id'], False, posted['version']))
        self.assertEqual(self.count('tbl_FixedAssetDeprSchedule'), 1)
        self.assertEqual(self.count('tbl_LedgerPosting'), 3)

    def test_finance_save_and_finalize_from_asset_purchase(self):
        doc = self.asset_purchase()
        posted = s.change_posting(self.db, 'purchase-invoices', doc['id'], True, doc['version'])
        finance = self.save('vehicle-finance', self.payload(manualNumber='TEST-FINANCE', ledgerId=5,
            sourceId=doc['id'], purchaseDetailId=doc['lines'][0]['id'], assetId=100,
            loanAmount=100, monthlyAmount=50, installments=2, bankId=4, chequeNoFrom='001', chequeDateFrom=DATE, lines=[]))
        self.assertEqual(len(finance['lines']), 2)
        result = s.change_posting(self.db, 'vehicle-finance', finance['id'], True, finance['version'])
        self.assertTrue(result['header']['isPosted'])
        self.assert_http(409, lambda: s.change_posting(self.db, 'purchase-invoices', doc['id'], False, posted['version']))

    def test_credit_note_uses_sales_return_and_decimal_total(self):
        doc = self.save('credit-notes', self.payload(ledgerId=2, lines=[dict(description='Adjustment', itemTypeId=1, unitId=1, qty=1, rate='10.25', taxId=2)]))
        self.assertEqual(doc['header']['voucherTypeId'], 39)
        self.assertEqual(doc['header']['grandTotal'], Decimal('10.76250'))
        self.assertEqual(self.count('tbl_SalesReturnMaster'), 1)

    def test_debit_note_rejects_unbalanced_and_posts_balanced_lines(self):
        lines = [dict(ledgerId=1, direction='Dr', amount=50, exchangeRateId=1), dict(ledgerId=3, direction='Cr', amount=49, exchangeRateId=1)]
        self.assert_http(422, lambda: self.save('debit-notes', self.payload(lines=lines)))
        self.assertEqual(self.count('tbl_DebitNoteMaster'), 0)
        lines[1]['amount'] = 50
        doc = self.save('debit-notes', self.payload(lines=lines))
        self.assertEqual(self.count('tbl_LedgerPosting'), 2)
        s.check_posting_balance(self.db, doc['header'])
        s.delete_document(self.db, 'debit-notes', doc['id'], doc['version'])
        self.assertEqual(self.count('tbl_LedgerPosting'), 0)

    def test_debit_against_allocation_cannot_overdraw(self):
        self.add('tbl_PartyBalance', ledgerId=1, voucherTypeId=13, voucherNo='100', invoiceNo='100', debit=0, credit=40, exchangeRateId=1)
        self.db.commit()
        lines = [dict(ledgerId=1, direction='Dr', amount=50, exchangeRateId=1, allocations=[dict(voucherTypeId=13, voucherNo='100', amount=50)]), dict(ledgerId=3, direction='Cr', amount=50, exchangeRateId=1)]
        self.assert_http(409, lambda: self.save('debit-notes', self.payload(lines=lines)))
        self.assertEqual(self.count('tbl_DebitNoteMaster'), 0)
        self.assertEqual(self.count('tbl_LedgerPosting'), 0)

    def test_debit_allocation_survives_read_and_reordered_update(self):
        self.add('tbl_PartyBalance', ledgerId=1, voucherTypeId=13, voucherNo='100', invoiceNo='100', debit=0, credit=40, exchangeRateId=1)
        self.db.commit()
        lines = [dict(ledgerId=1, direction='Dr', amount=20, exchangeRateId=1, allocations=[dict(voucherTypeId=13, voucherNo='100', amount=20)]),
                 dict(ledgerId=3, direction='Cr', amount=20, exchangeRateId=1)]
        doc = self.save('debit-notes', self.payload(lines=lines))
        self.assertEqual(doc['allocations'][0]['amount'], 20)
        for line in lines:
            line['id'] = next(row['id'] for row in doc['lines'] if row['ledgerId'] == line['ledgerId'])
        saved = s.save_document(self.db, 'debit-notes', self.payload(lines=lines[::-1], expectedVersion=doc['version']), 1, doc['id'])
        self.assertEqual(saved['allocations'][0]['amount'], 20)
        self.assertEqual(saved['allocations'][0]['ledgerId'], 1)

    def test_sales_register_filters_and_salik_link(self):
        self.add('tbl_SalesMaster', salesMasterId=1, invoiceNo='TEST-1', date=DATE, ledgerId=2, voucherTypeId=31, grandTotal=100, isPosted=True, extra1='TEST')
        self.add('tbl_SalesMaster', salesMasterId=2, invoiceNo='TEST-2', date=DATE, ledgerId=2, voucherTypeId=31, grandTotal=50, isPosted=False)
        self.add('tbl_SalesDetails', salesDetailsId=1, salesMasterId=1, itemTypeId=7, rate=2)
        self.add('Salik_Toll', TRANSID=1, INVOICENO='TEST-1', DATEANDTIME=DATE, AMOUNT=4)
        self.db.commit()
        result = sales_register.register(self.db, DATE.date(), DATE.date(), location='TEST', posted=True)
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['items'][0]['id'], 1)
        self.assertEqual(sales_register.salik(self.db, 1)[0]['amount'], 6)
        self.add('tbl_SalesMaster', salesMasterId=3, invoiceNo='TEST-1', date=DATE)
        self.db.commit()
        self.assert_http(409, lambda: sales_register.salik(self.db, 1))

    def test_exports_preserve_literal_cells_and_render_pdf(self):
        rows = [dict(invoiceNo='=1+1', date=DATE, customer='Test & Company', grandTotal=Decimal('100.25'), taxAmount=Decimal('5'), narration='Test <invoice>')]
        xml = exports.excel(rows)
        root = ElementTree.fromstring(xml)
        ns = '{urn:schemas-microsoft-com:office:spreadsheet}'
        cells = root.findall('.//' + ns + 'Data')
        self.assertEqual(cells[7].text, '=1+1')
        self.assertEqual(cells[7].get(ns + 'Type'), 'String')
        self.assertNotIn(ns + 'Formula', xml.decode())
        document = PdfReader(BytesIO(exports.pdf(rows * 60)))
        self.assertGreater(len(document.pages), 1)
        self.assertIn('Test & Company', document.pages[0].extract_text())
        self.assertIn('100.25', document.pages[0].extract_text())

    def test_finance_month_end_and_final_remainder(self):
        payload = self.payload(loanAmount=1000, monthlyAmount=350, installments=3, bankId=4, chequeNoFrom='0099', chequeDateFrom=datetime(2026, 1, 31), lines=[])
        rows = s.finance_schedule(payload)
        self.assertEqual([row['EMIDate'].day for row in rows], [31, 28, 31])
        self.assertEqual([row['chequeNo'] for row in rows], ['0099', '0100', '0101'])
        self.assertEqual(rows[-1]['EMIamount'], Decimal(300))

    def test_reconciliation_create_stale_wrong_bank_and_reopen(self):
        self.add('tbl_LedgerPosting', ledgerPostingId=1, ledgerId=4, date=DATE, debit=100, credit=0)
        self.db.commit()
        payload = ReconciliationInput(bankLedgerId=4, lines=[dict(ledgerPostingId=1, statementDate=DATE)])
        ops.save_reconciliation(self.db, payload)
        self.assertEqual(self.count('tbl_BankReconciliation'), 1)
        self.assert_http(409, lambda: ops.save_reconciliation(self.db, payload))
        self.assert_http(422, lambda: ops.save_reconciliation(self.db, ReconciliationInput(bankLedgerId=3, lines=[dict(ledgerPostingId=1, statementDate=DATE)])))
        ops.save_reconciliation(self.db, ReconciliationInput(bankLedgerId=4, lines=[dict(ledgerPostingId=1, expectedStatementDate=DATE, statementDate=None)]))
        self.assertEqual(self.count('tbl_BankReconciliation'), 0)
        self.assertEqual(self.count('tbl_LedgerPosting'), 1)

    def test_fine_uses_ticket_identity_and_rejects_duplicate(self):
        payload = FineInput(ticketNo='TEST-1', vehicleId=1, trafficFile='TEST-FILE', fineDate=DATE, authority='Test authority', amount=100, description='Test fine')
        result = ops.save_fine(self.db, payload)
        self.assertEqual(result['ticketNo'], 'TEST-1')
        self.assertFalse(result['isPosted'])
        self.assert_http(409, lambda: ops.save_fine(self.db, payload))
        self.assertEqual(self.count('Traffic_Fine'), 1)

    def test_invalid_date_range(self):
        self.assert_http(422, lambda: ops.period(date(2026, 2, 2), date(2026, 2, 1)))


if __name__ == '__main__':
    unittest.main()
