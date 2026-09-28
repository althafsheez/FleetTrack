# Current state audit

## Latest implementation — Receipt Voucher backend

Receipt Voucher now has an authenticated FastAPI backend implemented directly against the existing MSSQL tables through SQLAlchemy. No application stored procedure is called, and no generated model, schema, procedure, constraint, lookup, or master-data record was changed. The module provides a paginated Receipt Register, stable detail/print projection, voucher/account/party/AED-rate/numbering/contract lookups, open-reference lookup, draft create/update/delete, and explicit post/unpost commands.

Draft save writes `tbl_ReceiptMaster` with `isPosted=0`, its `tbl_ReceiptDetails`, and bill-by-bill allocations in `tbl_PartyBalance_Unposted`; it does not create ledger postings. Posting locks and revalidates each Against reference, debits the receiving cash/bank account, credits each detail ledger, creates matching active allocation credits in `tbl_PartyBalance`, verifies the exact expected posting count and balanced totals, then marks the master posted. Posted records cannot be edited or deleted. Unpost is blocked when another allocation consumes the Receipt credit or any posting is bank-reconciled; otherwise it preserves or restores the unposted allocation mirror before removing active allocations and postings.

The first release supports `Against` and `On Account` allocations and AED at rate `1.00000`. `New` and foreign-currency Receipt behavior remain blocked because they were not proved by active Receipt data. Cash Receipt rejects cheque fields; Cheque Receipt requires cheque number and date. Bill-by-bill allocations are allowed only for verified Sundry Debtor/Creditor party ledgers, must total their detail line, cannot exceed the current open balance, and may retain a verified contract on On Account entries. Automatic numbering requires a date-valid rule and is serialized under an MSSQL update/hold lock at creation.

Verification: all 21 focused Receipt Voucher tests pass, the combined Contra/Payment/Receipt suite passes all 53 tests, Python compilation passes, and all 16 Receipt routes are registered. Read-only live MSSQL verification returned 3,721 register rows, active Receipt subtypes, and the AED rate. A Party Balance detail query was narrowed to the Receipt's detail ledgers after the first live attempt exposed a broad scan; final detail re-verification could not be completed because the local MSSQL connection subsequently timed out. No Receipt create, update, post, unpost, or delete was submitted against live data, so controlled write behavior remains **UNKNOWN** pending explicit approval. The full legacy test discovery run reached its older integration section and stopped producing progress; it was terminated without a Receipt failure.

## Latest implementation — Payment Voucher backend and frontend

Payment Voucher now has an authenticated backend and Next.js screen implemented against the existing MSSQL tables. No application stored procedure is called and no generated model, schema, procedure, lookup, or master-data row was changed. The backend provides a paginated register, detail/print projection, voucher/account/currency/vehicle/numbering lookups, open party references, draft create/update/delete, and explicit post/unpost commands. The register supports inclusive date ranges, voucher number, voucher type, paying account, exact amount, party ledger, partial cheque number, posted status, and pagination. Party and cheque filters use correlated existence checks rather than detail joins, preventing duplicate master rows. Register rows include their detail-account names and line counts.

The `/payment-vouchers` frontend follows the existing Contra visual system. It provides the register and all verified filters, a modal create/edit workflow, per-line searchable account pickers, currency/cheque/vehicle inputs, nested `Against`/`New`/`On Account` bill allocation, draft save/update/delete, explicit post/unpost, posted read-only behavior, and browser printing. The account results render through a page-level portal so table and modal overflow cannot clip them; the picker remains anchored to its field, flips upward when needed, and closes on selection, outside click, Escape, resize, or outer scrolling. Duplicate detail accounts are removed from later pickers, the line action remains visible during horizontal scrolling, deleting the final line clears it, and Add Line stays disabled until every current line is complete. The paying-account selector shows the account group but intentionally does not force subtype-specific filtering: historical read-only data proves Bank and Cash Payment types have both used Bank Account and Cash-in Hand sources, while no verified Credit Card source group exists.

Drafts persist `tbl_PaymentMaster` with `isPosted=0`, `tbl_PaymentDetails`, and bill allocations in `tbl_PartyBalance_Unposted`; they create no ledger postings. Posting locks and revalidates each selected open reference, credits the paying cash/bank account, debits detail ledgers, creates Forex Gain/Loss entries through the verified ledger `12` when required, creates active `tbl_PartyBalance` allocations, verifies balanced totals, and sets `isPosted=1` last. Posted vouchers cannot be edited or deleted. Unpost is blocked when a later posted/draft allocation references the payment or when any posting is bank-reconciled; otherwise it preserves a draft allocation set before reversing active accounting effects.

Validation covers active Payment Voucher types, financial year, automatic/manual numbering, eligible Cash-in Hand/Bank Account/Bank OD source ledgers, existing detail ledgers and vehicles, date-valid exchange rates, positive Decimal amounts, unique detail ledgers/references, complete cheque fields, bill-by-bill Sundry Creditor/Debtor eligibility, party-line/allocation equality, pending-balance limits, currency agreement, idempotency, owned update identities, and atomic rollback. Final numbers are serialized under a SQL Server update/hold lock. Credit Card grouping, vehicle reporting semantics, and controlled foreign-currency `New`/`OnAccount` examples remain unresolved and are not invented.

Verification: fifteen focused Payment Voucher tests pass, and the combined Contra/Payment suite passes all 32 tests. Edited frontend files pass ESLint; the payment files add no TypeScript errors, while the full repository check remains blocked by pre-existing Contract print and Customer typing errors. The register, editor, and bill-allocation dialog were visually verified at desktop width with controlled mock reads. Live read-only MSSQL checks previously confirmed three active Payment Voucher types, three eligible paying ledgers, party-ledger classification, date-valid currency lookup, two open references for the controlled ledger, 2,275 register rows, posted detail projection, an existing unposted voucher with four draft allocations, and the pending-reference lock query. The extended register filters have not yet been exercised against the live MSSQL service. No live Payment Voucher write, post, unpost, or delete was submitted by Codex, so live write behavior remains **UNKNOWN** pending a user-controlled test.

## Latest implementation — Contra Voucher backend and frontend

Contra Voucher now has authenticated list, detail, create, update, delete, lookup, numbering-rule, and print-data endpoints. The paginated register supports inclusive date-only ranges, partial voucher-number search, header cash/bank account and direction filters, and returns detail-account names and line counts without per-row queries. The implementation uses direct SQLAlchemy reads/writes against the existing `tbl_ContraMaster`, `tbl_ContraDetails`, and `tbl_LedgerPosting` tables; no application stored procedure is called and no generated model, schema, procedure, lookup, or master-data row was changed.

The Next.js `/contra-vouchers` screen now provides the approved blue, compact register and modal create/edit workflow. It includes live filtering and pagination, date-aware numbering and exchange-rate lookups, eligible-account selection, multi-line amounts and cheque fields, update/delete actions, and browser printing. Shared API errors preserve structured negative-balance information: `Warn` shows the affected accounts and allows an explicit confirmed retry, while `Block` remains non-overridable.

Saving is the posting action. Deposit debits the selected header cash/bank account and credits the detail accounts; Withdrawal performs the opposite. Foreign amounts are converted with trusted date-valid `tbl_ExchangeRate` values, totals are server-calculated to five decimals, and each operation commits the complete master/detail/balancing-posting set once or rolls it back. Update verifies detail ownership and reconciles removed, retained, and new lines. Delete removes only postings with the voucher's type/number before its details and header. Optional idempotency keys support safe create retries, and SQL Server row locking serializes automatic numbering without a stored-procedure call.

Validation covers active Contra voucher configuration, automatic/manual numbering, optional suffix rules with a plain-number fallback, financial-year membership, verified `Cash-in Hand`/`Bank Account`/`Bank OD A/C` group eligibility, header/detail account separation, positive amounts/rates, bank-only cheque fields, posting balance, and the `NegativeCashTransaction` Warn/Block/Ignore setting. Live inspection proved `ViewCashBank` is unsuitable here because it includes `Sundry Debtors` and excludes `Bank Account`, so Contra does not use that view. `tbl_FinancialYearMonthStatus.isEnabled` is not treated as an open/closed flag because that meaning is unverified. There are no post/unpost endpoints because the verified legacy lifecycle posts on save.

Verification: seventeen focused Contra tests pass, including structured `Warn` and non-overridable `Block` negative-balance responses. Python compilation and targeted frontend TypeScript semantic checks pass. The authenticated route redirects correctly to login without a session; the register and create modal were visually verified with controlled mock reads at desktop width, with no write submitted. A live read-only register check previously returned 151 vouchers, populated line summaries, and confirmed that a combined same-day, voucher-number, header-account, and direction filter finds the expected record. Earlier read-only MSSQL checks confirmed Contra voucher type `3` uses Automatic numbering, financial year `3` covers 2026, AED exchange rate `1` is `1.00000`, Cash ledger `1` and ADCB ledger `138278` are valid accounts, and the negative-cash setting is `Warn`. Live create/update/delete, table hints, triggers, controlled rollback behavior, and authenticated browser integration against live MSSQL remain **UNKNOWN**. No live business data was written by Codex.

## Latest implementation — Rental Invoice drafts

Rental Invoice creation now follows the verified legacy contract schedule without changing SQL Server schema, procedures, lookups, or master data. A Monthly or Lease contract can create its first advance Rental Invoice draft atomically with its contract, driver, and vehicle-assignment rows when `initialRentalInvoice` supplies the selected sales account, exchange rate, credit period, and optional LPO number. Lease contracts persist the existing Monthly payment type. Daily and Weekly contracts reject advance billing; Daily final billing remains deferred to check-in.

The new contract-aware endpoints are `POST /contracts/{contract_id}/rental-invoices/preview`, `POST /contracts/{contract_id}/rental-invoices`, `GET /rental-invoices/due`, and `DELETE /contracts/{contract_id}/rental-invoices/{sales_master_id}`. Weekly, Date-to-Date, and Month End periods calculate their next due dates independently. Draft creation locks the contract row, rejects inactive/not-due/duplicate requests, creates the existing sales header/detail/tax records through `dbo.SalesMasterAdd`, then advances `NextInvStDate` and records `LastInvoiceDate` in the same transaction. Only the latest unposted Rental Invoice draft can be deleted; it calls `dbo.SalesInvoiceDelete` and restores the prior schedule. Generic Sales Invoice create/update/delete routes reject Rental Invoice drafts, preventing schedule bypass.

Rental line values are derived from existing contract rate, discount, driver-charge, additional-driver, CDW, and PAI fields. Existing Rental Invoice item types, their configured tax, the existing `NOS` unit, financial year, numbering rule, location, selected sales account, and selected exchange rate are validated at request time; no IDs are hard-coded. Contract billing terms cannot be edited after any Rental Invoice exists, while expected-end-date extension remains available. Invoice posting, payment/receipt allocation, party balance, Active Rentals, check-in, contract close, Daily final billing, Fine/Salik billing, and print stay out of scope.

Verification: 23 isolated contract, sales-invoice, and rental-billing tests pass; Python compilation and generated OpenAPI route checks pass. A live read-only MSSQL query confirmed the current Rental Invoice voucher, numbering rule, financial year, `NOS` unit, and all configured rental item types. No live MSSQL write was submitted during verification. Live controlled draft create/delete remains UNKNOWN pending an approved test contract and sales settings.

Frontend follow-up: the Contract Add screen now exposes Monthly/Lease advance invoice settings for sales account, exchange rate, credit period, and LPO number, and sends `initialRentalInvoice` only when advance billing is enabled. A new `/rental-invoices` screen lists due rentals from `GET /rental-invoices/due`, previews the next draft through the contract-aware preview endpoint, creates rental drafts, deletes the latest visible unposted draft through the rental-billing delete endpoint, and shows a Rental-filtered Sales Invoice Register. A shared frontend API client was restored under `FleetTrack Frontend/src/lib/api.ts`; `.gitignore` now explicitly allows that source directory. Verification: `git diff --check` and a lightweight TypeScript transpilation parse of the edited TS/TSX files passed. Full frontend `tsc` and ESLint runs hung without diagnostics in this desktop environment and were stopped; browser/API runtime behavior remains UNKNOWN.

## Latest implementation — portal authentication

FleetTrack now has backend authentication against existing `VT_ApplicationUsers` portal accounts. Read-only MSSQL inspection confirmed status `1` is Active, status `2` is Inactive, and all 13 stored password values use a 47-character hyphenated 16-byte digest representation. The compatibility verifier recognizes that legacy MD5 representation without returning or logging stored values. This is legacy compatibility, not a recommendation for new password storage.

`POST /auth/login` validates an active portal user and sets a signed, HTTP-only session cookie; `GET /auth/me` returns the safe current-user projection; `POST /auth/logout` clears the cookie. Customer, supplier, lookup, vehicle, tariff and contract routers now require the cookie. Roles and permissions are not implemented; every authenticated active portal user has the same MVP access. `AUTH_SECRET` must be supplied with at least 32 characters, with session lifetime and secure-cookie behavior configurable through environment variables.

Verification: five isolated authentication tests pass for active/inactive/invalid credentials, strict legacy digest handling, signed-session round trip, expiry, tampering, login cookie/current-user recovery and logout clearing. The five isolated contract regression tests still pass. Python compile and OpenAPI checks pass, and OpenAPI shows the three auth paths plus the cookie dependency on business APIs. Live MSSQL aggregate reads confirmed the status labels and password representation without exposing credentials. A successful live login remains UNKNOWN until an approved user supplies their password through the login endpoint.

## Latest implementation — vehicle frontend integration and pagination

Vehicles now has an additive `/vehicles/page` API endpoint with `items`, `total`, `offset`, and `limit`; the existing array-based vehicle list/search endpoints are unchanged. The Next.js Vehicles page follows the approved Stitch-derived application shell and connects to the authenticated vehicle and lookup APIs. It supports general, plate, and fleet-number search; ten-row page traversal; left-sticky View/Edit controls; a full detail drawer; and Create/Edit forms across plate, technical, registration, insurance, and operating fields. Vehicle delete stays disabled in the frontend because it is a physical backend delete. The signed-in portal user ID supplies `CreatedBy`/`LastUpdatedBy`. Existing missing insurance-type ID 3 is visibly preserved as a legacy option when editing an affected record.

Verification: vehicle-module compile, frontend TypeScript check, and whitespace/diff check pass. The live browser preview confirmed the authenticated paginated endpoint returns 121 records, page traversal works, and the View/Create UI renders with live lookup data; no vehicle writes were submitted. Production `next build` could not be completed in this desktop execution environment because Turbopack's CSS worker cannot bind its internal port; this is an environment limitation, not a diagnosed application error.

## Latest implementation — shared frontend navigation

Dashboard, Customers, and Vehicles now use the same dashboard-derived `FleetSidebar` component. Its active state is inferred from the current route, and its working links connect the three implemented screens. Tariffs and Contracts remain visible but explicitly marked `Next` rather than routing to unimplemented screens. New frontend screens can reuse this component without duplicating navigation markup. Frontend TypeScript verification passes; Dashboard navigation was exercised in the live browser.

## Latest implementation — tariffs and contracts frontend

Tariffs now has a live Next.js master/detail screen: selecting a group displays its real values in a persistent read-only detail panel. The tariff-group master list uses frontend-only eight-row pagination while the existing API returns the full set. Create Tariff and Edit each open a separate right-side drawer with the group name and all 17 mapped rate fields, grouped into rental, discount, kilometre/fuel, CDW, and PAI sections. It uses only the tariff API fields; reference-only group codes and vehicle-count badges were deliberately omitted.

Contracts now has a rebuilt live Add Contract screen based on the approved Stitch reference. It groups the verified backend fields into Agreement & Customer, Primary Driver & Licence, Vehicle & Handover, and Rates/Charges/Settlement panels with a live frontend-only summary rail. Customer selection cascades to prior customer users and can prefill recorded driver data. All `ContractCreate` required fields and all twelve stored charge fields remain connected to the existing create API; customer identity/passport snapshots remain backend-derived.

The shared sidebar now exposes Add Contract and Contract View subheadings. Contract View is a separate live register with combinable customer/agreement/vehicle search, ten-row numbered pagination that retains the active filters, a sticky left action column and the complete reference-grid financial columns. Agreement number matching is exact; customer and vehicle matching remain partial. Each rendered assignment row uses the unique `VT_ContractVehicleMaster.Id` returned as `assignmentId`, so repeated vehicle history within one contract does not create duplicate React keys. View opens a grouped read-only right drawer; Edit opens the corresponding prefilled editable drawer and uses the additive contract detail/PATCH endpoints. Customer and assigned vehicle remain locked after creation.

Contract Print is now enabled from both a register row and the contract View drawer. It opens a dedicated two-page Letter-size preview modelled on the supplied Rental Agreement and Vehicle Check List PDF, then invokes the browser print dialog for physical printing or Save as PDF. The read-only print endpoint requires the selected `assignmentId`, verifies that it belongs to the contract, and joins vehicle/model/make/colour/plate/tariff/nationality data. Only the values populated in the approved legacy example are rendered; all other paper fields remain blank for manual completion.

Verification: all six isolated contract service tests pass, including selected-assignment print projection coverage. Contract Python compilation, frontend TypeScript and whitespace checks pass. The authenticated browser preview rendered live agreement `3366`, its correct vehicle assignment and both printable pages with no console errors. Each page measures exactly 816 x 1056 CSS pixels (8.5 x 11 inches at 96 DPI), with no internal overflow. Search checks still confirmed exact agreement `3366`, combined filters, empty partial agreement `366`, and filter retention across pagination. No contract create, update or delete was submitted during verification.

## Latest implementation — customer pagination and frontend integration

Customers now have additive paginated read endpoints, /customers/page and /customers/search/page. Both accept offset and limit (1–100), order by ledger ID, and return items, total, offset, and limit; the existing unpaginated list/search endpoints remain unchanged. The Next.js Customers screen uses these page endpoints for ten-row pages and name/mobile search, displays real returned data, puts View/Edit/Delete controls in a left sticky column, and uses approved Stitch-derived detail/add/edit drawers. Delete remains intentionally disabled in the frontend because the backend delete is a physical database deletion. Frontend build and backend customer-module compile checks pass. Live page/read/write behavior remains UNKNOWN until tested against the running backend; no customer records were created, updated, or deleted for verification.

## Latest implementation — Contract view list/search

View Contracts now has `GET /contracts/view` and paginated `GET /contracts/view/page` endpoints for the reference grid. They read `VT_ContractMaster`, `VT_ContractVehicleMaster`, and `VT_Veh_VehicleMaster`, support combinable optional `customerName`, exact `agreementNo`, and `vehicle` filters, and return one frontend-ready row per matched contract vehicle assignment. Every row includes `assignmentId` from the assignment table's primary key in addition to agreement number, customer, date out/in, total days, rate, vehicle, rent, Salik, fine, received, and pending amount.

The demo calculation is intentionally simple and visible-grid based: `rent = Rate * totalDays`, `salik = SalikCharges`, `fine = TrafficCharges`, `received = Advance`, and `pendingAmount = rent + salik + fine - received`. This does not replace the later invoice/receipt posting workflow.

Verification: source-level regression coverage includes assignment identity and exact agreement matching. In the current workspace, automated backend test execution is unavailable because the accessible Python runtime does not include the project's SQLAlchemy/pytest dependencies; Python compilation passes. Live read-only browser checks against the running backend confirmed the search and filtered-pagination behavior. No live MSSQL writes were performed.

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
