# View Contracts dossier

## Purpose and evidence

Searches rental agreements and exposes operational totals, details, edit, and print actions. The supplied Transactions menu shows **View Contracts** with no shortcut. A current frontend screen and live read-only API behavior have been verified for representative data.

Status: **SUBSTANTIALLY IMPLEMENTED / MVP REQUIRED**. Remaining work is correctness hardening and replacement of provisional financial calculations with authoritative invoice/receipt totals.

## Current UI flow

Frontend `/contracts/list` provides combined customer, exact agreement, and vehicle filters; paginated results; view/edit drawers; and print. Visible columns are agreement, customer, out/in dates, days, rate, vehicle, rent, Salik, fine, received, and pending. Actions use the contract ID plus exact assignment ID.

Current flow:

```text
open register -> filter/page -> select assignment -> view or edit contract
              -> print exact assignment
```

The current totals are demo projections: rent is rate times days, Salik/Fine come from contract header charge fields, received comes from `Advance`, and pending is computed from those values. They are not a proven receivables balance.

## Data map and relationships

| Role | Source |
| --- | --- |
| Header/customer/rate | `VT_ContractMaster` |
| Assignment and out/in readings | `VT_ContractVehicleMaster` |
| Driver | `VT_ContractDriverDtls` |
| Vehicle display | `VT_Veh_VehicleMaster` plus make/model/plate/colour lookups |
| Authoritative billed totals | Candidate `tbl_SalesMaster`/details; final aggregation rule `UNKNOWN` |
| Authoritative receipts/balance | Candidate `tbl_ReceiptMaster`, `tbl_PartyBalance`; rule `UNKNOWN` |
| Fine/Salik exposure | `Traffic_Fine`, `Salik_Toll`; assignment-window rule requires final verification |

Assignment `ContractId` -> contract and assignment `VehicleId` -> vehicle are confirmed current query joins but are not declared transaction-table FKs in the generated snapshot.

## Procedures and code flow

No View Contracts stored procedure is verified. Current flow is:

`GET /contracts/view/page` -> router -> service -> repository joins/filters -> paginated projection -> frontend table.

Compatibility array endpoint `GET /contracts/view` remains. Detail, update, print-data, and PDF endpoints are described in [Contract Agreement](CONTRACT_AGREEMENT.md).

## Side effects, failure rules, and implementation

The register is read-only. View and print must never mutate contract, assignment, or invoice state. Edit uses Contract Agreement rules and must reject customer/vehicle reassignment.

1. Preserve filter combination, literal matching, stable ordering, total counts, and assignment identity.
2. Replace provisional rent/received/pending calculations only after Sales Invoice and Receipt Voucher relationships are verified.
3. Add explicit status and billing-position columns once authoritative predicates exist.
4. Keep one row per assignment; do not collapse replacement/history rows into one contract row.
5. Add links to checkout, check-in, charges, invoices, and receipts only when each command is operational.

Acceptance tests: multiple assignments for one contract; no assignment; exact agreement filtering; escaped wildcard text; empty/last page; invalid assignment print; totals from multiple invoices/receipts; no write during view/print; desktop/mobile overflow.

Estimate: **1-3 days** for current defect hardening; **2-4 additional days** after authoritative billing/allocation rules exist.

Risks: computed current totals can be mistaken for accounting balances; assignment history can duplicate contract rows; old data may have missing joins.
