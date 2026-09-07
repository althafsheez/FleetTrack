# Current state audit

## Latest implementation — portal authentication

FleetTrack now has backend authentication against existing `VT_ApplicationUsers` portal accounts. Read-only MSSQL inspection confirmed status `1` is Active, status `2` is Inactive, and all 13 stored password values use a 47-character hyphenated 16-byte digest representation. The compatibility verifier recognizes that legacy MD5 representation without returning or logging stored values. This is legacy compatibility, not a recommendation for new password storage.

`POST /auth/login` validates an active portal user and sets a signed, HTTP-only session cookie; `GET /auth/me` returns the safe current-user projection; `POST /auth/logout` clears the cookie. Customer, supplier, lookup, vehicle, tariff and contract routers now require the cookie. Roles and permissions are not implemented; every authenticated active portal user has the same MVP access. `AUTH_SECRET` must be supplied with at least 32 characters, with session lifetime and secure-cookie behavior configurable through environment variables.

Verification: five isolated authentication tests pass for active/inactive/invalid credentials, strict legacy digest handling, signed-session round trip, expiry, tampering, login cookie/current-user recovery and logout clearing. The five isolated contract regression tests still pass. Python compile and OpenAPI checks pass, and OpenAPI shows the three auth paths plus the cookie dependency on business APIs. Live MSSQL aggregate reads confirmed the status labels and password representation without exposing credentials. A successful live login remains UNKNOWN until an approved user supplies their password through the login endpoint.

## Latest implementation — Contract view list/search

View Contracts now has a backend-only `GET /contracts/view` endpoint for the reference grid. It reads `VT_ContractMaster`, `VT_ContractVehicleMaster`, and `VT_Veh_VehicleMaster`, supports optional `customerName`, `agreementNo`, and `vehicle` filters, and returns one frontend-ready row per matched contract vehicle assignment with agreement number, customer, date out/in, total days, rate, vehicle, rent, Salik, fine, received, and pending amount.

The demo calculation is intentionally simple and visible-grid based: `rent = Rate * totalDays`, `salik = SalikCharges`, `fine = TrafficCharges`, `received = Advance`, and `pendingAmount = rent + salik + fine - received`. This does not replace the later invoice/receipt posting workflow.

Verification: the isolated SQLite contract test suite passes, including the new grid-row/search regression test; OpenAPI exposes `/contracts/view` with the expected query parameters; a live read-only MSSQL service check returned the expected frontend response shape. No live MSSQL writes were performed.

## Previous implementation — Contract agreement create

Contract Agreement Add now has a backend-only `POST /contracts/` create endpoint. It inserts `VT_ContractMaster`, `VT_ContractDriverDtls`, and `VT_ContractVehicleMaster` in one transaction, using confirmed MVP rules: UI-supplied integer `ContractRefNo`, `RTACode=ContractRefNo`, `PaymentType=ContractType`, `PaymentMode` for Security/Cash, `BillingType=2` Date to Date, `Status=8` OPEN, `ContractVehicleStatus=10` ACTIVE, no vehicle-master status change, customer ledger ID fields copied into contract/driver passport fields for now, and `OtherCharges` for Acc Charges. `VT_ContractDriverDtls` also has backend CRUD routes under `/contracts/drivers`; `/lookups/customer-users` now reads previous driver rows from that table joined to `VT_ContractMaster` by contract and customer.

Contract-specific lookups were added for contract types, customer lookup, customer users from prior contract usernames, application/checkout users, sales persons, payment modes, discount types, billing types, visa types, license types, nationalities, fuel levels, customer types, confirmation refs, and contract statuses. See [API.md](API.md) for exact paths and source tables.

Verification: 4 isolated SQLite contract service tests pass; app OpenAPI exposes `POST /contracts/`, contract driver CRUD routes, and the new lookups; live MSSQL read-only checks passed for representative new lookup queries including EZhire customer user `322384 - MOHAMED TASHRIQ` from `VT_ContractDriverDtls`. No live MSSQL contract write was performed. The installed TestClient/httpx path hangs even for a toy FastAPI app, so the older full TestClient API suite was not rerun successfully in this environment.

## Previous implementation — Vehicle and tariff APIs

The user approved backend implementation after the analysis below. Vehicles now have registered CRUD/search APIs; tariff-group names have CRUD/search, and the existing group row has a separate rate read/initialize/update API. Insurance types now have a lookup endpoint. Existing type 3 is preserved on unchanged vehicle edits. See [API.md](API.md) for contracts, defaults and deletion guards.

Verification: 9 isolated SQLite API tests pass; live MSSQL read-only checks return 121 vehicles and 13 groups, including Fleet No 34 with InsuranceTypeId=3. Live MSSQL writes remain UNKNOWN; frontend remains MISSING. The earlier syntax/import defects below are repaired. Generated mappings, schema, existing business records and dependencies were not changed. No commit/push.

## Historical pre-implementation audit

Audit date: 2026-09-06. Branch: `mvp`, tracking `origin/mvp`. Initial working tree: clean. Evidence: local source inspection and Python AST parsing only. No application module was executed and no database connection or endpoint call was made. The user reports the backend is running; endpoint behavior remains independently unverified.

## Status definitions

- WORKING: verified behavior with recorded evidence and test scope.
- PARTIAL: incomplete implementation is visible; does not imply any endpoint has passed runtime testing.
- MISSING: no implementation found in this repository, even if corresponding database mappings exist.
- UNKNOWN: runtime or business behavior has not been verified.

No application feature is labeled WORKING by this audit.

## Structure before documentation additions

```text
FleetTrack/
├── .gitignore
├── README.md
├── .agents/ and .codex/ (environment metadata directories)
└── FleetTrack Backend/
    ├── requirements.txt
    ├── test_connection.py
    └── app/
        ├── __init__.py
        ├── main.py
        ├── database/{__init__.py,session.py}
        ├── generated_models/models.py
        ├── customers/{__init__.py,router.py,schemas.py,service.py,repository.py}
        ├── suppliers/{router.py,schemas.py,service.py,repository.py}
        ├── lookups/{router.py,service.py,repository.py}
        └── vehicles/{router.py,schemas.py,service.py,repository.py}
```

No tracked frontend, migration suite, CI configuration, or endpoint test suite was found. `test_connection.py` is a standalone database probe, not a regression suite. New root `AGENTS.md`, `docs/`, and `reference/` provide context without moving application files.

## Modules and registration

| Capability | Status | Source evidence / limits |
| --- | --- | --- |
| Root health message | UNKNOWN | `app/main.py` defines GET `/`; returns a fixed message without testing MSSQL. |
| Customers CRUD/search | UNKNOWN | Router, schemas, service, repository exist; router is registered. Filters `TblAccountLedger.accountGroupId == 26`. |
| Suppliers CRUD/search | UNKNOWN | Same layers, registered; account group 22. |
| Lookups | UNKNOWN | 18 registered GET routes, pass-through services and generated-model queries. No dedicated response schemas. |
| Vehicles | PARTIAL | Schemas and unfinished repository only; router/service empty and not registered. |
| Tariff management/calculation | PARTIAL | Tariff-group lookup exists; generated rates and customer tariffs exist. No dedicated pricing service or write API. Runtime UNKNOWN. |
| Contract, checkout, active rental, check-in | MISSING | Generated tables contain candidate data; no application workflow code/routes. |
| Fine/Salik handling | MISSING | Generated fine/toll mappings only; no import/allocation/billing API. |
| Invoice, receipt, registers | MISSING | Generated accounting/staging mappings only; no application implementation. |
| Frontend | MISSING | No frontend project found. |
| Authentication/authorization | MISSING | No application auth dependency/middleware found; generated user tables do not implement access control. Demo needs UNKNOWN. |

Complete route inventory: [API.md](API.md).

## Existing behavior worth preserving

Customers and suppliers share `TblAccountLedger`, with group-specific filtering on list, ID lookup, and search; creation assigns the respective group. Create/update uppercases `ledgerName`. Search supports optional name and mobile substring filters, combined when both supplied. Get/update/delete return 404 when the group-scoped record is absent. Request schemas require a name (1–200 chars), mobile (at least 10 chars), and emirate ID (1–7); email uses `EmailStr`. These are existing application rules, not independently confirmed database/business requirements.

Customer schemas additionally expose credit terms, nationality, identification and expiry, and corporate status. Both modules update using full `model_dump()`: omitted optional fields default to None and can clear stored values. PUT requires name/mobile/emirate; it is not a PATCH contract. Repositories add/commit/refresh, or physically delete/commit. Preserve behavior while confirming whether deletion and clearing are acceptable for ledgers used by accounting.

Lookup chains in repository queries: state → plate category → plate code, and make → model → engine capacity. Other GET lookups include types, fuel, transmission, colours, insurance policies/companies, TC numbers, tariff groups, company branches, locations, statuses. Existing queries should be preserved until discrepancies are resolved.

## Connection/session and generated models

`app/database/session.py` creates a synchronous SQLAlchemy engine using `mssql+pyodbc`, localhost port 1433, database `Balance`, ODBC Driver 18, `TrustServerCertificate=yes`, `pool_pre_ping=True`, and a 30-second connection timeout. Credentials are hard-coded; do not copy their values. `SessionLocal` disables autocommit and autoflush. `get_db()` yields a session and closes it in `finally`. Repositories own commits; no explicit exception-to-HTTP mapping or rollback handling is implemented in them. Session closure provides cleanup but is not a defined error contract.

`test_connection.py` duplicates connection configuration and executes `SELECT DB_NAME()` at module level. It was not imported or run. Generated mappings use SQLAlchemy `DeclarativeBase`, `Mapped` and `mapped_column`, plus Core `Table` objects for some tables/views. Customers/suppliers/lookups import these mappings directly. No schema creation call was found in the application files.

## Definite incomplete/broken code (static evidence)

- `app/vehicles/repository.py:43`: unfinished `def search_vehicle(db:Session , )` produces `SyntaxError: expected ':'` when parsed.
- Vehicle repository imports `Session` from `sqlacademy` instead of the SQLAlchemy ORM, and imports `VT_Veh_VehicleMaster`; the generated Python class is `VTVehVehicleMaster`.
- Vehicle router and service files are empty. `main.py` does not import/include them, explaining why this broken module need not prevent the registered backend from starting.
- Vehicle schemas define `Vehicle` twice. Fields `ModelID`/`EngineCapacityID` differ from mapped `ModelId`/`EngineCapacityId`; `VHType` is an int in schemas but a nullable string in the model. Direct dictionary-to-model creation would fail on the mismatched names once imports/syntax were fixed.
- Vehicle creation omits required mapped `LatestKmRdg` and creation/update audit fields without a service providing them. Some `Optional[...]` schema fields lack defaults and are still required inputs; intended behavior is unresolved.

## Risks and things to verify

- Most core transaction joins lack declared foreign keys in the generated snapshot. Two unusual vehicle/plate constraints conflict with intuitive naming; see [relationships](RELATIONSHIPS.md).
- Contract creation requires many non-null fields including actual end date before the rental finishes. Legacy default/sentinel conventions must be established, not invented.
- No runtime endpoint/query/serialization checks were run. Response schemas have no explicit `from_attributes` configuration; test actual FastAPI response handling before calling this a defect.
- Customer list imports repository function `get_all_customers` through the service namespace instead of using `get_all_customers_service`; it is valid due to the imported binding but bypasses that wrapper.
- No pagination, duplicate checks, or reference-aware deletion rules appear in customer/supplier repositories. Unhandled database failures may surface as server errors.
- Credentials are embedded in two source files. Future configuration work should remove that duplication; no credential or configuration changes were made here.
- Dependency file is UTF-16 with BOM, with pinned versions. Preserve it; installation/environment compatibility was not verified and no upgrade was attempted.
- Initial audit found no reference media. Three Vehicle screenshots were added in the subsequent analysis below. Status IDs, tariff precedence, allocation rules, voucher numbering, tax/rounding, and posting sequence remain unconfirmed.

## Verification performed

Parsed application Python sources with `ast.parse`, without imports, bytecode output, or database calls. The vehicle repository is the sole syntax failure found; other application Python files parse. This establishes syntax only, not import correctness or runtime functionality. Generated models parsed successfully and were not changed. Final documentation checks and Git status verify this task only adds context files.

## Vehicle feature preparation — 2026-09-06

Analysis/documentation only, on existing `mvp`. Previously created AGENTS/docs/reference files remain untracked; they were preserved. Three source screenshots were copied unchanged to `reference/screenshots/vehicle/`. [Reference analysis](REFERENCE_APP.md) and [Vehicle feature analysis](features/VEHICLE_ANALYSIS.md) now describe the master, group-name, and group-rate screens. No feature is newly runtime-verified.

Reinspection confirms:

- `vehicles/router.py` and `vehicles/service.py` are 0 bytes. No `/vehicles` endpoints are registered in main.py.
- Repository drafts: `get_all_vehicles`, `get_vehicle_by_id`, `create_vehicle`, `update_vehicle`, `delete_vehicle`, and unfinished `search_vehicle`. AST parsing still fails at line 43. `sqlacademy` and `VT_Veh_VehicleMaster` imports are wrong. These defects are documented, not repaired.
- `VehicleCreate` and `VehicleUpdate` exist; `Vehicle` is defined twice. ModelID/EngineCapacityID casing and VHType type differ from generated mapping. Optional-typed fields without defaults remain required. Create omits LatestKmRdg and audit values required by the mapping. No service fills them.
- All 18 lookup routes have repository/service implementations in source, including GET `/lookups/tariff-groups`, which queries the full generated group model. None was called during this task. There are no dedicated tariff-name writes, tariff-rate writes, explicit lookup response schemas or vehicle UI.
- Relevant existing query behavior to preserve: state/category/code and make/model/capacity filters, master lookup retrieval, customer/supplier routes, session lifecycle, and generated names/types. `.distinct()` on full lookup rows does not establish label uniqueness.
- Screens add UI evidence but expose unresolved Fleet No, policy-adjacent input, InsuranceTypeId, Emirate/category, status, narration/location and create-default questions.

Vehicle Master, Vehicle Tariff Group and Vehicle Group Tariff are each NEEDS CONFIRMATION for the full feature including writes. Read-only list/detail work is the least risky first implementation after approval; it does not establish write safety. See the operation-by-operation assessment and ordered plan in the feature analysis.


## Approved tariff API revision

Creating a group name now assigns its identity ID and initializes all 17 pricing values to 0.00 atomically. GET `/vehicle-tariff-groups/` lists all groups; GET `/vehicle-tariff-groups/search?q=...` searches names separately. Name and rate updates use PATCH only; PUT was removed for tariffs. Get-by-ID and guarded delete remain. Existing database rows were not backfilled. Ten isolated API tests pass, including complete listing beyond 100 rows, automatic pricing initialization and removal of PUT.


Latest tariff correction: main get-by-ID/PATCH return all group fields and PATCH accepts name plus rates. Twelve isolated API tests pass, including full-field editing and scoped development CORS. Existing MSSQL values were not changed by testing.
