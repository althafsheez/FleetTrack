# Traffic Fine dossier

## Purpose and evidence

Maintains imported or manually recorded vehicle traffic fines and supports billing eligible fines to the rental responsible at the fine time. The menu shows **Traffic Fine** with a submenu indicator; submenu entries and shortcut were not visible. No Traffic Fine management screen capture exists.

Status: **MISSING as management UI/API; PARTIAL as Sales Invoice source / MVP REQUIRED**.

## Candidate UI and lifecycle

Mapped fields support ticket number, vehicle, traffic file, fine date/time, authority, plate details, amount, black points, description, acknowledgment, download date, paid state, voucher number, invoice remarks, and posted state. Which are editable, imported, or authority-owned is `UNKNOWN`.

```text
import/enter fine -> match registered vehicle -> unbilled review
                  -> match contract assignment at FINEDATETIME
                  -> select for Fine Invoice -> posted/billed
                  -> optional payment-to-authority lifecycle (UNKNOWN)
```

## Data map and relationships

| Role | Table |
| --- | --- |
| Fine source | `Traffic_Fine`; PK is `TICKETNO`, while `Id` is identity but not PK. |
| Vehicle | `VT_Veh_VehicleMaster`; candidate join `VEHICLEID` -> `VehicleId`. |
| Responsible rental | `VT_ContractVehicleMaster`; candidate window `DatetimeOut <= FINEDATETIME <= DatetimeIn`, with open assignment handling. |
| Contract/customer | `VT_ContractMaster` through assignment `ContractId`. |
| Invoice | `tbl_SalesMaster`/details for voucher type 33 and Fine item types. |
| Revenue/tax | Sales account, item type, tax and voucher-tax tables. |

These relationships are not declared FKs. A fine can arrive after check-in, so "active contract now" is not a valid allocation rule.

## Procedures and current code flow

Traffic Fine import/add/edit/delete/payment procedures are `UNKNOWN`. Current read path is:

`GET /sales-invoices/sources/fines?contractId=...` -> Sales Invoice service -> repository joins candidate fine/vehicle/assignment data -> invoice-source lines.

Current code filters `ISPOSTED == false` and matches assignment identity, but the complete date-window, multi-ticket source link, and race-safe consumption behavior require verification before posting.

## Side effects and controls

- Ticket number is the stable source identity; never key billing by the non-PK identity alone.
- Duplicate billing needs both a pre-check and an atomic source claim/post operation.
- `ISPOSTED` likely means invoice consumption in current invoice logic, but its exact meaning versus authority payment is `UNKNOWN`.
- `PAID` likely represents authority settlement; do not map it to customer receipt without evidence.
- Service/administration charge, taxability, markup, and acknowledgment handling must come from verified item/tax rules.
- Unposting must release only the exact tickets belonging to that invoice.

## Implementation and tests

1. Capture submenu/screens and discover import/CRUD/post procedures.
2. Prove the vehicle and assignment-date matching rule with late-arriving and replacement-vehicle examples.
3. Introduce an evidence-backed source-to-invoice link using existing fields/tables only; if no safe representation exists, keep multi-fine posting blocked.
4. Add unbilled/assigned/billed/paid registers and Fine Invoice selection.

Acceptance tests: duplicate ticket; unknown vehicle; overlapping assignments; open assignment; boundary date/time; late fine; multiple fines per invoice; concurrent billing; invoice rollback/unpost; separate customer billing and authority payment states.

Estimate: **4-7 days** for management and allocation after procedure/source-link rules are proven, excluding generic Sales Invoice posting.

Risks: overloaded `ISPOSTED`, missing declared relationships, delayed fine arrival, and no clearly mapped many-to-many invoice-source table.
