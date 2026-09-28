# Vehicle Finance dossier

## Purpose and evidence

Records financed acquisition of a vehicle/asset and its installment cheque schedule. The menu shows **Vehicle Finance** with no shortcut. Existing Sales Invoice evidence explicitly distinguishes Vehicle Finance from Vehicle Invoice.

Status: **MISSING / OUTSIDE RENTAL MVP**.

## Candidate UI and lifecycle

Mapped header fields support finance number/date, purchase master/detail, asset, financier ledger, purchased/loan/monthly amounts, installment count, bank, starting cheque number/date, narration, creator, and posted state. Detail rows store installment number, PDC ID, bank, amount, cheque number/date, paid state, and audit values.

```text
select purchased vehicle/asset -> enter loan terms -> generate/review installments
-> save/post finance -> register installments -> clear/pay through verified PDC/payment flow
```

Interest, balloon payment, first/last installment rounding, early settlement, reschedule, and asset ownership are `UNKNOWN`.

## Data and relationships

- Finance header: `tbl_FinanceHeader`.
- Installments: `tbl_FinanceDetail`.
- Purchase source: `tbl_PurchaseMaster`, `tbl_PurchaseDetails`.
- Asset/vehicle: header `assetID`; authoritative target table `UNKNOWN`.
- PDC link: detail `PDCId`, likely payable instrument; not FK-confirmed.
- Financier/bank: `tbl_AccountLedger` via `ledgerId`/`bankId`.
- Accounting: `tbl_LedgerPosting`, `tbl_PartyBalance` candidates.

No generated FKs enforce header/detail, purchase, asset, PDC, or ledger links.

## Procedures and target code flow

Finance creation/schedule/post/payment/reversal procedures are `UNKNOWN`. Target `/vehicle-finance` module depends on verified Purchase Invoice and PDC Payable semantics; it must not generate instruments independently with incompatible rules.

## Accounting and safety rules

- Purchase and asset detail must be valid, unique, and eligible for financing.
- `purchasedAmount`, `loanAmount`, monthly amount, installment count, and schedule sum need a proven reconciliation formula.
- Schedule generation must be deterministic and idempotent.
- Posting point for liability/loan and linkage to purchase liability must be verified.
- `isPaid` must be driven by a verified payment/clearance event, not a free toggle.
- Posted finance with issued/cleared PDCs cannot be casually edited or deleted.

## Implementation and tests

Trace one active/completed finance agreement from Purchase Invoice through schedule, PDC generation, installment payment, and ledger rows. Capture reschedule/early settlement if used.

Acceptance tests: invalid/duplicate asset; financed amount limits; installment rounding; schedule count/dates; duplicate cheque/PDC; post retry; payment state; unpost with paid installment; rollback.

Estimate: **8-12 working days** after Purchase and PDC modules. Risks are compounding dependencies and an unresolved `assetID` target.
