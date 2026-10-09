# PDC Payable dossier

## Purpose and evidence

Registers a post-dated cheque issued by the business for future payment. The menu shows **PDC Payable - Alt+P**. No current module or screen capture exists.

Status: **BACKEND AND FRONTEND IMPLEMENTED**.

Current `/pdc-payables` APIs provide register/detail/print, all-account lookup and search, open-reference lookup, and atomic create/update/delete. The visible Account Ledger is unrestricted. Every new PDC currently requires one or more Against references chosen in the nested allocation window; they must belong to one party account and exactly equal the cheque amount. Save creates balanced ledger postings and `tbl_PartyBalance` Against rows. On Account creation is intentionally deferred. Clearance is handled by `/pdc-clearances`.

## Candidate UI and lifecycle

Mapped fields support voucher/date/numbering, payee ledger, amount, cheque number/date, bank, narration, user/type/year. Counterparty allocation, cheque status, printing, replacement, cancellation, and dishonour controls are not represented directly and remain `UNKNOWN`.

```text
register issued PDC -> pending -> clearance/due processing
                    -> cleared OR cancelled/dishonoured (states UNKNOWN)
```

## Data and relationships

- Instrument: `tbl_PDCPayableMaster`.
- Clearance: `tbl_PDCClearanceMaster` candidate `againstId` plus `type`.
- Bank/payee accounts: `tbl_AccountLedger`; meaning of header `ledgerId` versus `bankId` must be confirmed.
- Accounting/open item: `tbl_LedgerPosting`, `tbl_PartyBalance`; whether registration or clearance posts is `UNKNOWN`.
- Numbering/period: voucher type, suffix/prefix, financial year.

No generated FKs enforce these joins or prevent duplicate cheque numbers.

## Procedures and target code flow

Live inspection confirmed the legacy add/edit/delete/register/report/print/reference procedures. They remain evidence rather than application calls because the add procedure inserts only the master and does not atomically create postings and allocations.

## Safety rules

- Validate existing Account Ledger, Against party ledger, bank ledger, and the exact source references.
- Define cheque-number uniqueness scope: bank/account/date/status.
- Prevent a single instrument from being cleared twice or cleared after cancellation.
- Registration, Against allocation, and later clearance preserve one stable instrument ID.
- Unpost/delete must reject cleared instruments and reverse all earlier effects atomically where supported.

## Implementation and tests

Trace issue, edit, due, clearance, cancellation, dishonour, reissue, post, and unpost examples. Compare ledger/party rows both before and after clearance.

Acceptance tests: duplicate cheque; past/future date rules; invalid bank/payee; amount mismatch; double clearance; cancellation/clearance race; closed period; rollback; register filters.

Estimate: **4-7 working days** after lifecycle evidence. Main risk is posting at the wrong lifecycle stage.
