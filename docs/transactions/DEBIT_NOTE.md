# Debit Note dossier

## Purpose and evidence

Records a debit adjustment to a party or account. The menu shows **Debit Note - Ctrl+F9**. Whether this is supplier debit, customer debit, or a generic accounting note is `UNKNOWN`.

Status: **MISSING**.

## Candidate UI and lifecycle

Mapped fields support voucher/date/numbering, total/narration, and detail ledger debit/credit, exchange rate, cheque number/date. No direct source-document ID or tax amount appears on the header, so invoice adjustment and tax behavior must be discovered.

```text
new -> select party/source if applicable -> enter balanced adjustment
    -> save -> post -> allocate/open debit -> optional unpost
```

## Data and relationships

- Header: `tbl_DebitNoteMaster`.
- Lines: `tbl_DebitNoteDetails`.
- Accounting/open item: `tbl_LedgerPosting`, `tbl_PartyBalance`.
- Candidate source: sales or purchase documents, relationship `UNKNOWN`.
- Lookups: account ledger/group, exchange rate, voucher type, suffix, financial year; tax use `UNKNOWN`.

No generated FKs enforce any of these candidate joins.

## Procedures and target code flow

Debit Note procedures and result sets are `UNKNOWN`. Target `/debit-notes` API mirrors the verified lifecycle, not automatically the Credit Note API; their directions, tax, and allocation rules may differ.

## Accounting and safety rules

- Establish party direction and whether a source invoice is mandatory.
- Establish whether detail rows must balance independently or the party/control side is implicit.
- Verify open-item creation/allocation and tax handling.
- Prevent duplicate application and over-adjustment.
- Post/unpost atomically across header/details, ledger, party balance, and source state.

## Implementation and tests

Capture standalone/applied, customer/supplier, taxed/untaxed, partial/full, post/unpost examples and compare their ledger/party rows. Define API payload only after that trace.

Acceptance tests: wrong party direction; missing source; over-adjustment; tax; exchange rate; duplicate post; unpost with allocations; closed period; balanced ledger; rollback.

Estimate: **5-8 working days**. Main risk is assuming Debit Note is simply Credit Note with signs reversed.
