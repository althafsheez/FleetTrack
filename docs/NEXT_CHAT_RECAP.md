# FleetTrack next-chat recap

## Current app status

FleetTrack is a FastAPI backend MVP on branch `mvp`, using existing MSSQL database `Balance` as the source of truth. The database schema and generated SQLAlchemy models are treated as read-only. The current backend pattern is router -> service -> repository -> generated models/MSSQL.

There is no completed frontend yet. The intended frontend stack is Next.js, TypeScript, Tailwind CSS and shadcn/ui.

## Implemented backend areas

### Customers and suppliers

Existing customer and supplier CRUD/search routes are registered. Both use `tbl_AccountLedger` with group filtering:

- Customers: `accountGroupId = 26`
- Suppliers: `accountGroupId = 22`

These routes existed before the recent MVP work and should be preserved.

### Vehicles

Vehicle backend CRUD/search is implemented and registered:

- `GET /vehicles/`
- `GET /vehicles/search`
- `GET /vehicles/{vehicle_id}`
- `POST /vehicles/`
- `PATCH /vehicles/{vehicle_id}`
- `PUT /vehicles/{vehicle_id}`
- `DELETE /vehicles/{vehicle_id}`

Vehicle code uses actual DB fields from `VT_Veh_VehicleMaster`. Important rules:

- `VHType` is used for Fleet No and is treated as string.
- `LatestKmRdg` defaults from `InitialKmRdg` on create.
- Create/update requires caller-supplied audit user IDs.
- Vehicle delete is guarded against known candidate references.
- Existing `InsuranceTypeId = 3` can be preserved on existing records, but new type 3 associations are rejected if no lookup row exists.

### Tariff groups

Vehicle tariff group APIs are implemented:

- `GET /vehicle-tariff-groups/`
- `GET /vehicle-tariff-groups/search?q=...`
- `POST /vehicle-tariff-groups/`
- `GET /vehicle-tariff-groups/{group_id}`
- `PATCH /vehicle-tariff-groups/{group_id}`
- `DELETE /vehicle-tariff-groups/{group_id}`
- `GET /vehicle-tariff-groups/{group_id}/rates`
- `PATCH /vehicle-tariff-groups/{group_id}/rates`

Creating a tariff group initializes all pricing fields to `0.00`. PATCH supports name and/or rate edits. PUT is intentionally not supported for tariff edits.

### Contract Agreement Add

Phase 2 currently has backend create support for the Vehicle Contract Add screen:

- `POST /contracts/`

Create inserts these three DB tables in one transaction:

- `VT_ContractMaster`
- `VT_ContractDriverDtls`
- `VT_ContractVehicleMaster`

Confirmed MVP rules:

- `ContractRefNo` comes from UI as an integer but is stored as text.
- `RTACode = ContractRefNo`.
- `PaymentType = ContractType`.
- `PaymentMode` stores the Security/Cash selection.
- `BillingType = 2` means Date to Date and is the default.
- `Status = 8` means OPEN.
- `ContractVehicleStatus = 10`.
- `DriverStatus = 16`.
- Acc Charges maps to `OtherCharges`.
- Vehicle master `StatusId` is not changed for now.
- Customer ID No/Expiry is copied from the selected customer ledger into contract/driver passport fields for now.

### Contract driver details

Driver details CRUD is implemented for `VT_ContractDriverDtls`:

- `GET /contracts/drivers/?contract_id=...&q=...`
- `GET /contracts/drivers/{driver_id}`
- `POST /contracts/drivers/`
- `PATCH /contracts/drivers/{driver_id}`
- `PUT /contracts/drivers/{driver_id}`
- `DELETE /contracts/drivers/{driver_id}`

The main contract create endpoint also automatically creates the first driver row from the submitted contract person fields.

### Lookups

Existing vehicle/master lookups remain, and additional contract lookups were added:

- `/lookups/contract-types` -> `tbl_VehicleContractType`
- `/lookups/customers?q=...` -> customer ledgers in `tbl_AccountLedger`, group 26
- `/lookups/customer-users?customer_id=...&q=...` -> prior driver rows from `VT_ContractDriverDtls` joined to `VT_ContractMaster`
- `/lookups/users` and `/lookups/application-users` -> `VT_ApplicationUsers`
- `/lookups/sales-persons` -> `tbl_Employee`
- `/lookups/payment-modes` -> `tbl_PaymentMode`
- `/lookups/discount-types` -> `VT_DiscountType`
- `/lookups/billing-types` -> `tbl_SalesInvoiceBillingType`
- `/lookups/visa-types` -> `VT_VisaType`
- `/lookups/license-types` -> `VT_DLTypes`
- `/lookups/nationalities` -> `VT_Nationality`
- `/lookups/fuel-levels` -> `VT_Veh_FuelLevelMaster`
- `/lookups/customer-types` -> `VT_LookupTable`
- `/lookups/confirmation-ref-types` -> `VT_LookupTable`
- `/lookups/contract-statuses` -> `VT_StatusMaster`, `StatusTypeId = 2`

Live read-only check confirmed EZhire customer `138274` returns driver user `322384 - MOHAMED TASHRIQ` from `VT_ContractDriverDtls`.

## Manual testing notes

Swagger returning `201` means the contract was actually created. The response contains the new `ContractId`.

To find a created contract in MSSQL:

```sql
USE Balance;

SELECT *
FROM dbo.VT_ContractMaster
WHERE ContractId = <ContractId> OR ContractRefNo = '<ContractRefNo>' OR RTACode = '<ContractRefNo>';

SELECT *
FROM dbo.VT_ContractDriverDtls
WHERE ContractId = <ContractId>;

SELECT *
FROM dbo.VT_ContractVehicleMaster
WHERE ContractId = <ContractId>;
```

For latest rows:

```sql
SELECT TOP 1000 *
FROM dbo.VT_ContractMaster
ORDER BY ContractId DESC;
```

Important: in `VT_ContractVehicleMaster`, search by `ContractId`, not by `Id`.

## Verified so far

- Focused SQLite backend tests pass for vehicle/tariff work.
- Focused SQLite contract tests pass for contract header/driver/vehicle insert, lookup validation, driver CRUD and no vehicle master status mutation.
- Python compile checks passed for affected contract/lookup/main/test files.
- OpenAPI exposes contract create and driver CRUD routes.
- Live MSSQL read-only checks passed for representative lookup queries and for manually created contract rows.
- Live MSSQL writes were tested manually through Swagger by the user; created rows were found in all three contract tables.

Known test limitation: `fastapi.testclient`/httpx hangs in this environment even for a tiny one-route app, so full TestClient-based API tests were not used.

## Known gaps / not implemented yet

- No frontend screens yet.
- No contract list/detail endpoint for the contract header yet.
- No contract edit/delete endpoint for the contract header yet.
- No checkout transition logic beyond creating the initial vehicle assignment row.
- No active rental register.
- No check-in flow.
- No fines/Salik allocation flow.
- No invoice generation/posting.
- No receipt creation/allocation.
- No Sales Invoice Register or Receipt Register.
- No authentication/authorization layer.
- No confirmed accounting side effects.
- Contract status transitions need confirmation.
- Vehicle availability/overlap rules are not implemented.

## Recommended next steps

1. Add contract list/detail endpoints so created contracts can be searched and reopened from the UI.
2. Build the Contract Agreement Add frontend screen using the current lookups.
3. Add vehicle availability/search behavior for contract vehicle selection.
4. Confirm and implement checkout/status transition rules.
5. Implement Active Rental list.
6. Implement Check-in, then invoice and receipt flows.
7. Add Sales Invoice Register and Receipt Register after invoice/receipt writes are confirmed.

For the next chat: start by reading `AGENTS.md`, `docs/PROJECT.md`, `docs/CURRENT_STATE.md`, `docs/MVP_SCOPE.md`, `docs/API.md`, and this file.
