# Sales Invoice functional and API analysis

Status: design specification with read-only live MSSQL evidence. This document records screenshot evidence, generated-model evidence, live database findings, proposed API behavior, and unresolved rules separately. It does not authorize database/schema changes or claim that new posting behavior has been runtime verified.

## Scope and confirmed behavior

The legacy Sales Invoice entry point offers five invoice types:

- Rental Invoice
- Salik Invoice
- Fine Invoice
- Misc Invoice
- Vehicle Invoice

The supplied screenshots cover Rental, Misc, Fine, Salik, and Vehicle invoices. Populated examples were supplied for all except Vehicle Invoice; live MSSQL records establish its purpose and storage behavior.

The user confirmed:

- A saved invoice remains a draft until the user posts it.
- VAT must be selected and calculated from `tbl_Tax`; it must not be hard-coded as 5%.
- The legacy screens are functional references. FleetTrack may use a different UI while preserving verified behavior.

Screenshot evidence also shows:

- Rental Invoice displays a `Post` action while still a draft.
- Posted Fine and Salik invoices display an `UnPost` action.
- A draft Misc invoice has Update/Delete disabled in the captured state; the exact reason is unknown.
- Invoice lines can have different tax selections within the same invoice.
- Fine and Salik service-charge lines can be taxed while the underlying fine/toll line is not taxed.
- Invoice totals shown are tax-inclusive line totals: `line amount = base amount + line tax` in the supplied examples.
- The lower debit/credit grid can be empty while the invoice exists. Live Vehicle Invoice rows show that it can allocate existing customer credits/advances through `tbl_PartyBalance`; whether every invoice type must expose this during the MVP remains a product decision.

Read-only live verification on 2026-09-18 confirmed:

- Voucher type 38 is active `Vehicle Invoice`, with `typeOfVoucher = Sales Invoice`.
- Six posted Vehicle Invoice headers exist.
- Vehicle Invoice represents vehicle sales, using active item type 16 `Veh Sale`.
- Existing examples use quantity 1 and unit 2 `NOS`.
- Existing examples have no contract (`contractId = 0`, `contractRefNo = NA`).
- Some detail rows link a real vehicle ID; others store vehicle ID 0 and identify the sold vehicle only in description text. New FleetTrack records should require a real vehicle when the vehicle exists in the fleet database.
- Existing examples use tax row 1 `NA` at 0%, even though the item-type default points to tax row 2 `VAT @ 5%`. Therefore item-type tax is a default, not proof of the final selected tax.
- Existing Vehicle Invoice ledger postings debit the customer and credit ledger 10 `Sales Account` for the invoice total.
- Older Vehicle Invoices create a `tbl_PartyBalance` `New` debit and one or more `Against` credits whose amounts fully allocate existing customer credits/advances. This explains the lower Dr/Cr allocation grid.
- No relevant table triggers or generated foreign keys exist on the sales, tax, posting, or party-balance tables.
- The database contains legacy stored procedures for create/edit/detail, post/unpost, delete, party balance, printing, register, and invoice reporting.

## Evidence classification

- **CONFIRMED**: directly supplied by the user or represented by an explicit generated database constraint.
- **SCREEN EVIDENCE**: visible in supplied screenshots, but not yet traced through live database records.
- **MAPPED CANDIDATE**: matching generated columns/tables exist, but no FK or live trace proves the behavior.
- **UNKNOWN**: requires a live database trace, legacy behavior demonstration, or user decision.

## Functional lifecycle

### Draft

A draft stores the invoice header, details, tax rows, and any draft-only associations. Live procedure evidence confirms `SalesMasterAdd` accepts `isPosted` and generates both voucher and invoice numbers internally. Proposed database state:

- `tbl_SalesMaster.isPosted = 0`
- `tbl_SalesMaster` and `tbl_SalesDetails` exist
- `tbl_SalesBillTax` contains recomputed tax totals when used by the legacy system
- no posted `tbl_LedgerPosting` or final `tbl_PartyBalance` entries are created
- source Fine/Salik rows are not finally marked posted

The exact use of `tbl_PartyBalance_Unposted` for drafts remains UNKNOWN and must be checked against a live draft.

### Posted

Posting is a separate command. Legacy `SalesInvoicePost` only changes `tbl_SalesMaster.isPosted` from 0 to 1 for the supplied master/type/voucher identity. That means the desktop application likely prepares ledger, party-balance, tax, and source effects separately before calling the final post procedure. FleetTrack must coordinate the complete operation atomically and idempotently rather than copying that fragmented client workflow.

Proposed behavior:

1. Lock/reload the draft invoice.
2. Reject an already-posted invoice.
3. Revalidate customer, contract, vehicle, source records, tax rows, totals, and financial period.
4. Recompute every amount on the server.
5. Generate final accounting references if they are not assigned at draft creation.
6. Insert balanced `tbl_LedgerPosting` rows.
7. Insert/update the customer receivable in `tbl_PartyBalance`.
8. Mark Fine/Salik source rows as posted and attach the invoice reference where applicable.
9. Update applicable contract invoicing flags and dates.
10. Set `tbl_SalesMaster.isPosted = 1`.
11. Commit all changes together; roll back all changes on failure.

### Unposted

The Fine and Salik screenshots prove that an `UnPost` command exists. Live procedure evidence confirms that legacy `SalesInvoiceUnPost`:

- sets `tbl_SalesMaster.isPosted = 0`
- deletes matching `tbl_LedgerPosting` rows
- deletes matching `referenceType = New` rows from both `tbl_PartyBalance` and `tbl_PartyBalance_Unposted`

It does not visibly reverse source Fine/Salik rows or remove `Against` party-balance rows in the procedure body. Those effects may be handled elsewhere by the desktop client. FleetTrack must not reproduce an incomplete reversal.

FleetTrack must not implement unposting until one existing posted invoice is traced. A posted invoice with an allocated receipt should normally be blocked from unposting unless the legacy system explicitly supports a safe cascade/reversal.

### Delete

Physical delete should initially be limited to unposted drafts with no dependent allocation. Live `SalesInvoiceDelete` procedure evidence shows that legacy delete copies header/details to `tbl_SalesMaster_Deleted` and `tbl_SalesDetails_Deleted`, removes New and Against party-balance references, ledger postings, additional costs, bill tax, details, and finally the master. FleetTrack should preserve this archive behavior if the procedure is verified for all invoice types. Posted invoice deletion should not be exposed.

## Screen-to-database field mapping

### Header

| Functional field | Primary mapping | Lookup/source | Status and notes |
| --- | --- | --- | --- |
| Invoice No. | `tbl_SalesMaster.invoiceNo` | numbering functions/configuration | Prefixes differ by type (`RI`, `FN`, `SA`, `MS`); Vehicle Invoice currently uses plain sequential numbers. `SalesMasterAdd` calls database numbering functions and ignores caller-proposed numbers. |
| Invoice type / Voucher Type | `tbl_SalesMaster.voucherTypeId` | `tbl_VoucherType` | MAPPED CANDIDATE. The dropdown labels match invoice types, but IDs are not verified. |
| Voucher No. | `tbl_SalesMaster.voucherNo` | numbering configuration | Hidden on screen; likely used by postings and source rows. |
| Suffix/prefix | `tbl_SalesMaster.suffixPrefixId` | `tbl_SuffixPrefix` | MAPPED CANDIDATE for type/date-specific numbering. |
| Date | `tbl_SalesMaster.date` | user input/current business date | Required by API. Financial-year validation required. |
| Customer selector | `tbl_SalesMaster.ledgerId` | `tbl_AccountLedger`, customer group 26 | Existing customer lookup can be reused, with invoice-specific credit fields added. |
| Customer display snapshot | `tbl_SalesMaster.customerName` | selected customer/contract | Screenshot shows a second read-only customer field. Do not trust client-supplied text. |
| Credit period | `tbl_SalesMaster.creditPeriod` | `tbl_AccountLedger.creditPeriod` | Generated model marks it NOT NULL. Default from customer, allow authorized override if confirmed. |
| Due date | derived | `date + creditPeriod` | Not stored directly on sales master. |
| LPO No. | `tbl_SalesMaster.lpoNo` | user input/contract | Optional in screenshots. |
| Sales A/C | `tbl_SalesMaster.salesAccount` | revenue ledgers in `tbl_AccountLedger` | Defaults differ by type: Rental Revenue, Traffic Fine Revenue, Salik Revenue, Damage Revenue in screenshots. Filtering rules need live verification. |
| Sales Man | `tbl_SalesMaster.employeeId` | `tbl_Employee` | Existing `/lookups/sales-persons` is a candidate. `NA` is visible and must map to null or a verified sentinel. |
| Contract | `tbl_SalesMaster.contractId` | `VT_ContractMaster.ContractId` | No generated FK. Filter by selected customer. Screenshot displays contract reference numbers; API should use internal ContractId and return ContractRefNo. |
| Contract reference snapshot | `tbl_SalesMaster.contractRefNo` | `VT_ContractMaster.ContractRefNo` | Backend-populated. |
| Currency | `tbl_SalesMaster.exchangeRateId` | currency/exchange-rate tables | Screen displays Dirham/AED. Exact lookup and default exchange-rate row are UNKNOWN. |
| Location | `tbl_SalesMaster.extra1` in legacy create path | `VT_Veh_LocationMaster` or contract location | `SalesMasterAdd` derives the contract location when contractId > 0; otherwise it stores the supplied location name in `extra1`, defaulting to AL KARAMA. FleetTrack should resolve a location ID server-side and persist the verified legacy label required by this schema. |
| User | `tbl_SalesMaster.userId` | authenticated user mapping | Current auth uses `VT_ApplicationUsers`; legacy accounting uses numeric user references. Mapping needs verification. |
| Financial year | `tbl_SalesMaster.financialYearId` | `tbl_FinancialYear` | Backend-derived from invoice date/current company context. |
| Counter/POS | `counterId`, `POS` | `tbl_Counter` | Likely not required for rental-office invoice workflow; preserve null/default behavior after live trace. |
| Narration | `tbl_SalesMaster.narration` | generated/default plus user edit | Visible on every supplied screen. |
| Posted state | `tbl_SalesMaster.isPosted` | lifecycle | CONFIRMED draft/post distinction. |
| Vehicle summary | `tbl_SalesMaster.vehicleNos` | selected detail vehicles | Snapshot only; relational source remains detail `vehicleId`. |
| Fine reference | `tbl_SalesMaster.trafficFineNo` | `Traffic_Fine.TICKETNO` | Insufficient for multiple fine rows; source linkage strategy needs live trace. |

### Invoice details

| Screen column | Primary mapping | Lookup/source | Rules |
| --- | --- | --- | --- |
| Sl No | `tbl_SalesDetails.slNo` | server sequence | Positive, unique within invoice. |
| Type | `itemTypeId` | `tbl_SalesDetailItemType` | Filter active values by selected voucher type where `VoucherType` is used. |
| Vehicle Details | `vehicleId` | `VT_Veh_VehicleMaster` through contract assignment | UI displays vehicle/plate label; API stores ID. |
| Description | `description` | generated from source or manual for Misc | Preserve useful source reference without using description as relational identity. |
| Qty | `qty` | source/calculation | Greater than zero. Fine/Misc often 1; Salik screenshot aggregates four transactions. |
| Unit | `unitId` | `tbl_Unit` | Screenshot uses NOS. Exact unit ID must come from lookup. |
| Rate | `rate` | contract/source/manual | Non-negative. Rental must use stored contract rate, not the current tariff master. |
| Tax | `taxId` | `tbl_Tax` | Nullable/NA allowed. Use only active/applicable tax rows. |
| Tax Amount | `taxAmount` | server calculation | Never accept client total as authoritative. |
| Amount | `amount` | server calculation | Screenshot evidence indicates tax-inclusive line amount. |
| Discount | `discount` | manual/rules | Hidden in visible grid but mapped. Invoice-type permission needs confirmation. |
| Gross amount | `grossAmount` | server calculation | Exact legacy formula needs live trace. |
| Net amount | `netAmount` | server calculation | Exact legacy formula needs live trace. |

### Totals and tax summary

| Screen field | Mapping | Rule |
| --- | --- | --- |
| Tax summary rows | `tbl_SalesBillTax` | Aggregate line tax by `taxId` for `salesMasterId`. |
| Tax total | `tbl_SalesMaster.taxAmount` | Sum of server-calculated line tax amounts. |
| Total Amount | `tbl_SalesMaster.totalAmount` | Screenshot appears to show tax-inclusive total. Confirm against live row. |
| Bill Discount | `tbl_SalesMaster.billDiscount` | Invoice-level discount. Permission by type is UNKNOWN. |
| Grand Total | `tbl_SalesMaster.grandTotal` | Screenshot suggests `totalAmount - billDiscount`; confirm additional-cost ordering. |
| Additional cost | `tbl_SalesMaster.additionalCost` | Mapped but not visible in screenshots. Do not expose until required. |

Provisional calculation using screenshot evidence:

```text
line_base       = quantity * rate
line_tax        = tax calculation from tbl_Tax
line_amount     = line_base - line_discount + line_tax
tax_total       = sum(line_tax)
total_amount    = sum(line_amount)
grand_total     = total_amount + additional_cost - bill_discount
```

Rounding precision and `tbl_Tax.calculatingMode` semantics remain UNKNOWN. Use Decimal throughout and do not use binary floating point.

## VAT and tax lookup

`tbl_Tax` contains:

- `taxId`
- `taxName`
- `applicableOn`
- `rate`
- `calculatingMode`
- `isActive`
- narration and extra fields

`tbl_TaxDetails` can associate a selected tax with component taxes. Therefore, the API must not assume that every tax is a single percentage row. The first implementation should load active sales-applicable taxes and calculate according to verified `calculatingMode`. Until that mode is traced, only the behavior represented by existing rows can be supported safely.

`tbl_SalesDetailItemType.TaxId` is a candidate default tax for an item type. The backend may propose that tax, but the selected line tax and server validation remain authoritative.

Required lookup endpoints:

```text
GET /sales-invoices/lookups/types
GET /sales-invoices/lookups/item-types?invoiceType=...
GET /sales-invoices/lookups/taxes
GET /sales-invoices/lookups/units
GET /sales-invoices/lookups/sales-accounts?invoiceType=...
GET /sales-invoices/lookups/currencies
GET /sales-invoices/lookups/locations
GET /sales-invoices/lookups/salespersons
```

These may internally reuse existing lookup repositories, but invoice-specific filtering and stable response schemas should be added instead of exposing whole ORM rows.

## Invoice-type behavior

### Rental Invoice

Screen evidence:

- Invoice prefix `RI`.
- Sales account defaults to Rental Revenue.
- Item type is Rental Rate.
- Contract and vehicle are required in the populated example.
- Description includes billing period/contract information.
- Quantity can be 1 while rate represents the period charge.
- VAT is applied to rental value in the example.

Candidate sources:

- `VT_ContractMaster`: customer, contract dates, rate, charges, discount, invoice flags, next invoice date, billing type.
- `VT_ContractVehicleMaster`: assigned vehicle and checkout/check-in interval.
- `VT_Veh_VehicleMaster`: vehicle display details.
- stored contract rate/charges, not current tariff values.

Posting candidates:

- update `RentalInvoiced`
- update `LastInvoiceDate`
- update `NextInvStDate` for recurring billing

Do not set `RentalInvoiced = 1` merely because one periodic invoice exists unless the contract is fully billed. Multiple rental invoices per contract appear plausible and require confirmation.

### Misc Invoice

Screen evidence:

- Invoice prefix `MS`.
- Sales account can be Damage Revenue.
- Item type is MISC.
- Contract and vehicle can be selected.
- Description and amount are manually meaningful.
- VAT may apply.

Misc lines are manual, but customer, contract, vehicle, account, item type, tax, and totals must still be validated by the backend. If Misc is used for contract repair/penalty/other charges, posting may update `RepairCharged`, `PenaltyCharged`, or `OtherChargesCharged`; this cannot be inferred from free text and needs an explicit charge category.

### Fine Invoice

Screen evidence:

- Invoice prefix `FN`.
- Sales account defaults to Traffic Fine Revenue.
- The fine principal line is untaxed in the supplied example.
- A separate fine service-charge line is taxed.
- Posted screen exposes UnPost.

Source table: `Traffic_Fine`.

Candidate source fields include ticket number, vehicle ID, fine date/time, authority, amount, acknowledgment, description, paid state, posted state, voucher number, and invoice remarks.

Proposed source identity must include `TICKETNO` for each source-backed line. `tbl_SalesMaster.trafficFineNo` is insufficient for a multi-fine invoice. No dedicated sales-detail source-reference column exists, so a verified bridge or legacy convention is required before supporting multiple source records safely.

`Traffic_Fine.PAID` must not be treated as equivalent to customer-invoiced. Government/vendor payment and customer billing are different states.

### Salik Invoice

Screen evidence:

- Invoice prefix `SA`.
- Sales account defaults to Salik Revenue.
- Toll transactions may be aggregated: quantity 4 at the per-toll rate.
- Toll principal is untaxed in the supplied example.
- A separate service-charge line is taxed.
- Posted screen exposes UnPost.

Source table: `Salik_Toll`.

Candidate posting updates:

- `ISPOSTED = 1`
- `INVOICENO = generated invoice number`
- `INVOICEGENDATE = posting date/time`

Salik association to a contract likely uses tag/plate plus transaction time within a vehicle assignment interval. There is no generated contract/vehicle FK on `Salik_Toll`; allocation must be verified and cannot rely on plate text alone when plate history can change.

### Vehicle Invoice

Vehicle Invoice is a vehicle-sale invoice, not vehicle loan finance.

Confirmed live configuration and behavior:

- voucher type: 38, `Vehicle Invoice`
- item type: 16, `Veh Sale`
- unit: 2, `NOS`
- typical quantity: 1
- contract: not applicable (`0` / `NA`) in all six existing headers
- invoice and voucher numbers: plain sequential values in existing records
- default sales account in existing records: ledger 10, `Sales Account`
- posting: customer ledger debit and Sales Account credit for the invoice total
- tax: existing invoices selected `NA`/0%; the item-type default is VAT 5%, so selection must be explicit and server-validated
- one invoice can contain multiple sold-vehicle lines
- a vehicle link is supported through `tbl_SalesDetails.vehicleId`, but legacy data also contains zero/unlinked rows

Proposed FleetTrack rules:

1. Require customer, sales account, invoice date, currency, location, and at least one vehicle-sale line.
2. Require a real `vehicleId` for a fleet vehicle. Permit an unregistered/manual vehicle only through an explicit, confirmed workflow rather than silently writing zero.
3. Default item type to `Veh Sale`, quantity to 1, and unit to `NOS`.
4. Do not default VAT solely from historical invoices or item-type configuration; load active `tbl_Tax` choices and apply the selected rule.
5. Contract must be null/not applicable.
6. Posting creates customer debit, revenue credit, VAT credit when applicable, and party-balance rows.
7. Any vehicle status/ownership/disposal update is still UNKNOWN. Do not change `VT_Veh_VehicleMaster` until this side effect is verified.

## Vehicle Finance is a separate module

The generated schema contains `tbl_FinanceHeader` and `tbl_FinanceDetail`. These represent vehicle/asset loan finance and EMI/PDC scheduling, not customer Sales Invoice behavior.

`tbl_FinanceHeader` fields:

- `financeHeaderId`, `financeNo`, `docDate`
- `purchaseMasterId`, `purchaseDetailId`, `assetID`
- financier/account `ledgerId`
- `purchasedAmount`, `loanAmount`, `monthlyAmount`, `NoOfInstallments`
- `bankId`, starting cheque number/date
- created-by/date, narration, `isPosted`

`tbl_FinanceDetail` fields:

- `financeDetailId`, `financeHeaderId`
- EMI number, PDC ID, bank ID
- EMI amount, cheque number, EMI date
- paid state, created-by/date

No generated foreign keys prove the header/detail, purchase, asset, bank, or PDC joins. The expected header/detail join is `tbl_FinanceDetail.financeHeaderId = tbl_FinanceHeader.financeHeaderId`, but it remains a MAPPED CANDIDATE.

Vehicle Finance must remain outside the Sales Invoice API. The supplied screenshot and live records concern Vehicle Invoice, which is now confirmed as a vehicle-sale transaction.

## Accounting side effects

### Ledger posting

`tbl_LedgerPosting` is the candidate general-ledger table. Relevant fields are date, voucher type/no, ledger ID, debit, credit, details ID, financial year, invoice number, cheque fields, and extra fields.

Expected accounting shape for a posted credit invoice:

```text
Debit:  customer receivable ledger     grand total
Credit: sales/revenue ledger           taxable/exempt base
Credit: output VAT ledger              tax amount
```

This is standard accounting logic, not verified legacy behavior. Exact ledger IDs, `detailsId` semantics, line aggregation, rounding, and VAT posting must be traced before implementation.

### Party balance

`tbl_PartyBalance` is the candidate bill-by-bill receivable table. It includes ledger, voucher/invoice references, against-voucher references, debit/credit, credit period, exchange rate, financial year, and contract ID.

A posted invoice likely creates a debit/open-item row for the customer. Receipt allocation likely writes against-invoice references. The exact `referenceType` values and settlement rules are UNKNOWN.

### Staging invoices

`Staging_Invoice_Header` and `Staging_Invoice_Detail` exist and have the only explicit invoice header/detail FK in the generated mappings. Their columns support location, invoice type, transaction/contract/customer, invoice number, date-range remarks, vehicle, LPO, salesperson, cost, and tax.

It is UNKNOWN whether these tables are a required precursor for Rental/Vehicle invoice generation, an import queue, or a separate integration. Do not write them until an existing invoice is traced.

## Final proposed API

All routes require the existing signed-session authentication.

### Register and detail

```text
GET /sales-invoices
GET /sales-invoices/{salesMasterId}
GET /sales-invoices/{salesMasterId}/print
```

Register query parameters:

- `q`: invoice number, customer, contract reference, or vehicle
- `invoiceType`
- `posted`: true/false
- `paymentStatus`: unpaid/partial/paid, derived from verified party-balance allocations
- `dateFrom`, `dateTo`
- `offset`, `limit`

The register must initially return an empty `items` array naturally when no records match; it must not manufacture filler records.

### Source discovery

```text
GET /sales-invoices/eligible-contracts?customerId=...
GET /sales-invoices/sources/rental?contractId=...&throughDate=...
GET /sales-invoices/sources/fines?contractId=...
GET /sales-invoices/sources/salik?contractId=...&from=...&to=...
```

Source responses should include stable source IDs, display information, calculated suggestions, invoiced/posted state, and conflict/version information. They must not post or reserve records.

### Draft commands

```text
POST   /sales-invoices
PATCH  /sales-invoices/{salesMasterId}
DELETE /sales-invoices/{salesMasterId}
```

`POST` creates an unposted draft. `PATCH` and `DELETE` reject posted invoices.

Proposed draft request:

```json
{
  "invoiceType": "rental",
  "invoiceDate": "2026-09-18",
  "customerId": 123,
  "contractId": 456,
  "creditPeriod": 0,
  "lpoNo": null,
  "salesAccountId": 789,
  "salesPersonId": null,
  "currencyId": 1,
  "locationId": 1,
  "billDiscount": "0.00",
  "narration": "Billing period description",
  "lines": [
    {
      "itemTypeId": 1,
      "vehicleId": 10,
      "sourceType": "contract_charge",
      "sourceId": "456:rental:2026-09-18",
      "description": "Rental charge",
      "quantity": "1.00",
      "unitId": 1,
      "rate": "1905.00",
      "discount": "0.00",
      "taxId": 1
    }
  ]
}
```

`sourceType` and `sourceId` are API concepts needed for validation and duplicate prevention. No verified database destination exists for them yet. They must not be discarded until the source-link storage strategy is resolved.

### Lifecycle commands

```text
POST /sales-invoices/{salesMasterId}/post
POST /sales-invoices/{salesMasterId}/unpost
```

Use commands rather than allowing clients to PATCH `isPosted` directly. Both commands must be transactional. `post` should return the fully refreshed posted invoice. `unpost` should be unavailable until reversal behavior is verified.

Suggested errors:

- `404`: invoice/source/lookup not found
- `409`: already posted, already unposted, source already invoiced, dependent receipt exists, numbering conflict, or stale source state
- `422`: invalid line, tax, date, contract/customer mismatch, unbalanced totals, or unsupported type
- `403`: future role restriction when permissions are implemented

## Server-side validation

- Customer must exist and belong to the customer account group.
- Contract must belong to the selected customer.
- Detail vehicle must belong to the selected contract for source-backed invoice types.
- Voucher type, item type, sales account, tax, unit, currency, location, salesperson, user, and financial year must be valid and active/applicable where the schema supports that state.
- At least one valid line is required.
- Quantity must be greater than zero; monetary values must be non-negative unless a verified workflow allows otherwise.
- Backend recalculates tax and every total.
- Fine/Salik source rows must still be eligible at posting time.
- Duplicate source billing must be rejected.
- Draft updates use an optimistic version or updated timestamp strategy if concurrent users are expected.
- Posted invoices cannot be edited or deleted.
- All header, detail, tax, posting, party-balance, source, and contract changes occur in one transaction.

## Implementation structure

Use the existing architecture:

```text
app/sales_invoices/
  router.py
  schemas.py
  service.py
  repository.py
```

- Router: HTTP parsing, auth dependency, status codes.
- Schemas: strict request/response contracts using Decimal values.
- Service: invoice-type strategy, calculations, validation, lifecycle transaction coordination.
- Repository: database reads/writes only; no business-rule invention.

Avoid editing generated models. Use their `__table__` objects where relationships are not declared and write explicit joins.

## Required live verification before posting implementation

Before posting implementation, trace at least one draft and one posted example for each available type. Vehicle Invoice posted records have now been traced at header/detail/posting/party-balance level, but the remaining checks still apply:

1. `tbl_SalesMaster` and `tbl_SalesDetails`
2. `tbl_SalesBillTax`
3. `tbl_LedgerPosting`
4. `tbl_PartyBalance` and `tbl_PartyBalance_Unposted`
5. relevant `tbl_VoucherType`, `tbl_SuffixPrefix`, `tbl_SalesDetailItemType`, `tbl_Tax`, `tbl_Unit`, currency/exchange-rate rows
6. contract flags/dates
7. Fine/Salik source rows
8. triggers, stored procedures, and modules referencing these tables
9. deleted/archive tables after a controlled legacy draft deletion, if available
10. vehicle-master status/disposal effects after a Vehicle Invoice is posted or unposted

Do not include customer names, IDs, phone numbers, plate numbers, ticket numbers, or other customer data in documentation or logs. Record aggregate behavior and anonymized IDs only.

## Decisions still required from the user

1. Can a contract receive multiple periodic Rental Invoices? If yes, what defines each billing period?
2. May a draft invoice number be reused after deletion, or is numbering consumed immediately?
3. Can posted invoices with no receipt be unposted by any authenticated user, or only an authorized role?
4. Should Fine/Salik service-charge rate be fixed, configured, or manually editable?
5. Are invoice-level discounts allowed for Rental, Fine, Salik, and Misc?
6. Should the lower Dr/Cr allocation grid be included in the MVP, or should advance/credit allocation be deferred to Receipt Voucher?
7. Is `Staging_Invoice_*` mandatory for Rental invoice generation?
8. When a Vehicle Invoice is posted, should the sold vehicle's status or ownership record change? If yes, which status and fields?
9. Should Vehicle Invoice allow manual/unregistered vehicles, or only vehicles already present in FleetTrack?
10. Should Vehicle Invoice VAT default to NA/0% as historical records do, default to the item type's VAT 5%, or always require explicit selection?

## Recommended implementation boundary after confirmation

## Approved MVP decisions

The user approved the following Vehicle Invoice decisions on 2026-09-18:

- Vehicle Invoice supports only vehicles registered in FleetTrack; manual/unregistered vehicle lines are excluded.
- The user must explicitly select the VAT row; historical 0% examples and an item-type default must not silently choose the tax.
- Posting a Vehicle Invoice changes every sold vehicle to the verified `Sold` vehicle status.
- Unposting restores each sold vehicle's prior status. The API must retain a pre-post status snapshot before updating the vehicle.
- The lower Dr/Cr customer-credit allocation grid is deferred. Advance/credit allocation will be introduced with Receipt Voucher instead.

Phase 1 implements register/detail, invoice-specific lookups, validated draft create/update/delete, and Vehicle Invoice posting once the live Sold-status and VAT-output-ledger configuration are confirmed. Fine and Salik posting follows only after source-link and duplicate-prevention rules are proven. Vehicle Finance remains a separate future module.
