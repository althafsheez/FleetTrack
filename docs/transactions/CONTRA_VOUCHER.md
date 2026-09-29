# Contra Voucher dossier

## Status and scope

Contra Voucher records transfers between cash and bank accounts without creating customer or supplier income or expense. The legacy Transactions menu exposes **Contra Voucher - F4**.

Current FleetTrack status: **BACKEND AND FRONTEND IMPLEMENTED / LIVE MSSQL WRITES UNVERIFIED**.

The approved backend implements this contract with direct SQLAlchemy table access. It does not call application stored procedures. The stored-procedure and legacy-source investigation remains evidence for business behavior only. No database object or generated model was changed.

### Evidence confidence

| Evidence | Confidence | Notes |
|---|---:|---|
| Supplied legacy UI capture | Confirmed | Shows direction, fields, grid, update/delete/print behavior. |
| Generated SQLAlchemy table mappings | Confirmed | Confirms the three principal table shapes, but not declared transaction foreign keys. |
| Matching OpenMiracle legacy source | Strong candidate | Form, tables, fields, shortcut, and UI labels closely match the supplied application. Used to reconstruct behavior and procedure calls. |
| Live `Balance` MSSQL definitions and rows | **UNVERIFIED** | Local MSSQL was unavailable during this investigation. Every procedure name and side effect must be checked against the live database before coding. |

Legacy UI evidence: [contra-voucher.png](../../reference/screenshots/transactions/contra-voucher.png)

Candidate source inspected at revision `783497755f061913a8412b0e6f6810a86cb19ef1`: `Transactions/frmContraVoucher.cs`, `Classes/SP/ContraMasterSP.cs`, `Classes/SP/ContraDetailsSP.cs`, `Classes/SP/LedgerPostingSP.cs`, `Classes/General/TransactionsGeneralFill.cs`, and `Registers/frmContraRegister.cs`. This source is supporting evidence, not a substitute for inspecting FleetTrack's live database.

## Observed legacy UI

The supplied screen is an existing voucher in update mode. It contains:

- Direction: `Deposit` or `Withdrawal`; `Deposit` is selected.
- Voucher No: displayed as `175` and apparently not editable in update mode.
- Date: `10 Sep 2026`.
- Header Bank/Cash account: `ADCB`.
- Detail grid: `Sl No`, `Bank/Cash a/c`, `Amount`, `Currency`, `Cheque No.`, `Cheque Date`.
- Example detail: `Cash`, `4810.00`, `Dirham / AED`.
- Narration: `DEPOSITED TO ADCB`.
- Calculated Total: `4810.00`.
- Row removal, `Print after save`, `Update`, `Clear`, `Delete`, and `Close` controls.

The matching legacy source also supports create/save mode and register/print flows. It stores direction values as `Deposit` and `Withdraw`; the UI label `Withdrawal` must not be copied directly into the database.

## Business interpretation

The selected header account is the main cash/bank account. Each grid row is an offset cash/bank account. A voucher may contain multiple offset rows.

### Deposit

Money enters the header account from the detail accounts.

| Posting | Debit | Credit |
|---|---:|---:|
| Header account | Base-currency total | 0 |
| Each detail account | 0 | Line amount x exchange rate |

Example from the capture: debit ADCB AED 4,810 and credit Cash AED 4,810.

### Withdrawal

Money leaves the header account and enters the detail accounts.

| Posting | Debit | Credit |
|---|---:|---:|
| Header account | 0 | Base-currency total |
| Each detail account | Line amount x exchange rate | 0 |

The voucher total is the sum of converted detail lines, rounded using the configured decimal-place rule. `tbl_ContraDetails.amount` stores the entered foreign-currency amount; `tbl_LedgerPosting` stores converted base-currency debit or credit values.

## Lifecycle conclusion

The matching legacy implementation is **save-and-post**, not draft-then-post:

```text
new -> select direction/date/header account -> enter offset lines
    -> validate -> save master + details + balanced ledger postings atomically
    -> optionally print

existing -> load master/details -> update all affected rows and postings atomically
         -> or delete voucher, details, and postings atomically
```

There is no `isPosted` column on the mapped Contra master and no separate Post or Unpost control in the supplied UI. Therefore v1 must not expose `/post` or `/unpost` endpoints unless the live database proves a different lifecycle.

## Data model and relationships

### `tbl_ContraMaster`

Header and document identity:

- `contraMasterId`: primary identity used by details and API routes.
- `voucherNo`, `invoiceNo`, `suffixPrefixId`: numbering fields.
- `date`: voucher date.
- `ledgerId`: header cash/bank ledger.
- `type`: `Deposit` or `Withdraw`.
- `totalAmount`: converted base-currency total.
- `narration`, `userId`, `voucherTypeId`, `financialYearId`.
- `extraDate`, `extra1`, `extra2`: legacy extension fields.

### `tbl_ContraDetails`

One or more offset lines:

- `contraDetailsId`: line identity.
- `contraMasterId`: candidate relation to the master.
- `ledgerId`: offset cash/bank ledger.
- `amount`: entered amount in the selected currency.
- `exchangeRateId`: selected currency/rate record.
- `chequeNo`, `chequeDate`.

### `tbl_LedgerPosting`

Accounting entries generated when the Contra Voucher is saved:

- Detail posting: `detailsId = contraDetailsId`.
- Header balancing posting: `detailsId = 0` in the matching source.
- Voucher association: `voucherTypeId`, `voucherNo`, `invoiceNo`, and `yearId`.
- Amount: one of `debit` or `credit` is populated per posting.
- Detail cheque information is copied to the corresponding posting.

```text
tbl_ContraMaster (1)
    | contraMasterId
    +----< tbl_ContraDetails (many)
                | contraDetailsId
                +---- tbl_LedgerPosting.detailsId (one candidate detail posting)

tbl_ContraMaster
    +---- tbl_LedgerPosting (one balancing row identified by voucher fields,
                             with detailsId = 0 in matching source)
```

These are behavioral joins, not confirmed schema foreign keys. Live keys and indexes remain `UNKNOWN` until MSSQL inspection succeeds.

Lookup/source tables include `tbl_AccountLedger`, `tbl_AccountGroup`, `tbl_ExchangeRate`, `tbl_VoucherType`, `tbl_SuffixPrefix`, `tbl_FinancialYear`, and the company/settings data used for printing and negative-balance policy.

## Stored-procedure inventory

The strongly matching legacy source calls the following procedures. Names and signatures must be reconciled with `sys.procedures`, `sys.parameters`, `sys.sql_expression_dependencies`, and `OBJECT_DEFINITION` in the live `Balance` database.

### Create and update

- `ContraMasterAdd`: accepts voucher/invoice number, suffix/prefix, date, header ledger, type, total, narration, user, voucher type, financial year, and extra fields; returns the new master identity.
- `ContraMasterEdit`: accepts master identity plus invoice number, suffix/prefix, date, header ledger, type, total, narration, user, voucher type, financial year, and extra fields. The matching wrapper does not pass `voucherNo`; verify whether numbering is immutable.
- `ContraDetailsAddReturnWithhIdentity`: accepts master identity, detail ledger, amount, exchange-rate identity, cheque number/date, and extra fields; returns the new detail identity.
- `ContraDetailsEdit`: accepts detail identity and the complete detail fields.
- `ContraDetailsDelete`: deletes one line.
- `LedgerPostingAdd`: accepts date, voucher type/number, ledger, debit, credit, detail identity, year, invoice number, cheque number/date, and extra fields.
- `LedgerPostingEdit`: accepts posting identity and the complete posting fields.
- `LedgerPostingIdFromDetailsId(detailsId, voucherNo, voucherTypeId)`: locates a detail posting.
- `LedgerPostDeleteByDetailsId(detailsId, voucherNo, voucherTypeId)`: deletes a detail posting.
- `LedgerPostingIdForTotalAmount(voucherNo, voucherTypeId)`: locates the master balancing posting.

### Delete, reads, register, and print

- `ContraVoucherDelete`: candidate all-in-one voucher deletion by master/voucher identity.
- `ContraMasterView`: returns one header.
- `ContraDetailsViewWithMasterId`: returns lines for one header.
- `ContraVoucherRegisterSearch`: searches by date range, voucher number, ledger, and type.
- `ContraVoucherPrinting`: returns the print projection for a master/company.

### Numbering and validation

- `ContraVoucherCheckExistence`: duplicate voucher-number check.
- `ContraVoucherMasterMax`: candidate next-number source.
- `GetVoucherNoMaxByVoucherTypeIdForContraVoucher`: maximum voucher number for the type.
- `VoucherNumberAutomaicGeneration`: voucher-number formatting/generation.

### Lookups

- `CashOrBankComboFill`: eligible cash/bank accounts.
- `CurrencyComboByDate`: currency/rate choices for a voucher date.
- `GetExchangeRateByExchangeRateId`: selected conversion rate.
- `AccountGroupwithLedgerId`: classifies a line ledger, including bank/cash behavior.
- Voucher type, suffix/prefix, financial-year, and settings procedures used by shared legacy helpers.

The procedure bodies are still required. Wrapper names alone do not prove transaction boundaries, cascade behavior, concurrency safety, or all result-set columns.

## Validation and side effects

### Confirmed from the matching workflow

- Voucher number, header account, at least one complete line, nonzero total, line account, amount, and currency are required.
- The date must fall inside the active financial year.
- Duplicate voucher numbers are checked.
- Only cash/bank ledgers are offered by the legacy lookup.
- Cheque fields are enabled only when a detail ledger is classified as a bank account.
- Changing a line to cash clears and disables its cheque fields.
- Missing cheque dates use a legacy sentinel in the candidate code. The API should expose `null`; repository compatibility with the actual procedure must be verified.
- Saving creates the accounting postings immediately.

### Negative-balance policy

The legacy setting `NegativeCashTransaction` appears to support warning and blocking modes:

- Withdrawal checks the source/header balance after subtracting the voucher total.
- Deposit checks each source/detail account after subtracting its line amount.
- `Warn` requests confirmation; `Block` rejects; another mode permits the transaction.

The exact setting values, current-balance procedure, multi-currency basis, and whether the warning is auditable remain `UNKNOWN`.

### Required API invariants

- Header and detail ledgers must belong to the live-verified `Cash-in Hand`, `Bank Account`, or `Bank OD A/C` groups. `ViewCashBank` is not authoritative in this database because it includes `Sundry Debtors` and excludes `Bank Account`.
- A detail ledger cannot equal the header ledger.
- Amounts must be positive `Decimal` values within SQL precision.
- Exchange-rate IDs must be valid for the voucher date; clients cannot submit a trusted rate.
- Cheque values are accepted only for bank detail lines.
- The server calculates each base amount and the total.
- Base-currency debits must equal credits before commit.
- Update line IDs must belong to the addressed master.
- Duplicate number checks and numbering allocation must occur inside the write transaction.
- Any failure must roll back master, details, and all ledger postings.

## Implemented FastAPI contract

All routes require the existing authenticated-user dependency. Response schemas must be stable API models and must not expose generated SQLAlchemy models directly.

### Routes

| Method | Route | Purpose |
|---|---|---|
| `GET` | `/contra-vouchers/page` | Paginated register using inclusive date-only `fromDate`/`toDate`, partial `voucherNo`, header-account `ledgerId`, `direction`, `offset`, and `limit`; rows include offset-account names and line counts. |
| `GET` | `/contra-vouchers/{contraMasterId}` | Header, lines, calculated totals, and immutable identity fields. |
| `POST` | `/contra-vouchers` | Validate, number, save, and post one voucher atomically. |
| `PATCH` | `/contra-vouchers/{contraMasterId}` | Update header, reconcile line additions/edits/removals, and update postings atomically. |
| `DELETE` | `/contra-vouchers/{contraMasterId}` | Delete the complete voucher and its postings atomically. |
| `GET` | `/contra-vouchers/lookups/voucher-types` | Contra voucher type and numbering mode. |
| `GET` | `/contra-vouchers/lookups/accounts` | Eligible cash/bank accounts with account classification. |
| `GET` | `/contra-vouchers/lookups/exchange-rates?date=...` | Date-valid currency/rate choices. |
| `GET` | `/contra-vouchers/lookups/numbering-rule?voucherTypeId=...&date=...` | Display information for automatic/manual numbering. |
| `GET` | `/contra-vouchers/{contraMasterId}/print-data` | Legacy-compatible print projection. |

Route declaration must place static lookup routes before `/{contraMasterId}` if the router framework could otherwise treat `lookups` as an ID.

No separate post/unpost endpoint is implemented for v1.

### Create request

```json
{
  "voucherTypeId": 1,
  "voucherDate": "2026-09-10T00:00:00",
  "direction": "deposit",
  "headerLedgerId": 100,
  "manualVoucherNo": null,
  "narration": "DEPOSITED TO ADCB",
  "confirmNegativeBalance": false,
  "lines": [
    {
      "contraDetailsId": null,
      "ledgerId": 200,
      "amount": "4810.00000",
      "exchangeRateId": 1,
      "chequeNo": null,
      "chequeDate": null
    }
  ]
}
```

The API enum is `deposit | withdrawal`; the repository maps it to legacy `Deposit | Withdraw`. The server derives `userId`, financial year, suffix/prefix, voucher number when automatic, exchange rate, converted line values, and `totalAmount`.

For update, existing `contraDetailsId` values identify retained lines, omitted old IDs are deletions, and `null` IDs are additions. Voucher number changes are rejected because the verified legacy workflow treats the number as immutable during edit.

### Error contract

- `404`: voucher, lookup row, or addressed detail does not exist.
- `409`: duplicate voucher number, ineligible account, header/detail account collision, closed period, blocked negative balance, stale update, or deletion restricted by verified downstream usage.
- `422`: malformed direction/date, no lines, nonpositive/overflow amount, missing currency, invalid cheque combination, or manual/automatic numbering mismatch.
- `503`: sanitized database/procedure failure when the operation cannot be completed safely.

Warnings should be returned as structured codes, not UI text. A warned negative balance requires an explicit second request with `confirmNegativeBalance=true`; the service must recalculate the balance rather than trusting the first response.

## Backend flow

Target architecture:

```text
router -> Pydantic schemas -> service -> repository
       -> existing tables through SQLAlchemy -> MSSQL transaction -> stable response
```

### Create transaction

1. Resolve authenticated user, voucher type, active financial year, and numbering rule.
2. Validate the date, account eligibility, detail uniqueness rules, currencies, cheque fields, and amounts.
3. Fetch trusted exchange rates and calculate converted amounts and total using `Decimal`.
4. Apply the negative-balance policy.
5. Allocate or validate the voucher number inside the transaction.
6. Call `ContraMasterAdd` and capture `contraMasterId`.
7. For each line, call `ContraDetailsAddReturnWithhIdentity`, then `LedgerPostingAdd` with `detailsId=contraDetailsId`.
8. Add the single balancing header posting with `detailsId=0` if confirmed by the live procedure/data.
9. Assert debit equals credit and expected row counts exist.
10. Commit once and return the reloaded detail response. Any failure rolls back all steps.

### Update transaction

1. Lock/reload the current voucher and verify it is editable.
2. Re-run all create validations and compute the new total.
3. Delete removed details and their postings using the verified order.
4. Edit retained details and their identified postings.
5. Add new details and postings.
6. Call `ContraMasterEdit`.
7. Locate and update the balancing posting.
8. Assert ownership, row counts, and accounting balance; commit once.

### Delete transaction

1. Lock/reload the voucher and verify deletion is allowed.
2. Call the verified all-in-one delete procedure, or delete postings/details/master in the dependency order proven by the procedure bodies.
3. Assert that no orphan Contra details or postings remain.
4. Commit once.

Repository methods must participate in the service-owned SQLAlchemy transaction and must not commit independently. The matching desktop code opens separate connections per operation; reproducing that behavior would allow partial vouchers.

## Numbering and concurrency

The matching legacy code appears to calculate the next voucher number from a current maximum. That is unsafe under concurrent API requests. Before implementation, determine whether the live procedure already serializes allocation.

If it does not, the approved implementation needs a transaction-scoped SQL Server application lock or another database-supported serialization mechanism, followed by a duplicate recheck before insert. No schema or procedure modification is authorized by this dossier.

## Known uncertainty requiring live MSSQL

The following must be resolved before the implemented POST/PATCH/DELETE code is considered production-verified:

1. Exact procedure definitions, parameters, returned columns, dependencies, and error behavior.
2. Actual Contra `voucherTypeId`, numbering mode, optional suffix/prefix behavior, and financial-year rules.
3. Whether `ContraVoucherDelete` removes all detail and posting rows safely.
4. How the balancing posting is uniquely identified and whether `detailsId=0` is universal.
5. Cash/bank account-group classification and active-ledger filters.
6. Exchange-rate direction, precision, and rounding configuration.
7. Negative-balance setting values and balance calculation basis.
8. Whether voucher date or application current date is used for ledger postings. The matching source appears to use application current date; this may be a legacy defect and must not be copied without evidence.
9. Sentinel handling for empty cheque dates.
10. Register and print result-set columns.
11. Existing keys/indexes and whether duplicate numbering has database enforcement.

## Tests and acceptance

### Unit/service tests

- Deposit and withdrawal produce opposite, balanced entries.
- Multiple detail lines and currencies calculate the base total correctly.
- Decimal rounding follows the verified system rule.
- Automatic and manual numbering validation.
- Missing, inactive, and non-cash/bank ledger rejection.
- Header account repeated in details rejection.
- Zero, negative, and precision-overflow amount rejection.
- Bank cheque validation and cash cheque clearing/rejection.
- Negative-balance allow, warn/confirm, and block paths.
- Update line diffing rejects foreign detail IDs and handles add/edit/remove.
- Duplicate create retry does not create additional rows.
- Forced failure after each write step rolls back the entire operation.

### Controlled MSSQL integration tests after approval

- Inspect and archive sanitized procedure metadata and definitions.
- Create one Deposit and one Withdrawal with controlled accounts.
- Verify one master, expected detail rows, expected posting rows, converted amounts, dates, cheque fields, and balanced totals.
- Update header fields and add/edit/remove lines; verify no orphan postings.
- Delete the voucher and verify complete cleanup.
- Exercise simultaneous automatic-number allocation.
- Force a procedure failure and verify zero partial rows.
- Verify register filters, detail loading, and print projection.

No live write test should use customer production records.

## Implemented backend structure

1. `contra_vouchers/schemas.py`: stable request, response, register, lookup, and numbering models.
2. `contra_vouchers/repository.py`: direct SQLAlchemy table reads/writes and SQL Server numbering lock; no application procedure calls.
3. `contra_vouchers/service.py`: business validation, currency conversion, negative-balance policy, numbering, balanced posting construction, transaction ownership, and response mapping.
4. `contra_vouchers/router.py`: authenticated register, detail, CRUD, lookup, numbering, and print-data routes.
5. `tests/test_contra_vouchers.py`: focused mock-only accounting and rollback tests with no MSSQL writes.

The Next.js `/contra-vouchers` screen now includes the paginated register, filters, create/edit modal, delete, browser print, date-aware lookups, multi-line entry, and structured negative-balance confirmation. Remaining work is authenticated end-to-end verification and explicitly approved controlled MSSQL create/update/delete tests.

## Estimate and decision gate

- Read-only live procedure verification: **0.5-1 working day** once MSSQL is reachable.
- FastAPI backend and isolated tests: **implemented**.
- Controlled live MSSQL verification and resulting corrections: **0.5-1 working day** once the database is reachable and write testing is approved.
- Contra UI, register, and print integration: implemented; controlled live verification remains.

**Current gate:** do not claim production readiness or submit live Contra writes until the `Balance` SQL Server is reachable and controlled write testing is separately approved. The backend routes are implemented, but live behavior remains unverified.
