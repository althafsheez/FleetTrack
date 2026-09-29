# PDC Clearance dossier

## Purpose and evidence

Transitions a registered payable or receivable post-dated cheque into its bank-cleared or other terminal/intermediate state. The menu shows **PDC Clearance** with no shortcut observed. No current module or screen capture exists.

Status: **MISSING**.

## Candidate UI and lifecycle

The mapped record contains voucher/date/numbering, ledger, `type`, `againstId`, voucher type, narration, `status`, user, and financial year. It likely selects a pending PDC and records its result, but allowed types/status values and whether multiple clearance events are possible are `UNKNOWN`.

```text
select payable/receivable type -> list eligible pending instruments
-> select instrument -> clear/return/cancel under verified status rules
```

## Data and relationships

- Clearance event/header: `tbl_PDCClearanceMaster`.
- Source instruments: `tbl_PDCPayableMaster`, `tbl_PDCReceivableMaster`.
- Accounting: `tbl_LedgerPosting`, potentially `tbl_PartyBalance`.
- Bank/party: `tbl_AccountLedger`.
- Numbering/period: voucher type, suffix, financial year.

`againstId` is polymorphic by candidate `type`; there is no generated FK. Never join it to both PDC tables without first validating `type`.

## Procedures and target code flow

Clearance add/delete/post/unpost/status procedures are `UNKNOWN`. Target `/pdc-clearances` service must lock the source instrument, validate its current lifecycle, persist the event and all accounting/allocation effects atomically, then return the resulting source status.

## Safety rules

- One source instrument cannot receive conflicting effective clearances.
- Validate source type, amount, cheque identity, bank, and due-date rule.
- Define whether return/dishonour is another clearance record or a reversal/status update.
- Receivable clearance may settle/reopen customer debt; payable clearance may settle/reopen supplier debt.
- Retrying a command must return the existing result or conflict, never duplicate postings.

## Implementation and tests

Trace payable and receivable clearance, early clearance, return/dishonour, cancellation, unpost, and re-clearance. Identify status labels/IDs from approved records and procedure branches.

Acceptance tests: wrong polymorphic type; missing source; double clear; clear cancelled instrument; amount/date mismatch; return reopening; concurrent attempts; complete rollback/unpost; register filters.

Estimate: **5-8 working days** after both PDC source modules exist. Main risk is the unconstrained polymorphic `againstId`.
