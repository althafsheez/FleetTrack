# Payment Voucher dossier

## Status and scope

Payment Voucher records money paid from a cash or bank account to suppliers, expenses, advances, or other ledgers. The legacy Transactions menu exposes **Payment Voucher - F5**.

Current FleetTrack status: **BACKEND AND FRONTEND IMPLEMENTED / READ PATHS LIVE VERIFIED / CONTROLLED WRITES UNVERIFIED**.

The FastAPI implementation uses direct SQLAlchemy table access. It does not call application stored procedures. The stored procedures remain behavioral evidence only. No generated model, database object, schema, lookup, or master-data row was changed.

### Evidence confidence

| Evidence | Confidence | Notes |
|---|---:|---|
| Supplied Payment Voucher screen | Confirmed | Shows voucher number, paying account, date, lines, Against action, currency, cheque, vehicle, total, narration, save, and print behavior. |
| Supplied Party Balance screen | Confirmed | Shows `Against`, an outstanding Rental Invoice, pending amount, allocation amount, currency, `Cr`, and contract number. |
| Generated SQLAlchemy mappings | Confirmed | Confirms Payment master/detail, Party Balance, and posting table shapes. |
| Live MSSQL metadata and aggregate/sample inspection | Confirmed | Procedure definitions, eligible account groups, posted/unposted storage, posting orientation, and an anonymized allocation example were inspected read-only. |
| Matching OpenMiracle source | Strong candidate | Form names, fields, procedure calls, and allocation behavior match the supplied UI and live schema. |

Candidate source inspected at revision `783497755f061913a8412b0e6f6810a86cb19ef1`: `Transactions/frmPaymentVoucher.cs`, `Transactions/frmPartyBalance.cs`, `Classes/SP/PaymentMasterSP.cs`, `Classes/SP/PaymentDetailsSP.cs`, `Classes/SP/PartyBalanceSP.cs`, and `Classes/SP/LedgerPostingSP.cs`.

Legacy UI evidence: [Payment Voucher](../../reference/screenshots/transactions/payment-voucher.png) and [Party Balance / Against](../../reference/screenshots/transactions/payment-voucher-party-balance.png).

## What the two screens mean

### Main Payment Voucher screen

- `Voucher No.` identifies the payment inside the selected Payment Voucher type.
- `Bank / Cash` is the account from which money leaves.
- `Date` controls the financial year, numbering rule, and exchange-rate choices.
- Each grid row identifies the account receiving the debit: supplier, expense, advance, or another valid ledger.
- `Against` opens bill allocation only when the selected detail account is a bill-by-bill Sundry Creditor or Sundry Debtor ledger.
- `Amount` is entered directly for an ordinary ledger. For a bill-by-bill party ledger it is calculated from the Party Balance allocations and is read-only on the main screen.
- `Currency` selects the exchange-rate record effective for the voucher date.
- `Cheque No.` and `Cheque Date` describe the detail payment instrument.
- `Vehicle` optionally attributes the line to a vehicle. Its reporting/business effect is still `UNKNOWN`.
- `Total` is the sum of line amounts converted to base currency.

### Party Balance / Against screen

`Against` does not mean another account and does not create a second payment. It tells the system which existing party invoice the payment settles.

The supplied example means:

```text
Selected party ledger has Rental Invoice RI003075
Outstanding balance = AED 1,073
User enters all or part of AED 1,073 in Amount
Contract No. 1776 is context carried by the source balance row
Cr identifies the outstanding invoice as a credit balance
The Payment Voucher creates a debit allocation to reduce that credit balance
```

The popup supports three reference types:

| Reference | Meaning in a Payment Voucher |
|---|---|
| `Against` | Apply this payment to one existing open invoice/reference. Amount cannot exceed its current pending balance. |
| `New` | Create a new debit reference owned by this Payment Voucher, normally an advance that may be settled later. |
| `OnAccount` | Record the amount on the party account without selecting a specific invoice. |

For Payment Voucher, allocation direction is always `Dr`. The popup may display an open supplier invoice as `Cr`; the new debit allocation reduces that credit balance.

## Verified end-to-end workflow

```text
choose Payment Voucher subtype
    -> choose voucher date and paying cash/bank account
    -> add one or more detail ledgers
       -> ordinary ledger: enter amount/currency directly
       -> bill-by-bill party: open Against and allocate references
    -> optional cheque and vehicle attribution
    -> server validates and calculates base total
    -> save draft
    -> post explicitly
    -> print/register
```

### Voucher subtype

The live database has these active automatic Payment Voucher types:

- `35` - Bank Payment Voucher
- `36` - Cash Payment Voucher
- `40` - Credit Card Payment Voucher

The voucher type controls numbering, document identity, register/print labeling, and posting association. The live legacy cash/bank lookup itself includes all descendants of these account groups:

- `17` - Bank OD A/C
- `27` - Cash-in Hand
- `28` - Bank Account

Historical read-only data proves that Bank Payment Voucher and Cash Payment Voucher records have both used Bank Account and Cash-in Hand source groups. The subtype therefore controls document identity and numbering, but the API does not impose an invented one-to-one subtype/account-group rule. The selector exposes all verified cash/bank/Bank OD accounts and displays each group. Credit-card source-account grouping still requires one controlled example.

### Draft state

Live evidence confirms a real draft lifecycle:

- `tbl_PaymentMaster.isPosted = 0`.
- `tbl_PaymentMaster` and `tbl_PaymentDetails` contain the saved document.
- No active `tbl_LedgerPosting` rows exist for the draft.
- Draft party allocations may be stored in `tbl_PartyBalance_Unposted`.

There were three unposted Payment masters during inspection. One Bank Payment draft had one detail row, no ledger postings, no active party rows, and four unposted `Against` rows. This establishes that save and post must be separate API commands.

### Posted state

Posting produces these accounting rows:

| Row | Debit | Credit |
|---|---:|---:|
| Selected Bank/Cash header ledger | 0 | Base-currency voucher total |
| Each ordinary detail ledger | Entered amount x verified exchange rate | 0 |
| Each party detail ledger | Sum of its allocations converted using the source/reference rate | 0 |
| Forex Gain/Loss ledger `12`, when required | Difference if positive | Difference if negative |

A sanitized live posted Bank Payment sample proved this shape:

- Header total: `487.50000`.
- Header bank posting: credit `487.50000` with `detailsId = 0`.
- One party detail posting: debit `487.50000` linked to its `paymentDetailsId`.
- Two `Against` Party Balance rows: debit `105.00000` and `382.50000`, both linked back to the Payment Voucher and together equal to the detail posting.

For an `Against` allocation, the active `tbl_PartyBalance` row retains the original invoice as its `voucherTypeId` / `voucherNo` and stores the Payment Voucher as `againstVoucherTypeId` / `againstVoucherNo`. This is how the pending invoice balance is reduced without editing the original invoice row.

### Update, unpost, and delete

- Draft update replaces/reconciles master, details, and draft allocations without creating active ledger postings.
- Posted vouchers must not be edited directly. The client must unpost first, then update the draft.
- `PaymentMasterUnPost` sets `isPosted = 0` and deletes active ledger and Party Balance effects. The procedure does not reconstruct draft allocation rows, so the API must preserve or rebuild the allocations before allowing repost.
- `PaymentVoucherDelete` removes Party Balance rows, unposted Party Balance rows, bank-reconciliation rows tied to the voucher postings, ledger postings, details, and the master.
- The legacy delete check rejects deletion when another Party Balance row references the Payment Voucher.
- Deleting or unposting a bank-reconciled payment needs an explicit policy. The delete procedure silently removes reconciliation rows, but that behavior is financially risky and should not be copied without approval.

## Data model and relationships

### `tbl_PaymentMaster`

- `paymentMasterId`: primary API identity.
- `voucherNo`, `invoiceNo`, `suffixPrefixId`: numbering identity.
- `date`: voucher date.
- `ledgerId`: paying cash/bank/credit-card ledger.
- `totalAmount`: server-calculated base-currency total.
- `narration`, `voucherTypeId`, `userId`, `financialYearId`.
- `isPosted`: draft/post state.

### `tbl_PaymentDetails`

- `paymentDetailsId`: line identity.
- `paymentMasterId`: behavioral parent relation.
- `ledgerId`: supplier, expense, advance, or other destination ledger.
- `amount`: entered/allocated amount in selected currency.
- `exchangeRateId`: selected currency/rate row.
- `chequeNo`, `chequeDate`.
- `Vehicle`: optional vehicle identity; exact validation and reports are `UNKNOWN`.

### `tbl_PartyBalance` and `tbl_PartyBalance_Unposted`

These tables hold bill-by-bill allocation rows, not general-ledger postings.

- Draft allocations use `tbl_PartyBalance_Unposted`.
- Posted allocations use `tbl_PartyBalance`.
- `ledgerId` must match the selected party detail ledger.
- `referenceType` is `Against`, `New`, or `OnAccount`.
- Payment allocations use `debit`; `credit` is zero.
- `exchangeRateId` and `contractId` preserve source context.

### `tbl_LedgerPosting`

- One header credit posting uses `detailsId = 0`.
- One debit posting normally uses each `paymentDetailsId`.
- Additional Forex Gain/Loss rows may use ledger `12`.
- Voucher association is through `voucherTypeId`, `voucherNo`, `invoiceNo`, and `yearId`.

```text
tbl_PaymentMaster (1)
    +----< tbl_PaymentDetails (many)
    |          +---- tbl_LedgerPosting detail debit
    |          +----< Party Balance allocations for party lines
    |
    +---- tbl_LedgerPosting header credit (detailsId = 0)

original invoice Party Balance reference
    +----< Payment allocation row
           original invoice in voucherTypeId/voucherNo
           payment in againstVoucherTypeId/againstVoucherNo
```

The generated mappings do not declare these transaction foreign keys. The relations are confirmed behaviorally through procedure definitions and live rows.

## Stored-procedure findings

The procedures below were inspected read-only. The FastAPI implementation should reproduce their verified behavior with direct SQLAlchemy operations inside explicit transactions.

### Master and details

- `PaymentMasterAdd`: inserts the header, accepts `isPosted`, and rejects duplicate voucher type/number through `CheckDuplicateVoucher_PaymentVoucher`.
- `PaymentMasterEdit`: updates the complete header including `isPosted`.
- `PaymentDetailsAdd`, `PaymentDetailsEdit`, `PaymentDetailsDelete`: maintain detail rows, including `Vehicle`.
- `PaymentMasterPost`: only flips `isPosted` from `0` to `1`; it does **not** build ledger or Party Balance rows.
- `PaymentMasterUnPost`: flips `isPosted` to `0` and deletes active ledger and Party Balance rows for the payment.
- `PaymentVoucherDelete`: deletes allocations, reconciliation links, postings, details, and master.

### Party allocation

- `AccountGroupIdCheck`: permits the Against popup only for `billByBill = 1` ledgers under Sundry Creditors (`22`) or Sundry Debtors (`26`), including descendant groups.
- `PartyBalanceComboViewByLedgerId`: for Payment (`Dr`), returns references whose credit minus debit balance is positive.
- `PartyBalancePendingAmount`: calculates the current pending amount and includes the voucher's existing allocation during edit.
- `PartyBalanceAdd` / `PartyBalanceEdit`: maintain posted allocations.
- `PartyBalanceAdd_Unposted` / related edit/delete/view procedures: maintain draft allocations.
- `PartyBalanceCheckReference`: detects whether the Payment Voucher itself has become a reference used elsewhere.

### Posting, lookups, register, and print

- `LedgerPostingAdd` and related edit/delete procedures maintain accounting rows.
- `CashOrBankComboFill` returns ledgers under Bank OD, Cash-in Hand, and Bank Account groups.
- `PaymentVoucherCurrencyComboFill` and exchange-rate procedures provide date-specific currency choices.
- `PaymentMasterMax`, suffix/prefix, voucher-type, and numbering procedures determine the displayed number.
- `PaymentMasterSearch`, `PaymentMasterViewByMasterId`, `PaymentDetailsViewByMasterId`, `PaymentReportSearch`, and `PaymentVoucherPrinting` support detail/register/print projections.

## Implemented API contract

All routes require the existing authenticated-user dependency. The client never submits trusted totals, exchange rates, posting rows, `userId`, `financialYearId`, or `isPosted`.

### Routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/payment-vouchers/page` | Paginated register with inclusive date, voucher number, type, source account, exact amount, party, cheque number, and posted filters. |
| `GET` | `/payment-vouchers/{paymentMasterId}` | Header, detail lines, nested allocations, totals, and lifecycle state. |
| `POST` | `/payment-vouchers` | Create an unposted draft. |
| `PATCH` | `/payment-vouchers/{paymentMasterId}` | Update an unposted draft. |
| `DELETE` | `/payment-vouchers/{paymentMasterId}` | Delete an unposted, unreferenced, unreconciled voucher. |
| `POST` | `/payment-vouchers/{paymentMasterId}/post` | Revalidate and atomically create postings/active allocations, then mark posted. |
| `POST` | `/payment-vouchers/{paymentMasterId}/unpost` | Reverse all active effects and restore a usable draft allocation state. |
| `GET` | `/payment-vouchers/{paymentMasterId}/print-data` | Stable print projection. |
| `GET` | `/payment-vouchers/lookups/voucher-types` | Active Payment Voucher subtypes. |
| `GET` | `/payment-vouchers/lookups/paying-accounts` | Eligible Cash-in Hand, Bank Account, and Bank OD source accounts with group labels. |
| `GET` | `/payment-vouchers/lookups/detail-accounts` | Searchable detail ledgers with bill-by-bill capability. |
| `GET` | `/payment-vouchers/lookups/party-ledgers` | Searchable bill-by-bill Sundry Creditor/Debtor ledgers for the register Party filter. |
| `GET` | `/payment-vouchers/lookups/exchange-rates?date=...` | Date-valid currency/rate records. |
| `GET` | `/payment-vouchers/lookups/vehicles` | Optional vehicle choices. |
| `GET` | `/payment-vouchers/lookups/numbering-rule?voucherTypeId=...&date=...` | Numbering preview/rule, not a reserved final number. |
| `GET` | `/payment-vouchers/party-ledgers/{ledgerId}/open-references` | Open references and current pending balances for Against allocation. |

### Proposed write payload

```json
{
  "voucherTypeId": 35,
  "voucherDate": "2026-09-27T00:00:00",
  "payingLedgerId": 138278,
  "manualVoucherNo": null,
  "narration": "Supplier payment",
  "idempotencyKey": "payment-voucher-unique-key",
  "lines": [
    {
      "paymentDetailsId": null,
      "ledgerId": 209082,
      "amount": "487.50000",
      "exchangeRateId": 1,
      "chequeNo": null,
      "chequeDate": null,
      "vehicleId": null,
      "allocations": [
        {
          "partyBalanceId": null,
          "referenceType": "against",
          "sourceVoucherTypeId": 41,
          "sourceVoucherNo": "3639",
          "amount": "105.00000"
        },
        {
          "partyBalanceId": null,
          "referenceType": "against",
          "sourceVoucherTypeId": 41,
          "sourceVoucherNo": "3620",
          "amount": "382.50000"
        }
      ]
    }
  ]
}
```

For an ordinary expense line, `allocations` is empty. For a bill-by-bill party line, the server requires allocations and calculates/validates the line amount from them. Source invoice number, pending balance, contract identity, source exchange rate, names, base amounts, and totals are loaded server-side.

## Service and repository flow

### Create/update draft

1. Authenticate the user and start one database transaction.
2. Resolve the financial year and verify the date is open.
3. Validate Payment Voucher type and paying-account eligibility.
4. Validate detail ledgers, currencies, cheque fields, vehicle IDs, and positive amounts.
5. For each party line, lock/re-read every source reference and recompute pending balance.
6. Reject duplicate source references in the request and allocations above pending.
7. Require the allocation base total to equal its party detail base total.
8. Allocate the final voucher number safely inside the transaction.
9. Insert/update master with `isPosted = 0`, reconcile details by identity, and reconcile `tbl_PartyBalance_Unposted` rows.
10. Confirm base debits equal the header total, commit, and return the refreshed draft.

### Post

1. Lock and reload the draft; if already posted with complete effects, return it idempotently.
2. Re-run all eligibility, period, exchange-rate, and pending-balance checks.
3. Ensure no active posting/allocation set already exists for the voucher.
4. Insert the header credit and each detail debit, including any verified Forex Gain/Loss row.
5. Convert draft Party Balance allocations into active rows with the correct original/payment reference orientation.
6. Verify total debit equals total credit and every party line equals its allocations.
7. Mark `isPosted = 1` last and commit everything atomically.

### Unpost/delete

1. Reject unpost if a later Party Balance row references a `New` payment reference.
2. Reject or require separately approved handling when bank reconciliation exists.
3. Preserve/recreate the draft allocations before deleting active accounting effects.
4. Delete all active ledger and Party Balance effects and set `isPosted = 0` atomically.
5. Delete is allowed only for an unposted voucher with no external reference or reconciliation dependency.

## Validation and safety rules

- At least one complete line and a positive total are required.
- Paying account and detail account cannot be the same.
- Paying account must belong to a verified Cash-in Hand, Bank Account, or Bank OD group; no stricter subtype mapping is enforced without evidence.
- Duplicate detail ledgers should be rejected; the legacy grid removes already-selected ledgers from later rows.
- Amounts use `Decimal`, never float.
- The server resolves exchange-rate values by ID/date and calculates all base amounts.
- `Against` amount must be greater than zero and no greater than the locked current pending amount.
- One source reference cannot be allocated twice within the same request.
- Party-line amount must equal the sum of its allocations under the verified currency rule.
- Cheque date requires a cheque number; the API uses `null`, not a legacy sentinel date.
- Detail IDs and Party Balance IDs supplied on update must belong to the addressed voucher/line.
- Draft update/delete is blocked after posting.
- Voucher numbering, idempotency, all rows, and final `isPosted` transition share one transaction.
- Any error rolls back the complete operation.

## Implemented application structure

- `app/payment_vouchers/schemas.py`: stable list, detail, write, lookup, and nested allocation models.
- `app/payment_vouchers/repository.py`: direct SQLAlchemy lookup, register/detail, draft, allocation, posting, locking, and reversal queries. It contains no application stored-procedure calls.
- `app/payment_vouchers/service.py`: calculation, validation, numbering, idempotency, pending-reference locking, posting, unposting, and transaction coordination.
- `app/payment_vouchers/router.py`: authenticated routes listed above, registered by `app/main.py`.
- `tests/test_payment_vouchers.py`: focused mock-only tests that perform no MSSQL writes.
- `FleetTrack Frontend/src/app/payment-vouchers/page.tsx`: register, draft editor, per-line searchable account picker, guarded line addition/deletion, bill-allocation dialog, lifecycle actions, and browser print flow.
- `FleetTrack Frontend/src/app/payment-vouchers.css`: compact responsive presentation shared with the Contra visual system.
- `FleetTrack Frontend/src/lib/api.ts`: stable Payment Voucher request and response contracts.

The remaining verification is a user-controlled live sequence: ordinary cash expense draft, bank supplier partial allocation, multi-invoice allocation, post, retry post, unpost, update, and delete.

## Acceptance tests

- Active voucher type and independently verified cash/bank/Bank OD source eligibility.
- Closed period and invalid financial year.
- Automatic/manual number collision and concurrent create.
- Missing line, zero/negative amount, duplicate ledger, and header/detail same account.
- Direct expense line with one and multiple currencies.
- Bill-by-bill party line with `Against`, `New`, and `OnAccount`.
- Partial invoice settlement and multiple invoices on one party line.
- Allocation above pending and stale pending balance under concurrent requests.
- Allocation total mismatch and duplicate source reference.
- Cheque validation and optional vehicle attribution.
- Balanced postings, Forex Gain/Loss, and rounding.
- Duplicate post idempotency and rollback after a simulated mid-post failure.
- Unpost followed by successful edit/repost.
- Delete blocked by external Party Balance reference or bank reconciliation.
- Posted voucher update/delete rejection.

## Remaining unknowns

- Exact Credit Card Payment Voucher source-account group; no historical type-40 rows were available to prove it.
- The business/reporting effect of `tbl_PaymentDetails.Vehicle` and whether zero or `NULL` is canonical.
- Approved behavior for unposting/deleting a bank-reconciled payment.
- Whether stale `tbl_PartyBalance_Unposted` rows found for some posted historical vouchers are intentional history or legacy residue. They must not be treated as authoritative without a controlled test.
- Exact foreign-currency rule for `New` and `OnAccount` references in the customized application.
- Whether a posted Payment Voucher may be unposted after its `New` reference has been allocated by a later voucher.

Backend implementation is complete in source. Controlled MSSQL write verification remains required before production use; allocation/post/unpost integrity is the highest-risk verification area.
