# Journal Voucher dossier

## Purpose and evidence

Records non-cash general-ledger adjustments with explicit debit and credit lines. The menu shows **Journal Voucher - F7**. No current module or screen capture exists.

Status: **MISSING / ACCOUNTING FOUNDATION**.

## Candidate UI and lifecycle

The mapped schema supports voucher/date, total/narration, and a grid of ledger, debit, credit, exchange rate, cheque information, vehicle, and line narration. Whether party/open-item allocation is available on the legacy screen is `UNKNOWN`.

```text
new -> enter debit/credit lines -> validate balanced journal
    -> save draft -> post -> register/print -> optional unpost
```

## Data and relationships

- Header: `tbl_JournalMaster`.
- Lines: `tbl_JournalDetails`.
- Posting: `tbl_LedgerPosting`.
- Candidate party references: `tbl_PartyBalance` when customer/supplier ledgers participate; exact rules `UNKNOWN`.
- Lookups: account ledger/group, exchange rate, vehicle, voucher type, numbering, financial year.

Header/detail and all lookup joins are unenforced by generated FKs.

## Procedures and target code flow

Journal procedure names and behavior are `UNKNOWN`. Target `/journal-vouchers` module provides list/detail/lookups/draft CRUD/post/unpost/print after read-only investigation.

## Accounting and safety rules

- Every line must have either debit or credit under the verified zero-value policy, never both.
- Base-currency debit total must exactly equal credit total after verified rounding.
- At least two effective lines are required.
- Party ledgers may require `tbl_PartyBalance`; do not post only to the general ledger if the legacy workflow maintains open items.
- Vehicle attribution is optional only if verified.
- Posting/unposting must be all-or-nothing and idempotent.

## Implementation and tests

Trace simple two-line, multi-line, customer adjustment, supplier adjustment, foreign-currency, vehicle-attributed, post, and unpost examples. Reuse shared numbering/posting services only where procedures demonstrate the same contract.

Acceptance tests: unbalanced journal; both debit/credit supplied; empty/zero lines; rounding boundary; party-balance side effect; invalid account/vehicle; duplicate post; complete unpost; closed period; rollback.

Estimate: **5-8 working days**. Main risk: a balanced `tbl_LedgerPosting` set can still be incomplete if party balances are omitted.
