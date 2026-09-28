# Contract Agreement dossier

## Purpose and evidence

Creates and maintains the rental agreement joining a customer, driver snapshot, vehicle assignment, dates, tariff/charges, payment settings, and billing schedule. The supplied Transactions menu shows **Contract Agreement** with a submenu indicator; no shortcut or submenu contents were visible. The detailed legacy screen was not captured.

Status: **PARTIAL / MVP REQUIRED**. Current backend and frontend support create, detail, edit, driver CRUD, print, and optional initial Monthly/Lease Rental Invoice draft. Checkout/check-in are not separate implemented commands.

## UI and state flow

Current frontend `/contracts` contains customer/driver/vehicle selection, contract dates/type/location, identity and licence fields, charge inputs, payment/discount/billing settings, handover fields, optional advance Rental Invoice settings, summary, save, clear, and cancel. `/contracts/list` opens view/edit drawers and print.

Proposed state flow, pending authoritative status confirmation:

```text
new form -> validate references -> save contract + driver + assignment
         -> optional initial rental draft -> OPEN contract
OPEN -> checkout command -> ACTIVE rental -> check-in command -> CLOSED
```

`OPEN=8`, assignment `ACTIVE=10`, and driver status `16` are current accepted creation values from earlier live investigation. Their wider transition meanings remain `UNKNOWN`.

## Data map

| Role | Table | Important columns |
| --- | --- | --- |
| Header/customer/pricing | `VT_ContractMaster` | `ContractId`, `ContractRefNo`, customer snapshot/`CustomerId`, dates, type, rate/charges, payment/billing, status, invoice flags, next/last invoice dates. |
| Driver snapshot | `VT_ContractDriverDtls` | `ContractDriverId`, `ContractId`, identity/licence/contact/status fields. |
| Vehicle assignment/handover | `VT_ContractVehicleMaster` | `Id`, `ContractId`, `VehicleId`, status, out/in date-time, km, fuel, actor and location fields. |
| Attachments | `VT_ContractDocuments` | Contract-linked document metadata; current application use is MISSING. |
| Lookups | Customer ledger, vehicle, contract/status/type, location, employee, payment/discount/billing, nationality/visa/licence/fuel | Exact filters are described in `docs/API.md`. |
| Optional initial invoice | `tbl_SalesMaster`, `tbl_SalesDetails`, `tbl_SalesBillTax` | Created only through rental billing when requested. |

No transaction-table foreign keys are declared in the generated snapshot. `ContractId` and `VehicleId` joins are application-level candidates already used by current code, not database-enforced guarantees.

## Procedures and code flow

No Contract Agreement stored procedure is verified. Current code persists through SQLAlchemy repositories:

`POST /contracts/` -> contracts router -> service validation/orchestration -> contract repository inserts -> optional rental billing service -> `dbo.SalesMasterAdd` for initial invoice -> commit/rollback.

Other current APIs: `GET/PATCH /contracts/{id}`, driver CRUD, `GET /contracts/{id}/print-data`, and `GET /contracts/{id}/print.pdf`. Current implementation is under `app/contracts`, `app/rental_billing`, frontend `/contracts`, `/contracts/list`, and `/contracts/[contractId]/print`.

## Side effects and transaction rules

- Contract header, initial driver, and assignment must save atomically.
- Optional initial invoice and schedule changes must be in the same transaction as creation.
- Customer and vehicle references are validated; current update intentionally does not change them.
- Creation currently does not change vehicle master status. Checkout ownership of vehicle status is `UNKNOWN`.
- Numbering ownership for `ContractRefNo`/`RTACode` is currently caller-driven; authoritative concurrency behavior is `UNKNOWN`.
- Delete/cancel behavior, overlap prevention, document handling, and status reversals are `UNKNOWN`.

## Implementation and tests

1. Inspect approved legacy screen/submenu and read-only procedures/triggers; confirm numbering, required fields, status transitions, cancellation, and overlap rules.
2. Stabilize create/detail/edit/print and ensure all current response fields reflect persisted values.
3. Add explicit checkout and check-in commands rather than broad status PATCH operations.
4. Add active-rental predicate, conflict handling, and vehicle availability transition only after status IDs are proven.
5. Add attachment support only if required for the demo.

Acceptance tests: invalid references; date ordering; duplicate/overlapping assignment; atomic rollback at each insert; optional invoice rollback; immutable identity/audit fields; checkout/check-in replay; print assignment ownership; and live read-only comparison to an approved complete agreement.

Estimate after unknowns are resolved: **3-5 days** to stabilize existing Contract Agreement behavior; checkout/check-in are estimated separately in the rental workflow.

Risks: status IDs are weakly constrained, contract tables duplicate customer/driver data, and many joins lack FKs. Do not normalize or backfill them during application work.
