# PDC Receivable dossier

## Purpose and evidence

Registers a post-dated cheque received from a customer or other party for future collection. The menu shows **PDC Receivable - Alt+R**. No current module or screen capture exists.

Status: **MISSING**.

## Candidate UI and lifecycle

Mapped fields mirror PDC Payable: voucher/date/numbering, party ledger, amount, cheque number/date, bank, narration, user/type/year. Allocation against customer invoices and deposit/clearance/dishonour states are `UNKNOWN`.

```text
register received PDC -> pending -> deposit/clearance
                      -> cleared OR returned/dishonoured (states UNKNOWN)
```

## Data and relationships

- Instrument: `tbl_PDCReceivableMaster`.
- Clearance: `tbl_PDCClearanceMaster` through candidate `againstId`/`type`.
- Party/bank accounts: `tbl_AccountLedger`; `ledgerId` and `bankId` roles require proof.
- Allocation/posting: candidate `tbl_PartyBalance`, `tbl_LedgerPosting`.
- Numbering/period: voucher type, suffix, financial year.

No generated FKs or visible unique cheque constraint establish these relationships.

## Procedures and target code flow

All PDC Receivable procedures are `UNKNOWN`. Target `/pdc-receivables` module must preserve instrument identity and integrate with Receipt/open-item logic only where legacy behavior proves it.

## Safety rules

- Confirm whether invoice allocation occurs when received or only when cleared.
- Prevent duplicate cheque registration and double clearance.
- Keep "received," "deposited," "cleared," and "customer invoice settled" as separate concepts unless evidence combines them.
- Reject delete/unpost after downstream clearance; reverse atomically when supported.

## Implementation and tests

Trace registration, allocation, deposit, clearance, return, replacement, and reversal examples, including ledger/party state at each stage.

Acceptance tests: duplicate cheque; invalid customer/bank; over-allocation; partial allocation; double clear; returned cheque reopening receivable; concurrent clearance; closed period; rollback.

Estimate: **5-8 working days**. Risks are premature invoice settlement and unclear bank ownership semantics.
