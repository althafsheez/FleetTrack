# Implemented FleetTrack APIs

## Portal authentication — 2026-09-07

Authentication uses existing `VT_ApplicationUsers` records, not the separate Balance Sheet ERP `tbl_User` records. Roles are out of scope; all active authenticated portal users currently have equal access.

| Method | Path | Behavior |
| --- | --- | --- |
| POST | `/auth/login` | Accepts `{username, password}`, verifies an active portal user and sets the signed `fleettrack_session` HTTP-only cookie. Returns `{user: {userId, userName, displayName}}`. |
| GET | `/auth/me` | Returns `{userId, userName, displayName}` for the current session; 401 when missing, invalid or expired. |
| POST | `/auth/logout` | Clears the browser session cookie and returns 204. |

All customer, supplier, lookup, vehicle, tariff and contract endpoints require the session cookie. Frontend cross-origin requests must use credentials. Local development must configure `AUTH_SECRET` with at least 32 characters; `AUTH_SESSION_TTL_SECONDS` defaults to eight hours and `AUTH_COOKIE_SECURE` must be true behind production HTTPS. The backend recognizes the portal's existing 47-character hyphenated MD5 digest representation strictly for legacy login compatibility. It never returns password fields. Registration, password changes/resets, roles, permission checks and server-side session revocation are not implemented.

## Contract agreement create and view — 2026-09-07

`POST /contracts/` creates a vehicle contract agreement from the Add screen. `GET /contracts/view` and `/contracts/view/page` list/search contracts for the Contract View register. `GET /contracts/{contract_id}` composes the legacy contract header with its first driver and vehicle-assignment snapshots. `PATCH /contracts/{contract_id}` updates the supported header, driver and handover fields in one transaction. `GET /contracts/{contract_id}/print-data` composes the deliberately limited values used by the approved two-page paper agreement. Customer and assigned-vehicle ownership are intentionally immutable in this MVP edit route. Contract delete, checkout transition, invoice posting and receipt posting remain unimplemented.

Create writes three rows in one transaction:

| DB table | Purpose |
| --- | --- |
| `VT_ContractMaster` | Contract header, customer snapshot, user/person text, rates/charges, payment/status/billing fields. |
| `VT_ContractDriverDtls` | Driver/user snapshot copied from the same submitted person fields. |
| `VT_ContractVehicleMaster` | Vehicle assignment/out row with `DatetimeOut`, `KmOut`, `FuelLevelIdOut`, `CheckedOutBy`, and `LocationOut`. |

Accepted rules: `ContractRefNo` is supplied by the UI as an integer and stored as text; `RTACode` is set to the same text; `PaymentType` is copied from `ContractType`; `PaymentMode` stores the Security/Cash selection; `BillingType` defaults to `2` (`Date to Date`); `Status` defaults to `8` (`OPEN`); `ContractVehicleStatus` defaults to `10` (`ACTIVE`); `DriverStatus` defaults to `16`; `OtherCharges` stores Acc Charges; vehicle master `StatusId` is not changed in this phase. `PassportNo` and `PassportExpiryDate` are populated from the selected customer ledger's `CustomerIdNo` and `CustomerIdExpiry` for now, and duplicated into both contract header and driver detail rows.

Contract driver detail endpoints:

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/contracts/view?customerName=...&agreementNo=...&vehicle=...&offset=0&limit=100` | List/search contracts for the View Contracts grid. Filters are optional and combine when supplied. Customer and vehicle use partial matching; agreement number uses exact matching. |
| GET | `/contracts/view/page?customerName=...&agreementNo=...&vehicle=...&offset=0&limit=10` | Additive paginated View Contracts response: `{items,total,offset,limit}` with the same combined-filter semantics. The array response above is preserved. |
| GET | `/contracts/{contract_id}` | Return `{contract,driver,vehicleAssignment}` for the full-record View/Edit drawer. |
| GET | `/contracts/{contract_id}/print-data?assignmentId=...` | Return the approved print projection for one exact contract-vehicle assignment. The assignment must belong to the contract. This endpoint is read-only. |
| PATCH | `/contracts/{contract_id}` | Update supplied MVP-safe contract, driver and handover fields. Requires `UpdatedBy`; customer and assigned vehicle cannot be changed. |
| GET | `/contracts/drivers/?contract_id=...&q=...` | List driver detail rows from `VT_ContractDriverDtls`, optionally scoped to one contract and filtered by username. |
| GET | `/contracts/drivers/{driver_id}` | Get one driver detail row by `ContractDriverId`. |
| POST | `/contracts/drivers/` | Add a driver detail row for an existing `VT_ContractMaster.ContractId`. |
| PATCH, PUT | `/contracts/drivers/{driver_id}` | Update supplied driver detail fields only. |
| DELETE | `/contracts/drivers/{driver_id}` | Delete one driver detail row. |

View Contracts response rows use frontend-oriented names: `slNo`, `contractId`, `assignmentId`, `agreementNo`, `customer`, `dateOut`, `dateIn`, `totalDays`, `rate`, `vehicleId`, `vehicle`, `rent`, `salik`, `fine`, `received`, and `pendingAmount`. `assignmentId` is `VT_ContractVehicleMaster.Id` and uniquely identifies each contract-vehicle history row; it is intentionally distinct from the contract and vehicle IDs. For the demo grid, rent is calculated as `Rate * totalDays`, Salik from `SalikCharges`, fine from `TrafficCharges`, received from `Advance`, and pending as the visible total less received.

The print projection populates only values visibly populated in the supplied legacy example: agreement number; hirer identification, nationality, birth/licence/contact fields; selected vehicle make/model/plate/colour; the one applicable contract rate; allowed kilometres; other charges; checkout date; and repeated hirer names on the checklist. Unrecorded inspection, signature, accident, passport-issue, email/address and card fields remain blank on paper. Rate placement is chosen from the contract-type label: monthly names populate Monthly Price, weekly names populate Weekly Price, and all other types populate Daily Price.

Additional lookup endpoints:

| Method | Path | Source |
| --- | --- | --- |
| GET | `/lookups/contract-types` | `tbl_VehicleContractType` |
| GET | `/lookups/customers?q=...` | Customer ledgers in `tbl_AccountLedger` group 26 |
| GET | `/lookups/customer-users?customer_id=...&q=...` | Prior driver rows in `VT_ContractDriverDtls`, joined through `VT_ContractMaster.CustomerId` |
| GET | `/lookups/users` and `/lookups/application-users` | `VT_ApplicationUsers`, for application/checkout users |
| GET | `/lookups/sales-persons` | `tbl_Employee` |
| GET | `/lookups/payment-modes` | `tbl_PaymentMode` |
| GET | `/lookups/discount-types` | `VT_DiscountType` |
| GET | `/lookups/billing-types` | `tbl_SalesInvoiceBillingType` |
| GET | `/lookups/visa-types` | `VT_VisaType` |
| GET | `/lookups/license-types` | `VT_DLTypes` |
| GET | `/lookups/nationalities` | `VT_Nationality` |
| GET | `/lookups/fuel-levels` | `VT_Veh_FuelLevelMaster` |
| GET | `/lookups/customer-types` | `VT_LookupTable` rows where `LookupType='CustomerType'` |
| GET | `/lookups/confirmation-ref-types` | `VT_LookupTable` rows for corporate/individual confirmation refs |
| GET | `/lookups/contract-statuses` | `VT_StatusMaster` rows where `StatusTypeId=2` |

Verification: isolated SQLite contract service tests pass for header/driver/vehicle inserts, reference validation, customer ID copying, View Contracts grid rows/search filters, driver CRUD and no vehicle status mutation. OpenAPI exposes the create/list/detail/update routes, driver CRUD and lookup routes. Live MSSQL read-only checks passed for the paginated register and a composed contract detail response, and the authenticated frontend rendered both View and Edit drawers from that data. No live MSSQL contract write was performed, so PATCH runtime behavior remains UNKNOWN against MSSQL.

---

# Implemented Vehicle and Tariff APIs — 2026-09-06

These endpoints now supersede the earlier proposals below for this slice. Backend only; generated models and MSSQL schema are unchanged. Vehicle search and edits use actual column casing, including ModelId, EngineCapacityId and string VHType (Fleet No). No Emirate/Make columns were added: use the existing state/category/plate-code and make/model/capacity lookups.

| Method | Path | Behavior |
| --- | --- | --- |
| GET | `/vehicles/page` | Paginated list/search envelope. Supports the same optional `q`, `plate_no`, and `fleet_no` filters plus `offset=0` and `limit=10` (maximum 100). Returns `{items, total, offset, limit}` ordered by VehicleId. |
| GET | `/vehicles/`, `/vehicles/search` | List/search; optional `q` matches plate/fleet/chassis/engine, `plate_no`, `fleet_no`; filters combine; literal wildcard escaping; `offset=0`, `limit=100` (maximum 500); ordered by VehicleId. |
| GET | `/vehicles/{vehicle_id}` | Full persisted fields, including unchanged legacy insurance IDs. |
| POST | `/vehicles/` | Create; returns 201 and full record. See VehicleCreate in OpenAPI for required master/date fields. |
| PATCH, PUT | `/vehicles/{vehicle_id}` | Both apply supplied fields only; require LastUpdatedBy. Omitted fields remain unchanged. Explicit null allowed only for nullable fields. |
| DELETE | `/vehicles/{vehicle_id}` | Physical delete of an unreferenced record; 204 success, 404 missing, 409 candidate history/accounting reference or DB constraint. No cascade. |
| GET, POST | `/vehicle-tariff-groups/` | List all names without pagination; create from TariffGroupName, assign identity ID and initialize all 17 rates to 0.00 atomically; returns 201. |
| GET | `/vehicle-tariff-groups/search?q=...` | Search group names by literal substring, ordered by ID. |
| GET, PATCH, DELETE | `/vehicle-tariff-groups/{group_id}` | Full detail (ID, name and all 17 pricing fields), partial update, or delete. PATCH accepts name and/or pricing fields; omitted values stay unchanged. Delete rejects vehicle references. |
| GET, PATCH | `/vehicle-tariff-groups/{group_id}/rates` | Read/initialize/update 17 pricing values on the existing group row. Missing group returns 404; create its name first. PATCH changes supplied fields only. |
| GET | `/lookups/insurance-types` | Existing insurance-type master rows; legacy type 3 is not invented as a lookup row. |

Responses: validation errors 422; missing records 404; known constraint/reference conflicts 409; other database failures 503 with sanitized details. The additive `/vehicles/page` endpoint is the total-count envelope for the frontend; the older vehicle list/search responses remain JSON arrays. Tariff-group list/search return all matches. Existing customer/supplier/lookup response contracts were preserved.

### Vehicle write rules

Create requires the mapped non-null fields and a caller-supplied positive CreatedBy; it requires StatusId and InsuranceTypeId explicitly rather than guessing them. InsurancePolicyRecNo defaults to 0. LatestKmRdg defaults to InitialKmRdg when omitted/null. Server assigns UTC-naive CreatedDate/LastUpdatedDate and initially copies CreatedBy to LastUpdatedBy. PUT/PATCH require LastUpdatedBy; creator/creation timestamp/primary key cannot be edited through these schemas. Audit IDs are supplied by the caller, not authenticated identities; this repository still has no authentication layer.

VHType accepts a string (preferred to preserve leading zeros), or an integer converted to text. New/changed lookup IDs must exist, including model/capacity consistency and both existing generated fuel-capacity-unit FK targets. Unchanged legacy references are preserved even if resent: InsuranceTypeId=3 on an existing type-3 vehicle is retained. Creating a new type-3 association is rejected because no lookup row exists. Nulling required fields or sending unknown fields is rejected.

Example update:

```json
{"Remarks": "Updated vehicle notes", "LastUpdatedBy": 7}
```

The audit ID is an example; callers must provide their actual approved actor value. StatusId remains explicit master data; no rental transition or automatic availability workflow is implemented.

### Tariff write rules

Group-name input is nonblank, trimmed, maximum 100 characters. No unconfirmed global uniqueness rule was invented; existing schema constraints remain authoritative. Name creation accepts no pricing fields; the main group PATCH accepts the optional name plus any of the 17 pricing fields. Group creation initializes all 17 rates to 0.00 in the same row/transaction. Existing rows are not backfilled. PATCH rates edits supplied values; omitted values stay unchanged, explicit null clears that value. All 17 accept finite Decimal values fitting DECIMAL(18,2); extra fields and excessive precision are rejected. Decimal responses are serialized as strings. No unconfirmed percentage bounds, nonnegative rule, currency, calculation or contract repricing behavior was added.

```json
{"DailyRate": "110.00", "WeeklyRate": "660.00", "ExtraKmCharges": "0.30"}
```

### Deletion limits

Vehicle delete checks mapped candidate VehicleId/vehicle references, staging invoice vehicle IDs, replacement taking/giving IDs and legacy history/accounting tables. Group delete checks mapped TariffGroupId references. These are deliberately conservative guards, not proof of every legacy business relationship. They do not add foreign keys or cascades, inspect undocumented procedures, or provide cross-application referential guarantees where MSSQL has no FK. Concurrent external writers and string-based legacy associations still require operational care.

### Verification

12 isolated SQLite API regression tests passed for CRUD/search, validation, rate/name independence, nullable updates, rollback and reference conflicts, and preserving insurance type 3. Live read-only endpoint checks passed for all 121 vehicles, search/detail of Fleet No 34, 13 groups, group/rate detail, insurance types and the existing group lookup. No live write request or MSSQL schema change was made; MSSQL-specific insert/update/delete behavior and triggers remain unverified. Existing generated ORM overlap warnings appear on legacy ORM lookup paths; models were not altered to silence them.

Run from the backend directory: `venv/bin/python -m unittest discover -s tests -v`. OpenAPI at `/docs` provides the complete payload schemas.

---

# Earlier inventory and proposals (historical)

Evidence: route decorators and `app/main.py` registration, inspected 2026-09-06. EXISTING means registered in source, not runtime verified. PARTIAL means unfinished code. PROPOSED means a future design suggestion, not implemented or an approved business contract. Paths preserve existing trailing slashes and parameter names.

## EXISTING endpoints (runtime UNKNOWN)

| Method | Path | Behavior / request |
| --- | --- | --- |
| GET | `/` | Fixed `{"message": "Backend is running!"}`; no database probe. |
| GET | `/customers/search` | Optional `name` and `mobile` query filters, AND when both supplied. |
| GET | `/customers/` | List group-scoped ledgers; no pagination. |
| GET | /customers/page | Paginated customer list. Query: offset (default 0) and limit (default 10; 1–100). Returns items, total, offset, and limit, ordered by ledger ID. |
| GET | /customers/search/page | Paginated customer search. Supports the same name/mobile filters plus offset and limit; response has the same page envelope. |
| GET | `/customers/{customerId}` | Get group-scoped ID; 404 when absent. |
| POST | `/customers/` | Create via CustomerCreate; uppercase ledgerName. |
| PUT | `/customers/{customerId}` | Full update schema; name/mobile/emirateId required; absent optional fields become None; 404 when absent. |
| DELETE | `/customers/{customerId}` | Physical delete; 404 when absent; success message. |
| GET | `/suppliers/search` | Optional `name` and `mobile` query filters, AND when both supplied. |
| GET | `/suppliers/` | List group-scoped ledgers; no pagination. |
| GET | `/suppliers/{supplierId}` | Get group-scoped ID; 404 when absent. |
| POST | `/suppliers/` | Create via SupplierCreate; uppercase ledgerName. |
| PUT | `/suppliers/{supplierId}` | Full update schema; name/mobile/emirateId required; absent optional fields become None; 404 when absent. |
| DELETE | `/suppliers/{supplierId}` | Physical delete; 404 when absent; success message. |
| GET | `/lookups/states` | No query parameters. |
| GET | `/lookups/plate-categories` | Required integer query: `state_id`. |
| GET | `/lookups/plate-codes` | Required integer query: `plate_category_id`. |
| GET | `/lookups/makes` | No query parameters. |
| GET | `/lookups/models` | Required integer query: `make_id`. |
| GET | `/lookups/engine-capacities` | Required integer query: `model_id`. |
| GET | `/lookups/vehicle-types` | No query parameters. |
| GET | `/lookups/fuel-types` | No query parameters. |
| GET | `/lookups/fuel-capacity-units` | No query parameters. |
| GET | `/lookups/transmission-types` | No query parameters. |
| GET | `/lookups/colours` | No query parameters. |
| GET | `/lookups/insurance-policies` | No query parameters. |
| GET | `/lookups/insurance-companies` | No query parameters. |
| GET | `/lookups/tc-nos` | No query parameters. |
| GET | `/lookups/tariff-groups` | No query parameters. |
| GET | `/lookups/company-branches` | No query parameters. |
| GET | `/lookups/locations` | No query parameters. |
| GET | `/lookups/statuses` | No query parameters. |

Customer and supplier POST/PUT use their module's Pydantic schemas; name length 1–200, mobile minimum length 10, emirateId 1–7, and optional validated email. Customer fields additionally include credit terms, nationality and identity data. Responses expose ledger IDs and details. POST has no explicit status code override (FastAPI default 200). Missing required parameters/schema validation use framework validation; exact response behavior remains untested. Database failures have no tailored error handling. All routes are synchronous and no auth dependencies were found.

FastAPI also normally exposes generated `/openapi.json`, `/docs`, and `/redoc` with this default constructor; these are framework-provided routes, not custom application features, and were not requested at runtime.

## PARTIAL: vehicles and tariffs

No vehicle endpoint is registered or defined: router/service files are empty, and the repository does not parse. CRUD-shaped functions and schemas are drafts only. Tariff group retrieval is an EXISTING lookup; dedicated tariff management/calculation is absent.

## Proposed MVP APIs

All paths below are PROPOSED; none is implemented by this task. Confirm resource names, payloads, statuses, IDs and business rules before implementation. Reuse existing customer/lookup APIs instead of duplicating them.

| Method | Proposed path | Purpose / prerequisite |
| --- | --- | --- |
| GET, POST | `/vehicles/` | List/filter and create fleet master records once mapping/required fields are verified. |
| GET, PUT | `/vehicles/{vehicleId}` | Detail/update; exact writable fields TBD. |
| GET | `/vehicles/available` | Selection for requested rental dates; predicate/status/overlap rules TBD. |
| GET | `/tariffs/` | Applicable pricing sources; reconcile group/customer tariffs. |
| GET | `/tariffs/{tariffId}` | Detail after choosing authoritative tariff identity. |
| POST, PUT | `/tariffs/`, `/tariffs/{tariffId}` | Tariff master maintenance if approved demo requires it; avoid guessing target table. |
| GET, POST | `/contracts/` | List/create contract with confirmed joins, numbering, required fields and atomic writes. |
| GET | `/contracts/{contractId}` | Detail including confirmed assignment/status/pricing. |
| POST | `/contracts/{contractId}/checkout` | Verified handover transition. |
| GET | `/rentals/active` | Active rental register/list; exact state definition TBD. |
| GET, POST | `/contracts/{contractId}/fines` | Review/record allocated fines; source/matching method TBD. |
| GET, POST | `/contracts/{contractId}/salik` | Review/record allocated tolls; source/deduplication TBD. |
| POST | `/contracts/{contractId}/check-in` | Verified return/closure transition and agreed charges. |
| POST | `/contracts/{contractId}/invoices` | Generate invoice using confirmed accounting/posting workflow. |
| GET | `/invoices/{invoiceId}` | Invoice details and lines. |
| POST | `/receipts/` | Record payment and verified allocations; settlement model TBD. |
| GET | `/receipts/{receiptId}` | Receipt detail and allocation evidence. |
| GET | `/registers/sales-invoices`, `/registers/receipts` | Requested registers; date/customer filters and totals TBD. |

Additional lookup GETs may be needed for insurance type, fuel level, contract/status/payment types, emirates, nationality, tax, voucher numbering and financial year. Add only those required by verified screens and data rules. Do not infer foreign keys or legal state transitions from these proposed URLs.


Tariff revision: only PATCH is supported for name/rate edits (PUT returns 405). A new name automatically creates its pricing state; no second create request is needed. Database identity TariffGroupId is the stable record key, not a guaranteed consecutive display serial number; UI row numbering can be computed from the list. Creation still accepts the object `{"TariffGroupName": "MG5"}`.


### Full group editing and CORS

GET `/vehicle-tariff-groups/{group_id}` and its PATCH response now return all 19 mapped fields: identity, name and 17 pricing values. PATCH can change any supplied name/pricing field together; TariffGroupId is read-only. Name may be omitted but cannot be null or blank. Dedicated `/rates` endpoints remain supported. Creation still zero-initializes pricing and list/search still return names and IDs.

CORS allows explicit localhost/127.0.0.1 origins on ports 3000 and 8000. Set comma-separated `CORS_ORIGINS` for other frontend origins and restart the backend. Same-origin Swagger requests do not need CORS; the previously limited response schema was a separate issue. The reported browser error's precise cause was not reproduced. Regression tests verify full group get/edit, allowed-origin GET/preflight and blocked unlisted origins. No production wildcard origin was added.
