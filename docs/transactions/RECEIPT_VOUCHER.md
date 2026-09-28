# Receipt Voucher dossier

## Purpose, scope, and evidence

Receipt Voucher records incoming money into a cash, bank, or approved receipt account and credits one or more customer or other detail ledgers. For bill-by-bill customer ledgers, the receipt can settle open invoices or retain an unapplied credit.

Legacy shortcut: **Receipt Voucher - F6**.

Status: **BACKEND IMPLEMENTED / LIVE WRITES UNVERIFIED**. The Receipt frontend remains missing.

Implementation update (2026-09-28): `app/receipt_vouchers` now implements the approved FastAPI schemas, repository, service, router, register, lookups, draft lifecycle, posting lifecycle, and print projection with direct SQLAlchemy operations. Twenty-one focused tests and the 53-test Contra/Payment/Receipt suite pass. Read-only MSSQL verified the 3,721-row register, Receipt subtypes, and AED rate; no live Receipt write was performed, and final live detail re-verification was blocked by a subsequent local MSSQL login timeout.

Evidence inspected read-only on 2026-09-28:

- Legacy Receipt Voucher, Party Balance, and Receipt Register screenshots supplied by the user.
- Live MSSQL table metadata, keys, indexes, triggers, procedure parameters, dependencies, and definitions.
- Sanitized aggregate and transaction-shape queries. No customer names or credentials were copied into this dossier.
- Existing Payment Voucher architecture, which is structurally similar but has the opposite accounting orientation.

No schema, stored procedure, generated model, or live data was changed. The stored procedures are behavioral references; the proposed implementation will use FastAPI service/repository code and direct SQLAlchemy operations inside explicit transactions.

## Legacy UI workflow

### Receipt entry screen
f
The supplied screen confirms these controls:

- Voucher number, generated from the selected Receipt Voucher subtype and numbering rule.
- Bank / Cash receiving account.
- Voucher date.
- Detail grid with Account Ledger, `Against`, Amount, Currency, Cheque No., and Cheque Date.
- Add/remove detail rows.
- Narration and server-calculated total.
- `Print after save` option.
- Save, Clear, Delete, Close, Print, and Post actions.

The voucher subtype is selected before or while opening the entry screen. Current live types are:

| ID | Name | Numbering evidence |
|---|---|---|
| 5 | Receipt Voucher | Automatic; no date-valid suffix/prefix row found. |
| 41 | Cash Receipt Voucher | Automatic; prefix `CR`, four digits, zero-filled. |
| 42 | Cheque Receipt Voucher | Automatic; prefix `CHR`, four digits, zero-filled. |
| 43 | Credit Card Receipt | Automatic; no date-valid suffix/prefix row found. |

The API must not hard-code these IDs. It must select active rows whose `typeOfVoucher` is `Receipt Voucher` and use the date-valid numbering configuration. A subtype with no valid numbering rule must be blocked with a clear configuration error rather than inventing a number.

### Party Balance popup

Clicking `Against` for a bill-by-bill party line opens an allocation grid with:

- Reference type.
- Source voucher type.
- Source voucher/invoice number.
- Current pending amount.
- Allocation amount.
- Currency.
- Debit/credit marker.
- Contract number.
- Remove, Save, and Close actions.

Confirmed live Receipt allocations settle Rental Invoice, Salik Invoice, and Fine Invoice references. Multiple invoices can be allocated to one receipt detail line, and one receipt can contain multiple detail ledgers.

`Against` and `OnAccount` are proven by live Receipt rows. The generic Party Balance procedures support `New`, but no active Receipt `New` rows were found and the screenshot does not prove that option. `New` remains **UNKNOWN** and should not be exposed in the first implementation without further legacy evidence.

### Receipt Register

The supplied register confirms:

- From Date and To Date.
- Cash/Bank account.
- Voucher number.
- Exact amount.
- Party/detail ledger.
- Optional cheque-number search.
- All, Posted, and Non-posted status.
- Result columns for serial number, voucher number, voucher type, date, amount, narration, and cash/bank account.
- View Details action.

The new register should also provide pagination, create, edit/view, print, post/unpost, and delete actions according to lifecycle state. All filters should compose in one query; the legacy implementation splits cheque search into a separate procedure and therefore does not reliably combine every filter.

## Confirmed lifecycle

```text
create draft
  -> choose Receipt Voucher subtype
  -> choose receiving cash/bank account
  -> add one or more credited detail ledgers
  -> for eligible party lines: allocate Against open invoices or On Account
  -> save master + details + unposted allocation mirror

draft
  -> view / edit / delete / print draft
  -> post

post
  -> debit receiving account
  -> credit each detail ledger
  -> activate Party Balance credits
  -> mark master posted last

posted
  -> view / print
  -> unpost only when no later dependency or bank reconciliation blocks reversal

unpost
  -> delete active ledger postings and active allocations
  -> retain/rebuild unposted allocations
  -> mark master draft
```

`ReceiptMasterPost` only changes `isPosted` to `1`; it does not create accounting rows. Therefore posting is not a single legacy procedure call. FastAPI must coordinate all posting writes atomically.

Live data proves that posted receipts retain matching rows in `tbl_PartyBalance_Unposted` as a draft mirror. The unpost procedure removes active `tbl_PartyBalance` and `tbl_LedgerPosting` rows but leaves the unposted rows available for editing and reposting.

## Data model and relationships

### `tbl_ReceiptMaster`

- `receiptMasterId`: primary API identity.
- `voucherNo`: internal numeric sequence stored as text.
- `invoiceNo`: displayed formatted receipt number, such as the configured prefix plus padded sequence.
- `suffixPrefixId`: numbering-rule identity.
- `date`: voucher date.
- `ledgerId`: receiving cash/bank ledger.
- `totalAmount`: base-currency total calculated by the server.
- `narration`, `voucherTypeId`, `userId`, `financialYearId`.
- `isPosted`: draft/post lifecycle state.
- `extra1`: candidate idempotency-key storage, following Payment Voucher; this is an application convention, not a database constraint.

### `tbl_ReceiptDetails`

- `receiptDetailsId`: line identity and the `detailsId` used by its ledger posting.
- `receiptMasterId`: behavioral parent relation.
- `ledgerId`: customer, party, or other credited ledger.
- `amount`: entered amount in the selected line currency.
- `exchangeRateId`: currency/rate row.
- `chequeNo`, `chequeDate`: instrument metadata.

There is no detail-to-allocation ID in Party Balance. Allocations are associated by receipt type/number and party ledger. Repeating the same detail ledger in two lines would make allocation ownership ambiguous, so the API should allow each detail ledger only once per receipt.

### `tbl_PartyBalance_Unposted`

Stores draft allocation rows. It is the editable source for an unposted Receipt and is retained as a mirror for posted legacy records.

### `tbl_PartyBalance`

Stores active bill-by-bill effects:

what i v int the - `Against`: the original invoice remains in `voucherTypeId`, `voucherNo`, and `invoiceNo`; the Receipt is placed in `againstVoucherTypeId`, `againstVoucherNo`, and `againstInvoiceNo`.
- `OnAccount`: the Receipt itself is the voucher identity, the against fields are zero, and the credit remains available on the party account.
- Receipt allocation value is stored in `credit`; `debit` is zero.
- `contractId` preserves source rental context where available.

For Receipt open-reference selection, `PartyBalanceComboViewByLedgerId` uses the non-`Dr` path and returns references whose `SUM(debit) - SUM(credit)` is positive.

### `tbl_LedgerPosting`

- One header debit posting uses the receiving ledger and `detailsId = 0`.
- One credit posting is created for every receipt detail and uses its `receiptDetailsId`.
- Voucher association uses `voucherTypeId`, `voucherNo`, `invoiceNo`, and `yearId`.
- Cheque metadata is copied to the relevant posting rows.

```text
tbl_ReceiptMaster (1)
    +----< tbl_ReceiptDetails (many)
    |          +---- tbl_LedgerPosting detail credit
    |          +----< Party Balance allocation credits by party ledger
    |
    +---- tbl_LedgerPosting receiving-account debit (detailsId = 0)

original invoice Party Balance reference
    +----< Receipt Against row
           original invoice in voucherTypeId/voucherNo
           receipt in againstVoucherTypeId/againstVoucherNo
```

### Supporting tables

| Role | Table |
|---|---|
| Accounts and eligibility | `tbl_AccountLedger`, `tbl_AccountGroup` |
| Currency and rate | `tbl_ExchangeRate`, `tbl_Currency` |
| Voucher subtype | `tbl_VoucherType` |
| Numbering | `tbl_SuffixPrefix` |
| Period | `tbl_FinancialYear` |
| Accounting | `tbl_LedgerPosting` |
| Draft/active allocations | `tbl_PartyBalance_Unposted`, `tbl_PartyBalance` |
| Bank control | `tbl_BankReconciliation` |
| Rental print context | `tbl_SalesMaster` |

No foreign keys, secondary indexes, or triggers exist on the two Receipt tables in the inspected database. Relationships are confirmed from stored-procedure joins and live row behavior, not from enforced constraints.

## Verified live behavior

- 3,721 Receipt masters exist: 3,720 posted and one unposted.
- 3,716 have one detail line, four have two lines, and one has four lines.
- No inspected Receipt repeats the same detail ledger, and no detail ledger equals its receiving header ledger.
- Every existing Receipt and detail amount is positive.
- Every header total equals the sum of detail amount multiplied by its exchange rate.
- Every Receipt detail currently uses AED/Dirham at rate `1.00000`; foreign-currency behavior is not demonstrated.
- A sanitized posted sample confirmed a receiving-account debit and matching detail-account credit.
- Sanitized allocation samples confirmed partial and multi-invoice settlement across Rental, Salik, and Fine invoices.
- `Against` and `OnAccount` Receipt rows are present. No Receipt `New` row was found.
- No current Receipt posting is bank reconciled, but the delete procedure contains reconciliation cleanup, proving the dependency exists.
- 88 Receipt-origin Party Balance references have later allocation relationships, so dependency checks before unpost/delete are required.

Cheque evidence is inconsistent: cash receipts contain a non-null timestamp in `chequeDate` but blank cheque numbers, while five of seven Cheque Receipt rows contain a cheque number. The legacy database does not prove strict instrument validation. The proposed API should require cheque number and date for Cheque Receipt Voucher, omit them for Cash Receipt Voucher, and treat Credit Card fields as a separate product decision.

## Stored-procedure findings

The procedures below were inspected only as behavioral references.

### Master and detail

- `ReceiptMasterAdd`: inserts the complete header and returns the identity.
- `ReceiptMasterEdit`: updates the complete header, including `isPosted`.
- `ReceiptMasterViewByMasterId`: returns header detail and state.
- `ReceiptMasterIdView`: resolves master ID from type and voucher number.
- `RecieptMasterMax`: finds the maximum numeric internal voucher number by subtype.
- `ReceiptVoucherCheckExistence`: checks duplicate voucher number within a subtype.
- `ReceiptDetailsAdd`, `ReceiptDetailsEdit`, `ReceiptDetailsDelete`, `ReceiptDetailsDeleteByMasterId`: maintain lines.
- `ReceiptDetailsViewByMasterId`: returns all lines for a header.

### Posting, unposting, and deletion

- `ReceiptMasterPost`: only changes `isPosted` from `0` to `1`.
- `ReceiptMasterUnPost`: marks the master unposted and deletes active Receipt ledger postings plus active Party Balance rows on both sides of the Receipt reference.
- `ReceiptVoucherDelete`: deletes active allocations, unposted allocations, linked bank-reconciliation rows, ledger postings, details, and master.
- `PartyBalanceCheckReference`: detects whether a Receipt-origin balance has become referenced by a later allocation.
- `LedgerPostingAdd`: inserts individual accounting rows; it is not a full posting workflow.

The new service must not copy the legacy delete procedure's silent deletion of bank-reconciliation rows. A reconciled Receipt should return a conflict until an explicitly approved reconciliation reversal workflow exists.

### Allocation

- `AccountGroupIdCheck`: enables bill allocation only for `billByBill = 1` ledgers in Sundry Creditors or Sundry Debtors, including descendant groups.
- `PartyBalanceComboViewByLedgerId`: returns open debit references for Receipt allocation.
- `PartyBalancePendingAmount`: recalculates current pending value and includes the voucher's own existing allocation while editing.
- `PartyBalanceAdd` / `PartyBalanceEdit` / delete procedures maintain active allocations.
- Corresponding `_Unposted` procedures maintain the editable draft mirror.
- `PartyBalanceViewByVoucherNoAndVoucherType` and its `_Unposted` version reconstruct allocation grids for detail/edit screens.

### Register and print

- `ReceiptMasterSearch`: filters by inclusive date range, receiving ledger, displayed voucher number, party/detail ledger, status, and exact amount.
- `ReceiptDetailsSearchByChequeNo`: provides cheque search but does not compose every register filter.
- `ReceiptReportSearch`: filters report rows by dates, detail ledger, subtype, and receiving account.
- `ReceiptVoucherPrinting`: returns contract/vehicle context, receipt header, and detail lines with currency and cheque data.
- `ReceiptReportPrinting` and `ReceiptReportSummaryPrinting`: provide detailed and subtype-summary report projections.
- `ReceiptViewFromBillAllocation`: returns Receipt master/detail information when navigating from bill allocation.
- `CashOrBankComboFill`: selects ledgers under Bank OD A/C, Cash-in Hand, and Bank Account, including descendant groups.

## Proposed FastAPI contract

Use the same architecture and naming style as Payment Voucher:

`router -> schema -> service -> repository -> SQLAlchemy/generated model -> MSSQL`

Primary prefix: `/receipt-vouchers`. This is consistent with `/payment-vouchers` and `/contra-vouchers`. Add a `/receipts` compatibility alias only if an existing client contract requires it.

### Routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/receipt-vouchers/page` | Paginated register with composable filters. |
| `GET` | `/receipt-vouchers/{receiptMasterId}` | Header, lines, allocations, totals, and lifecycle state. |
| `POST` | `/receipt-vouchers` | Create an unposted draft. |
| `PATCH` | `/receipt-vouchers/{receiptMasterId}` | Update an unposted draft. |
| `DELETE` | `/receipt-vouchers/{receiptMasterId}` | Delete an eligible unposted draft. |
| `POST` | `/receipt-vouchers/{receiptMasterId}/post` | Atomically create active accounting/allocation effects. |
| `POST` | `/receipt-vouchers/{receiptMasterId}/unpost` | Atomically remove active effects and restore draft state. |
| `GET` | `/receipt-vouchers/{receiptMasterId}/print-data` | Stable print projection. |
| `GET` | `/receipt-vouchers/lookups/voucher-types` | Active Receipt Voucher subtypes. |
| `GET` | `/receipt-vouchers/lookups/receiving-accounts` | Eligible cash/bank/Bank OD accounts. |
| `GET` | `/receipt-vouchers/lookups/detail-accounts` | Searchable ledgers with bill-by-bill capability flag. |
| `GET` | `/receipt-vouchers/lookups/party-ledgers` | Searchable eligible party ledgers for register filtering. |
| `GET` | `/receipt-vouchers/lookups/exchange-rates?date=...` | Date-valid currencies and rates. |
| `GET` | `/receipt-vouchers/lookups/numbering-rule?voucherTypeId=...&date=...` | Numbering preview; not a reserved number. |
| `GET` | `/receipt-vouchers/party-ledgers/{ledgerId}/open-references` | Open debit references and current pending values. |

Register query parameters:

`fromDate`, `toDate`, `voucherNo`, `voucherTypeId`, `receivingLedgerId`, `amount`, `partyLedgerId`, `chequeNo`, `posted`, `offset`, and `limit`.

The API uses an exclusive next-day boundary internally for `toDate` so all times on the selected final date are included.

### Proposed write payload

```json
{
  "voucherTypeId": 41,
  "voucherDate": "2026-09-28T00:00:00",
  "receivingLedgerId": 138278,
  "manualVoucherNo": null,
  "narration": "Customer receipt",
  "idempotencyKey": "receipt-voucher-unique-key",
  "lines": [
    {
      "receiptDetailsId": null,
      "ledgerId": 208848,
      "amount": "70.00000",
      "exchangeRateId": 1,
      "chequeNo": null,
      "chequeDate": null,
      "allocations": [
        {
          "partyBalanceId": null,
          "referenceType": "against",
          "sourceVoucherTypeId": 31,
          "sourceVoucherNo": "005055",
          "amount": "30.43000"
        },
        {
          "partyBalanceId": null,
          "referenceType": "on_account",
          "sourceVoucherTypeId": null,
          "sourceVoucherNo": null,
          "amount": "39.57000"
        }
      ]
    }
  ]
}
```

The client does not submit trusted totals, exchange rates, invoice display values, contract IDs, posting rows, posted state, user ID, or financial-year ID. The server reloads those values from authoritative tables.

## Service and repository design

### Create draft

1. Authenticate the user and begin one transaction.
2. Resolve the date's financial year and reject an unconfigured/closed date.
3. Validate that the subtype is active, is a Receipt Voucher, and has a date-valid numbering rule.
4. Validate the receiving ledger against the cash/bank/Bank OD group tree.
5. Validate at least one complete, positive detail line; reject the receiving ledger as a detail ledger.
6. Require unique detail ledger IDs to keep allocations unambiguous.
7. Validate date-valid positive exchange rates. Foreign currency remains disabled until a controlled test proves rounding and gain/loss behavior.
8. For bill-by-bill party lines, require allocations. For ordinary ledgers, reject allocations.
9. For every `Against` row, lock/re-read the source reference and calculate `debit - credit` pending balance.
10. Reject duplicate source references and allocation above pending balance.
11. Require party-line allocation total to equal the line amount. Any unapplied remainder must be an explicit `OnAccount` row.
12. Lock the numbering scope, allocate the final internal/display number, and recheck duplicates.
13. Insert master as unposted, insert details, and insert `tbl_PartyBalance_Unposted` rows.
14. Verify the server-calculated base total, commit, and return a refreshed response.

### Update draft

1. Lock the master and require `isPosted = 0`.
2. Do not allow voucher subtype, final number, or idempotency identity to change.
3. Re-run every create validation and pending-balance check.
4. Reconcile detail rows by `receiptDetailsId`: update retained rows, insert new rows, and delete omitted rows.
5. Reconcile unposted allocation rows by `partyBalanceId` and reject IDs owned by another voucher.
6. Commit the complete master/detail/allocation change or roll everything back.

Detail identities should be preserved when a line remains. A changed line must not be implemented as delete-and-reinsert, because unnecessary identity changes complicate audit history and later posting links.

### Post

1. Lock and reload the draft.
2. If already posted and all expected effects exist, return the current result idempotently. If state is partial, return a conflict for investigation.
3. Revalidate period, account eligibility, rates, allocations, and current pending balances under locks.
4. Ensure no active ledger or Party Balance effects already exist for this Receipt.
5. Insert the receiving-account debit with `detailsId = 0`.
6. Insert one detail-account credit per line using its `receiptDetailsId`.
7. Copy validated draft allocations into active `tbl_PartyBalance` as credits, retaining the unposted mirror.
8. Verify total debit equals total credit and each party line equals its allocations.
9. Mark `isPosted = 1` last and commit atomically.

### Unpost

1. Lock and require a currently posted Receipt.
2. Reject if the Receipt's On Account/New balance has been consumed by a later voucher.
3. Reject if any related ledger posting is bank reconciled.
4. Verify the unposted allocation mirror exists; rebuild it from active rows if needed before reversal.
5. Delete active Receipt ledger postings and active Party Balance rows.
6. Mark `isPosted = 0` and commit atomically.

### Delete

1. Lock and require an unposted Receipt.
2. Reject external Party Balance references or reconciliation dependencies.
3. Delete unposted allocations, detail rows, and master in one transaction.
4. Never silently delete bank-reconciliation records.

### Detail, register, and print

- Detail chooses active allocations when posted and the unposted mirror when draft.
- Register uses one composable, paginated query and `EXISTS` subqueries for party and cheque filters to avoid duplicate masters.
- Print data is a stable response model with company, header, receiving account, detail lines, allocations, contract references, totals, and status. It does not expose generated models.

## Validation and edge cases

### Required validation

- Invalid/inactive Receipt subtype.
- Missing numbering rule or duplicate final number.
- Date outside an allowed financial year or closed period.
- Invalid receiving ledger or detail ledger equal to receiving ledger.
- Empty lines, zero/negative amounts, duplicate detail ledger, or repeated detail ID.
- Missing/stale exchange rate.
- Partial cheque fields or instrument rules inconsistent with subtype.
- Allocation on a non-party ledger or missing allocation on a bill-by-bill party ledger.
- Duplicate `Against` source within a Receipt.
- Source belonging to another party, closed source, stale pending value, or over-allocation.
- Party line total not equal to allocation total.
- Omitted unapplied remainder instead of explicit `OnAccount`.
- Client-supplied child ID owned by another Receipt.
- Edit/delete of posted Receipt.
- Duplicate post/unpost request.
- Unpost/delete after a later voucher consumes the receipt credit.
- Unpost/delete after bank reconciliation.
- Concurrent receipts attempting to settle the same final pending amount.
- Failure after any master, detail, allocation, or posting write must roll back all writes.

### Explicit unknowns and decisions required

- Foreign-currency receipt gain/loss direction and rounding are **UNKNOWN** because all live Receipt details use AED at rate 1. Foreign currency should remain blocked initially.
- `New` Receipt allocation behavior is **UNKNOWN**; implement `Against` and `OnAccount` first.
- Credit Card Receipt has no active date-valid suffix/prefix row in the inspected data. It cannot be enabled safely until configuration is corrected outside this implementation.
- Whether Cheque Receipt must always require a cheque number is not enforced by legacy data. Recommended new rule: require cheque number/date for Cheque Receipt, prohibit cheque fields for Cash Receipt, and define card-reference handling separately.
- The exact authorization roles for post, unpost, and delete are **UNKNOWN** and must follow the application's eventual permission model.
- Whether a reconciled receipt may be reversed through a dedicated bank-reconciliation workflow is **UNKNOWN**; initial behavior should block it.

## Automated and controlled tests

### Unit/service tests

- Automatic numbering and missing-rule failure.
- Receiving/detail account eligibility.
- Empty, duplicate, zero, and negative lines.
- Against, partial Against, multi-invoice Against, and On Account.
- Rental, Salik, and Fine source references.
- Over-allocation, stale balance, duplicate source, wrong party, and closed source.
- Cheque subtype rules and incomplete cheque fields.
- Draft create/update with preserved detail IDs and deleted omitted rows.
- Header/detail/allocation total reconciliation.
- Register filter composition and pagination.
- Posted edit/delete rejection.
- Idempotent create and post.
- Unpost dependency and reconciliation conflicts.

### Integration tests against controlled MSSQL data

- Draft creates master, details, and only unposted allocations.
- Post creates one header debit, detail credits, active allocation credits, and balanced totals.
- Post failure at each persistence stage rolls back everything.
- Two concurrent receipts cannot both consume the same pending balance.
- Unpost removes every active effect while preserving/restoring draft allocations.
- Delete removes the draft graph but no unrelated rows.
- Register returns correct inclusive-date, account, voucher, amount, party, cheque, and status results.
- Print projection includes the correct contract/invoice context without exposing private fields.

Controlled write tests require separate approval. Until then, only unit tests with rollback/fakes and read-only live verification are allowed.

## UI implementation sequence after API approval

1. Build Receipt Register using the same shell, spacing, blue action palette, table, filters, pagination, and modal pattern as Contra and Payment.
2. Add `New Receipt Voucher`; choose subtype inside the modal, then load the matching number preview and receiving-account options.
3. Use the searchable ledger combobox pattern already corrected on Payment Voucher; results must open outside the horizontally scrolling line grid.
4. Add removable lines and block adding another line until the current line is complete.
5. For eligible party ledgers, show an `Allocate` action that opens a nested allocation modal with open references, pending amount, entered amount, and explicit `On Account` remainder.
6. Keep Save Draft, Save & Print, Post, Unpost, Print, Edit, and Delete visible only when the current lifecycle state permits them.
7. Preserve structured backend conflicts, especially stale/over-allocation source lists, and display them in the allocation modal instead of reducing them to generic text.
8. Verify desktop/mobile overflow, keyboard navigation, focus return, loading, empty, error, and confirmation states.

## Delivery phases and estimate

1. **Approval checkpoint:** confirm route prefix, cheque policy, disabled foreign currency, and `Against` plus `OnAccount` scope.
2. **Backend:** schemas, repository, service, router, register, posting lifecycle, and print projection.
3. **Tests:** unit/service suite, compile/import checks, then controlled MSSQL writes only after approval.
4. **UI design prompt:** derive the exact Receipt Register, entry modal, and allocation modal from the approved API and current FleetTrack visual system.
5. **Frontend:** implement and integrate the register and workflow.
6. **Acceptance:** backend tests, frontend typecheck/build, responsive verification, controlled live workflow, and documentation update.

Estimate: **5-8 working days** for backend, tests, register, frontend, and controlled verification after the four approval decisions are made. The main remaining risks are foreign-currency behavior, instrument validation policy, and reversal after reconciliation.
