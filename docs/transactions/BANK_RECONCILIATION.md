# Bank Reconciliation dossier

## Purpose and evidence

Marks bank-ledger postings as cleared against a statement date and provides outstanding/cleared views. The menu shows **Bank Reconciliation - Alt+B**. No current module or screen capture exists.

Status: **MISSING**.

## Candidate UI and lifecycle

The mapped table stores only reconciliation ID, `ledgerPostingId`, and `statementDate` plus generic extras. The expected screen is a bank/date selector and posting grid with cheque/reference, transaction date, debit/credit, cleared state, statement date, and totals, but this is INFERRED.

```text
select bank and statement period -> load unreconciled ledger postings
-> mark/enter statement dates -> save reconciliation
-> reopen/correct only under verified rules
```

There is no mapped header, imported statement table, or closing-balance field; statement import and formal period close are `UNKNOWN`.

## Data and relationships

- Reconciliation marker: `tbl_BankReconciliation`.
- Source transaction: `tbl_LedgerPosting` via candidate `ledgerPostingId`.
- Bank account: `tbl_AccountLedger` through posting `ledgerId` and verified bank account-group filter.
- Source voucher detail: posting voucher type/no/invoice/cheque fields.

No generated FK enforces reconciliation-to-posting identity.

## Procedures and target code flow

List/save/delete/reopen procedures are `UNKNOWN`. Target flow:

`GET /bank-reconciliations/entries?bankLedgerId&from&to&status` -> read postings plus markers; `POST/PATCH` applies approved statement dates in one transaction; no accounting posting should be created unless legacy evidence proves otherwise.

## Safety rules

- A posting can have at most one effective reconciliation marker under the verified uniqueness rule.
- Only postings for the selected verified bank ledger are eligible.
- Reconciliation should not change voucher amounts or create accounting entries.
- Unposting/deleting a source voucher with a reconciliation marker must reject or first follow a verified reopen workflow.
- Concurrent saves must not duplicate reconciliation rows.

## Implementation and tests

Capture one reconciled and outstanding statement and inspect duplicate/index behavior, correction workflow, opening/closing totals, and source-voucher restrictions. Implement read grid before writes.

Acceptance tests: wrong bank; duplicate marker; missing posting; debit/credit display; date filtering; concurrent mark; source unpost protection; reopen; totals; read-only register behavior.

Estimate: **4-7 working days**. Risks: no declared uniqueness/FK, absent statement header, and source vouchers may currently be deleted without reconciliation checks.
