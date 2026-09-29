# PDC Payable dossier

## Purpose and evidence

Registers a post-dated cheque issued by the business for future payment. The menu shows **PDC Payable - Alt+P**. No current module or screen capture exists.

Status: **MISSING**.

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

PDC Payable add/edit/delete/post/register and clearance procedures are `UNKNOWN`. Target `/pdc-payables` module should expose register/detail/draft commands and lifecycle actions only after the posting point and statuses are proven.

## Safety rules

- Validate verified bank and payee/control ledgers.
- Define cheque-number uniqueness scope: bank/account/date/status.
- Prevent a single instrument from being cleared twice or cleared after cancellation.
- Registration, party allocation, and later clearance must preserve one stable instrument ID.
- Unpost/delete must reject cleared instruments and reverse all earlier effects atomically where supported.

## Implementation and tests

Trace issue, edit, due, clearance, cancellation, dishonour, reissue, post, and unpost examples. Compare ledger/party rows both before and after clearance.

Acceptance tests: duplicate cheque; past/future date rules; invalid bank/payee; amount mismatch; double clearance; cancellation/clearance race; closed period; rollback; register filters.

Estimate: **4-7 working days** after lifecycle evidence. Main risk is posting at the wrong lifecycle stage.
