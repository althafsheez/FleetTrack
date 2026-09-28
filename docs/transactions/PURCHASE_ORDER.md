# Purchase Order dossier

## Purpose and evidence

Records a non-accounting commitment to buy goods/services, potentially for a specific vehicle, and can source a later Purchase Invoice. The menu shows **Purchase Order - Shift+F9**. No current module or screen capture exists.

Status: **MISSING / OUTSIDE RENTAL MVP**.

## Candidate UI and lifecycle

Mapped fields support voucher/date/numbering, supplier ledger, due date, cancellation, employee, narration, total, exchange rate, financial year, and detail description/vehicle/quantity/rate/unit/amount. Product identity does not appear in order details, so free-text ordering may be intentional.

```text
new -> select supplier/date/due date -> enter item/vehicle lines
    -> save/approve behavior UNKNOWN -> open order
    -> partially/fully invoice or cancel (quantities/status UNKNOWN)
```

Approval, delivery, partial fulfillment, closure, print, and conversion behavior are `UNKNOWN`.

## Data and relationships

- Header: `tbl_PurchaseOrderMaster`.
- Lines: `tbl_PurchaseOrderDetails`.
- Supplier: `tbl_AccountLedger`, with supplier group/filter to verify.
- Employee/unit/vehicle: `tbl_Employee`, `tbl_Unit`, `VT_Veh_VehicleMaster`.
- Numbering/currency/period: voucher type, suffix, exchange rate, financial year.
- Downstream invoice: `tbl_PurchaseMaster.purchaseOrderMasterId` and `tbl_PurchaseDetails.orderDetailsId` candidate links.

No generated FK protects these relationships. There is no mapped posted flag; whether an order creates ledger postings should be treated as **no** unless procedures prove otherwise.

## Procedures and target code flow

Order add/edit/delete/cancel/approve/register/print/conversion procedures are `UNKNOWN`. Target `/purchase-orders` module provides list/detail/lookups/draft CRUD, explicit cancel, and print. Do not expose post/unpost unless verified.

## Safety and state rules

- Supplier, vehicle, unit, quantities, rates, and calculated totals must be validated.
- Cancellation must preserve history and block new invoice conversion while retaining existing conversions.
- Prevent invoicing beyond ordered quantity/amount under the verified tolerance rule.
- Concurrent invoice creation must lock/re-read remaining quantities.
- Edits to partially invoiced orders require explicit verified restrictions.

## Implementation and tests

Capture create/edit/print/cancel and partial/full conversion examples. Inspect how remaining quantity and order status are derived without explicit mapped fields.

Acceptance tests: invalid supplier/unit/vehicle; zero/negative quantity/rate; total rounding; duplicate number; partial/multiple invoice conversion; over-invoice; cancelled conversion; edit after conversion; rollback; pagination/filtering.

Estimate: **5-8 working days** after procedures and conversion rules are known. Risks are no explicit line product ID, no explicit status except `cancelled`, and no mapped remaining quantity.
