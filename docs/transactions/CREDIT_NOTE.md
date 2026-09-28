# Credit Note (Invoice) dossier

## Purpose and evidence

Records a customer/supplier credit adjustment and, where supported, applies it against an existing invoice. The menu label is **Credit Note (Invoice)** with no shortcut observed. The exact direction (sales credit, purchase credit, or generic accounting note) is not proven by the label or schema.

Status: **MISSING**.

## Candidate UI and lifecycle

Mapped fields support voucher/date/numbering, total/tax/narration, and a detail grid with ledger, debit, credit, exchange rate, and cheque fields. The source invoice selector, party field, tax breakdown, and return linkage are `UNKNOWN`.

```text
new -> select party/source invoice if required -> enter adjustment lines/tax
    -> save -> post -> apply/open credit -> optional unpost
```

## Data and relationships

- Header: `tbl_CreditNoteMaster`.
- Lines: `tbl_CreditNoteDetails`.
- Accounting/open item: `tbl_LedgerPosting`, `tbl_PartyBalance`.
- Candidate source invoices: `tbl_SalesMaster` and/or `tbl_PurchaseMaster`; direction `UNKNOWN`.
- Tax/lookup: `tbl_Tax`, account ledger/group, exchange rate, voucher type, suffix, financial year.

No source-document ID is visible in the mapped Credit Note tables; linkage may be stored through `tbl_PartyBalance`, free-text voucher fields, or procedures. This is a critical investigation gate.

## Procedures and target code flow

Credit Note add/edit/delete/post/unpost/allocation/register/print procedures are `UNKNOWN`. Target `/credit-notes` module must not select a sales-only or purchase-only contract until procedure and UI evidence settle the direction.

## Accounting and safety rules

- Confirm whether the note decreases customer receivable, decreases supplier payable, or supports both voucher types.
- Verify tax reversal calculation and control-ledger behavior.
- Prevent adjustment beyond original taxable/base balance unless an independent open credit is allowed.
- Preserve source invoice, applied/unapplied amount, and full reversal semantics through existing structures.
- Posted/allocated notes are immutable; unpost must detach allocations first or reject safely.

## Implementation and tests

Capture the screen and trace standalone/applied, full/partial, taxed/untaxed, post/unpost examples. Document the exact source identity representation before defining API payloads.

Acceptance tests: wrong document direction; over-credit; repeated application; tax rounding; closed/posted source; multi-currency; duplicate post; allocated unpost; balanced postings; rollback.

Estimate: **5-8 working days** after direction and procedures are known. Main risk is implementing the wrong business meaning from the ambiguous menu label.
