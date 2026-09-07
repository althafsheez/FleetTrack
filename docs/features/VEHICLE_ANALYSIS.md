# Vehicle feature analysis

**Implementation update:** The user subsequently approved backend implementation and requested preservation of legacy insurance type 3. Vehicle CRUD/search, group-name CRUD/search, rate read/initialize/update, and insurance-type lookup are now implemented. The content below records the earlier analysis and decisions; its approval gates are historical. See [API.md](../API.md) for the current contracts and verification limits.

Date: 2026-09-06. Branch: `mvp`. Scope: analysis/documentation only. Screenshots were copied without alteration; original files retained. Application source, generated models and dependencies are unchanged. No database calls, application imports, endpoint tests, frontend implementation, commit or push occurred.

## 1. Screenshot analysis

Three screens were inspected independently: [Vehicle Master](../../reference/screenshots/vehicle/vehicle-master.png), [Vehicle Tariff Group](../../reference/screenshots/vehicle/vehicle-tariff-group.png), and [Vehicle Group Tariff](../../reference/screenshots/vehicle/vehicle-group-tariff.png). The full field/control/required-marker inventory, actions, visual notes and uncertainties is in [REFERENCE_APP.md](../REFERENCE_APP.md). Browser/AnyDesk surrounds are capture context, not FleetTrack UI requirements.

| Screen | Observed sections / interaction affordances | CRUD limits |
| --- | --- | --- |
| Add Vehicle | Plate, make, registration, insurance, RTA/operational details; search/list at right; Update, Clear, Close. | Existing record appears selected; create suggested by title, not shown; no delete visible. |
| Tariff Group | Required group-name input, Details grid with serial/name columns; Save, Clear, dim Delete-looking button, Close. | Create suggested; list/select visible; rename/update behavior unknown; delete enablement unknown; no search. |
| Vehicle Group Tariff | Left group selection, 17 numeric-looking inputs, Update and Close. | Read/select/update visible; no create/delete/clear/search; no required markers. |

Example rate values are captured observations, not defaults or calculations. Blank Location with required marker and greyed ON CONTRACT status show why a screenshot cannot establish validation or editable fields.

## 2. Concrete feature list and workflow

| Feature | Purpose / inferred user workflow | Backend queries needed | Frontend state needed |
| --- | --- | --- | --- |
| Vehicle Master | List/search → select → view/edit → Update; new entry only after confirming create mode. | Paginated deterministic vehicle read; detail by PK; verified lookup joins/labels; parameterized search; future duplicate/reference checks and controlled insert/update. | Search text/results, selected VehicleId, form draft/original, lookup IDs/options, dependent selections, date values, dirty/loading/error state, read-only status, create/edit mode only if approved. |
| Vehicle Tariff Group | List groups → enter name/Save; select group for approved maintenance; Clear/Close. | List/detail; name collision check using confirmed case/whitespace rules; insert/name-only update; deletion reference query only after policy known. | Group list/selection, name draft, create/edit mode, dirty/validation/error/submitting state; delete availability based on server rules. |
| Vehicle Group Tariff | Select group → review/change 17 values → Update. | Read selected group/rates; update only allowed pricing columns, preserve group name and omitted values; concurrency policy TBD. | Selected TariffGroupId, Decimal-safe input strings, original/draft/null representation, dirty/errors/loading/saving and selection-change handling. |

No need to rebuild existing backend modules or implement rental calculation as part of merely editing tariff master values. Rate application to contracts is a separate confirmed-business-rules prerequisite if included later.

## 3. Existing backend mapping

Paths below are relative to `FleetTrack Backend/`.

| Component | What exists | Status |
| --- | --- | --- |
| `app/main.py` | Root, customers, suppliers, lookups registered. Vehicles not imported/registered. | Existing source; runtime UNKNOWN. |
| `app/vehicles/router.py`, `service.py` | Empty files, 0 bytes each. | MISSING implementation. |
| `app/vehicles/repository.py` | Draft get_all_vehicles, get_vehicle_by_id, create_vehicle, update_vehicle, delete_vehicle; incomplete search_vehicle. | PARTIAL; syntax failure at line 43, wrong sqlacademy import and generated class import. No method is currently usable through this module. |
| `app/vehicles/schemas.py` | VehicleCreate, VehicleUpdate, duplicate Vehicle response-like class. | PARTIAL; ModelID/EngineCapacityID casing differs; VHType int versus DB string; required Optional fields lack defaults. |
| Vehicle create/update persistence | Direct model_dump → model/setattr; per-operation commit/refresh; physical delete draft. | PARTIAL, no business validation, duplicate checks, safe deletion or audit initialization. Not verified. |
| `app/lookups/{router,service,repository}.py` | 18 GET routes with model queries and pass-through services, including group records/rates. | Implemented in source, runtime UNKNOWN; no explicit response schemas. |
| `app/database/session.py` | Synchronous pyodbc/MSSQL engine and yielded session with finally-close. | Existing source; this task made no connection. Hard-coded secret values omitted. |
| Dedicated tariff CRUD/rate APIs and schemas | None found. | MISSING. |
| Frontend / feature tests | None found for this slice. | MISSING. |

Preserve customer/supplier behavior, existing lookup endpoints/filter arguments and session pattern. Fix only the unfinished vehicle module when approved; keep generated mappings untouched. Draft methods are useful intent, not working functionality to claim. No feature is marked WORKING by this static audit.

## 4. Database mapping

Vehicle Master candidate: `VT_Veh_VehicleMaster` / `VTVehVehicleMaster`, integer identity PK `VehicleId`. Tariff group-name and rate screens both match `VT_Veh_TariffGroupMaster` / `VTVehTariffGroupMaster`, integer identity PK `TariffGroupId`. The latter stores required `TariffGroupName` and all 17 nullable DECIMAL(18,2) rate values in the same row. No separate tariff-rate entity is established.

| Section | Visible UI field | Control appearance | Required marker | Candidate persisted field / derivation | Evidence / uncertainty |
| --- | --- | --- | --- | --- | --- |
| Plate Details | Plate No | Text input | Yes | PlateNo | Direct field candidate; preserve as text, including leading zeros. |
| Plate Details | Emirate | Select | Yes | Derived / UNKNOWN | No EmirateId or StateId in VehicleMaster. State master versus tbl_Emirate and plate join must be resolved. |
| Plate Details | Plate Code | Select | Yes | PlateCodeId | FK to plate-code master; displayed code label versus Code column unknown. |
| Plate Details | Fleet No | Numeric-looking text input | No visible marker | UNKNOWN | No FleetNo column in VehicleMaster. Do not substitute VehicleId, VHType or FleetTypeId without evidence. |
| Make Details | Make | Select | Yes | Derived via ModelId → ModelMaster.MakeId | Make is not directly stored on VehicleMaster; FK chain exists. |
| Make Details | Model | Select | Yes | ModelId | Generated spelling differs from draft schema ModelID. |
| Make Details | Engine capacity | Select | Yes | EngineCapacityId | Lookup label is a string, not necessarily a numeric measurement; draft schema uses EngineCapacityID. |
| Make Details | Year of Manufacture | Select | Yes | Year | Integer column; year-option source/range unknown. |
| Make Details | Veh Type | Select | Yes | TypeId (candidate) | Type master has FK; selected body-style label supports this candidate. Do not confuse with string VHType. |
| Make Details | Veh Fuel Type | Select | Yes | FuelTypeId | No declared vehicle FK; candidate lookup. |
| Make Details | Veh Fuel Capacity — amount | Numeric-looking input | Yes, at combined row | FuelCapacity | Integer column, visible amount 50; accepted range unknown. |
| Make Details | Veh Fuel Capacity — unit | Select | Yes, at combined row | FuelCapacityUnitId | Displays LITRES. FK targets FuelCapUnitId AND FleetTypeId; requires investigation. |
| Make Details | Engine No | Text input | Yes | EngineNo | Identifier, not numeric quantity; duplicate policy unknown. |
| Make Details | Chasis No | Text input | Yes | ChasisNo | Retain existing DB spelling; UI concept is chassis number. |
| Make Details | Veh. Transmission | Select | Yes | TransmissionId | FK to transmission master; Automatic visible. |
| Make Details | Veh. Color | Select | Yes | ColourId | FK to colour master; WHITE visible. |
| Veh Registration Details | Reg Start Date | Date picker | Yes | RegistrationStartDate | Screenshot format dd/MM/yyyy; time/timezone semantics unknown. |
| Veh Registration Details | Reg Expiry Date | Date picker | Yes | RegistrationExpiryDate | Do not infer expiry validation/grace period from this frame. |
| Veh Insurance Details | Veh Ins Policy | Select | No clear marker | InsurancePolicyId | Policy master stores InsurancePolicyNo as text. |
| Veh Insurance Details | Unlabeled box beside policy (0) | Numeric-looking input; editability unknown | No clear marker | InsurancePolicyRecNo (suspected) | Could be record number or another concept; screenshot cannot identify meaning. |
| Veh Insurance Details | Veh Ins Company | Select | No clear marker | InsuranceCompanyId | Candidate company master; policy-company dependency not established. |
| Veh Insurance Details | Veh Ins Expiry Date | Date picker | Yes | InsuranceExpDate | Mapped NOT NULL; screen shows date only. |
| RTA Details / operational fields | Veh TC No | Select | Yes | TCNoId | TCNo master supplies string identifier. |
| RTA Details / operational fields | Salik Tag | Text input with numeric-looking value | No visible marker | SalikTag | Mapped string; keep identifier formatting. Does not establish toll allocation rule. |
| RTA Details / operational fields | Initial Km Rdg | Numeric-looking input | Yes | InitialKmRdg | LatestKmRdg is also required by DB but not visible. |
| RTA Details / operational fields | Veh. Tariff Group | Select | Yes | TariffGroupId | Business association visible; exact DB join has no declared FK. |
| RTA Details / operational fields | Branch | Select | Yes | BranchId | Candidate VT_Company_BranchMaster; no vehicle FK. |
| RTA Details / operational fields | Location | Select, empty in capture | Yes | LocId (suspected) | Candidate LocationId; cannot exclude legacy LocationToRemove without evidence. |
| RTA Details / operational fields | Veh. Status | Select-looking, greyed/read-only-looking | Yes | StatusId | ON CONTRACT visible; editability, status domain and ID unknown. |
| RTA Details / operational fields | Narration | Multiline text input | No visible marker | Remarks (suspected) | No Narration column on VehicleMaster. |
| Search panel | Search | Text input above scrollable list | No visible marker | Query only | No separate Search button shown; live filtering versus Enter/other trigger unknown. |

| Visible label | Candidate column in VTVehTariffGroupMaster | Example shown for selected MG5 |
| --- | --- | --- |
| Daily Rate | `DailyRate` | 110.00 |
| Weekly Rate | `WeeklyRate` | 660.00 |
| Monthly Rate | `MonthlyRate` | 2100.00 |
| Disc % Daily (per day) | `DiscountPercentPerDayDaily` | 0.00 |
| Disc % Daily (3 days) | `DiscountPercent3DaysDaily` | 0.00 |
| Disc % Daily (5 days) | `DiscountPercent5DaysDaily` | 0.00 |
| Disc % Weekly | `DiscountPercentWeekly` | 0.00 |
| Disc % Monthly | `DiscountPercentMonthly` | 0.00 |
| Fuel Charges | `FuelCharges` | 0.00 |
| Allowed Kms / day | `AllowedKmsPerDay` | 200.00 |
| Extra Km Charges | `ExtraKmCharges` | 0.30 |
| Daily CDW | `DailyCDW` | 25.00 |
| Weekly CDW | `WeeklyCDW` | 75.00 |
| Monthly CDW | `MonthlyCDW` | 250.00 |
| Daily PAI | `DailyPAI` | 0.00 |
| Weekly PAI | `WeeklyPAI` | 0.00 |
| Monthly PAI | `MonthlyPAI` | 0.00 |

The complete related table/model/PK/column/constraint catalogue is in [DATABASE.md](../DATABASE.md), Vehicle addendum. This is generated snapshot evidence, not a live-schema audit. No FleetNo column or direct vehicle Emirate/Make/Narration field exists. Required InsuranceTypeId/latest odometer/audit values are not represented by clear visible controls.

## 5. Required APIs (proposals only)

Reuse existing `/lookups/*` rather than duplicating them. New paths here refine the earlier generic [API proposals](../API.md); they are not registered contracts. PATCH is proposed to prevent accidental clearing of unedited nullable values; method choice and field names must be agreed before implementation.

| Capability | Proposed API | Query / guard |
| --- | --- | --- |
| Vehicle list/search | GET `/vehicles/` with optional `q`, limit, offset | Parameterized text search and stable ordering; plate/make/model search candidates. Fleet No search blocked until mapping known. Exact response shape TBD. |
| Vehicle detail | GET `/vehicles/{vehicleId}` | Read PK; return IDs plus agreed labels and preserve unresolved lookup values. 404 for absent ID. |
| Vehicle create | POST `/vehicles/` | Confirmed required fields, lookup references, identity generation, defaults/audit values and duplicate policy. |
| Vehicle update | PATCH `/vehicles/{vehicleId}` | Explicit writable-field allowlist, supplied fields only; protect status/operational/history-sensitive fields per confirmed policy. |
| Group read | Existing GET `/lookups/tariff-groups`; proposed GET `/vehicle-tariff-groups/{tariffGroupId}` | Existing full-model query may suffice for list; verify JSON/Decimal/null shapes before UI binding. |
| Group name create/update | POST `/vehicle-tariff-groups/`; PATCH `/vehicle-tariff-groups/{tariffGroupId}` | Name-only updates must preserve rates; uniqueness/default-rate policy TBD. |
| Rate read/update | GET and PATCH `/vehicle-tariff-groups/{tariffGroupId}/rates` | Same underlying group row, 17-field allowlist, Decimal/null rules; do not change name or unrelated data. |
| Missing lookup | Proposed GET `/lookups/insurance-types` | Needed if user must select required InsuranceTypeId; otherwise confirm legacy derivation. |
| Domain selection | Status-type/filter capability, exact API TBD | Do not expose all statuses as valid vehicle transitions. Existing GET statuses is unfiltered. |

Vehicle deletion is not shown and is not proposed for the first implementation. Group delete is a conditional future DELETE `/vehicle-tariff-groups/{tariffGroupId}` only after confirming the visible affordance and reference safeguards. Do not implement soft deletion without an existing suitable field and confirmed semantics. No new schema is proposed.

Future API verification must exercise lookup JSON shape, null/Decimal values, not-found and invalid input behavior, update preservation, database constraint errors and any permitted writes with approved test records. Read-only list/detail implementation can be scoped separately while write questions remain open.

## 6. Required frontend screens/components (not built)

1. Vehicle Master: searchable selectable vehicle list plus sectioned form matching visible information groups. Components: text/identifier inputs, dependent selects, date inputs, capacity-plus-unit row, narration textarea, read-only status treatment pending confirmation, Update/Clear/Close; create mode only when confirmed. Do not add deletion based on draft repository code.
2. Vehicle Tariff Group: name input, group grid, Save/Clear/Close and conditional Delete only under approved rules. Clarify whether Save also renames a selected record.
3. Vehicle Group Tariff: group list plus 17-value rate form and Update/Close. Preserve two-decimal display as observed without turning sample values into defaults.

Target Next.js/TypeScript/Tailwind/shadcn/ui. Share group selection and lookup adapters where useful, without inventing a full frontend architecture. Required state is listed in section 2. Dependent-selection reset, empty/missing options, failed requests and unsaved-change handling are proposed UX needs, not behaviors proven by screenshots. Exact menu routes, responsive layout and navigation after Close remain TBD.

## 7. Lookup dependencies

| UI dependency | Existing API / model source | Evidence / gap |
| --- | --- | --- |
| Emirate/category/code | `/lookups/states`, `/plate-categories?state_id=…`, `/plate-codes?plate_category_id=…` under `/lookups` | Category control absent in screenshot; FK targets state directly. Must reconcile before write mapping. |
| Make → Model → Capacity | `/lookups/makes`, `/lookups/models?make_id=…`, `/lookups/engine-capacities?model_id=…` | Existing query filters; vehicle capacity association lacks FK. |
| Vehicle/Fuel Type | `/lookups/vehicle-types`, `/lookups/fuel-types` | TypeId versus VHType semantics need confirmation. |
| Capacity unit | `/lookups/fuel-capacity-units` | FuelCapUnitId label/ID source; additional FleetType FK unresolved. |
| Transmission/Color | `/lookups/transmission-types`, `/lookups/colours` | Vehicle FKs declared. |
| Insurance | `/lookups/insurance-policies`, `/lookups/insurance-companies` | Insurance type missing from API/screen; policy-company filtering unproven. |
| TC number | `/lookups/tc-nos` | Candidate TCNoId association lacks vehicle FK. |
| Tariff group | `/lookups/tariff-groups` | Existing group-model query; IDs/rates serialization unverified. |
| Branch/Location | `/lookups/company-branches`, `/lookups/locations` | No branch key on LocationMaster; branch-filter behavior unknown. |
| Status | `/lookups/statuses` | Unfiltered StatusMaster; correct status domain/editability unknown. |
| Year | No dedicated year API | Integer DB value; UI select options/range unknown. |

All API paths in this table are source-defined except explicit gaps. Real option completeness, label uniqueness and response shape are UNKNOWN until tested. Schema presence does not prove required lookup rows exist.

## 8. Relationship map

CONFIRMED DATABASE RELATIONSHIP (generated snapshot only): Vehicle → Model → Make; Vehicle → PlateCode, Colour, Transmission, Type; Vehicle.FuelCapacityUnitId → both FuelCapacityUnit and FleetType; PlateCode.PlateCategoryId → State.StateId. The last two are anomalous and must not be “corrected” by guessing.

CONFIRMED BUSINESS RELATIONSHIP: current code's state/category/code and make/model/capacity query chains; screenshots show a vehicle tariff-group choice and pricing for a selected group. This confirms visible business associations, not hidden database IDs.

SUSPECTED RELATIONSHIP: Vehicle.TariffGroupId → group PK; Vehicle → engine capacity, fuel type, insurance policy/company/type, TC number, branch/location/status through named ID candidates; Narration → Remarks and policy-adjacent box → InsurancePolicyRecNo.

UNKNOWN: Fleet No; Emirate source/derivation; status IDs and edit rules; branch/location and policy/company filtering; current-contract impact of rate changes. See [RELATIONSHIPS.md](../RELATIONSHIPS.md) for exact classification and constraint targets.

## 9. Implementability and risks

Status refers to the full feature including writes, not permission to begin coding. Basic read-only implementation is feasible after approval, with unresolved labels displayed honestly rather than fabricated.

| Feature / operation | Assessment |
| --- | --- |
| Vehicle list/search/detail | Feasible after repairing the isolated module; start with confirmed raw fields/IDs. Enriched labels and Fleet No search need mapping evidence. Runtime/query shape unverified. |
| Vehicle create | NEEDS CONFIRMATION: Fleet No, Emirate/category, InsuranceTypeId, audit/latest-km defaults, lookup constraints and status/duplicate rules. |
| Vehicle update | NEEDS CONFIRMATION: writable versus derived/status fields, nullable preservation, relationships and effect on active rentals. |
| Vehicle delete | Not safe to assume; absent from screenshot and candidate references span contracts/fines/movements/accounting. Exclude initially. |
| Tariff group list/detail | Feasible using existing lookup query after verification. |
| Tariff group create | Model can accept required name while rates are nullable, but null-versus-zero initialization and name policy require confirmation. |
| Tariff group rename | Feasible column update only after confirming Save/edit behavior and duplicate policy; preserve all rates. |
| Tariff group delete | NEEDS CONFIRMATION: referenced by vehicle business association with no declared FK; additional use/data may exist. |
| Group tariff read | All 17 fields exist on one row per group ID; actual rows/response unknown. |
| Group tariff update | NEEDS CONFIRMATION: rate bounds/null/default rules and impact on current contracts; safe field allowlist and write verification needed. |

| Risk | Classification | Impact / resolution |
| --- | --- | --- |
| Vehicle repository syntax/import/schema defects | BLOCKING | Fix in future approved vehicle work before import/endpoint verification; generated code unchanged. |
| Unknown Fleet No, Emirate/category mapping and insurance type/defaults | BLOCKING | Prevent faithful Vehicle create/update contract; inspect legacy behavior/live metadata. |
| Anomalous plate/state and dual fuel-unit FKs | BLOCKING | Verify live metadata and sample associations before affected vehicle writes. |
| Unknown audit identity/latest odometer/create values | BLOCKING | Existing required fields cannot be filled with guessed actor IDs or defaults. |
| Status domain and greyed control | NEEDS CONFIRMATION | Do not allow manual ON CONTRACT changes or infer an ID. |
| Group/rate null-versus-zero, validations/defaults | NEEDS CONFIRMATION | No generated defaults/range checks; visible examples are not rules. Blocks final write contract until decided. |
| Delete references / edits affecting transactions | NEEDS CONFIRMATION | Missing FK does not mean unused; gate delete and history-sensitive updates. |
| Duplicate plate/chassis/group labels | NEEDS CONFIRMATION | No relevant uniqueness declared; duplicates not observed. Determine identity/uniqueness rule and inspect data. |
| Nullable values / orphan lookup IDs / legacy inconsistency | NEEDS CONFIRMATION | Potential, not observed. Use read-only checks and preserve unknown values instead of silently resetting. |
| Lookup JSON shapes, Decimal serialization and label casing | NEEDS CONFIRMATION | Current endpoints return ORM objects without explicit schemas; test response before designing adapters. No incompatibility has been proven. |
| Insurance-company or location filtering | NEEDS CONFIRMATION | No supporting direct lookup key; no dependent filtering assumed. |
| Rate updates affecting existing contracts/customer tariffs | NEEDS CONFIRMATION | Snapshot/recalculation and precedence not established. |
| Concurrent edits and accidental full-row overwrites | NEEDS CONFIRMATION | Approve field-level write and concurrency behavior; current draft uses full dump. |
| Static label/layout adaptation | LOW RISK | Clear screenshots support three dialogs and field groups; exact navigation remains unknown. |
| Copying evidence / read-only generated metadata extraction | LOW RISK | Completed without source or DB changes. |

## 10. Questions requiring confirmation

1. What is Fleet No, where is it stored, and is it editable or automatically assigned?
2. Does selecting Emirate directly filter Plate Code? Is Plate Category hidden, automatic, or omitted from this capture?
3. What is the small numeric box beside Insurance Policy? Where does required InsuranceTypeId come from?
4. How should new vehicles obtain initial status, latest odometer, and created/updated actor values? Which fields may be edited while ON CONTRACT?
5. Does Location depend on Branch, and does Policy depend on Company? Does Narration save to Remarks?
6. Does Tariff Group Save also rename a selection? Is Delete required for the demo, and what happens when a group is used by vehicles?
7. For a new group, should unspecified rates be null or zero? What bounds/rounding and discount rules are required? Do rate changes affect current contracts or only future selections?
8. Which plate/chassis/fleet/group-name values must be unique, and what casing/whitespace rules does the reference app apply?

Database-verifiable follow-up (not business assumptions): confirm live FKs/defaults/triggers, required lookup rows/status domains, representative reference joins and any duplicate/orphan values. No such live check was executed here. Business answers alone should not overwrite contradictory database evidence.

## 11. Proposed implementation plan and readiness

| Feature | Readiness now | Reason |
| --- | --- | --- |
| Vehicle Master | NEEDS CONFIRMATION | Field/default/status/relationship gaps plus unfinished backend. |
| Vehicle Tariff Group | NEEDS CONFIRMATION | Table clear; create defaults, rename behavior, uniqueness and deletion policy unresolved. |
| Vehicle Group Tariff | NEEDS CONFIRMATION | All fields present; null/validation and existing-contract impact unresolved. |

Recommended order after explicit approval:

1. Resolve Vehicle field questions and verify live lookup/FK metadata read-only; define a minimal API payload and allowed writes. Scope out delete unless explicitly required.
2. Repair Vehicle syntax/imports/schema mapping, implement verified read-only list/search/detail, and verify current lookups without altering their existing contracts unnecessarily.
3. Implement group-name maintenance and rate editor APIs against the same group table once name/null/validation/update policies are approved; verify field preservation.
4. Implement Vehicle create/update with verified lookups, actor/default values and status rules; test permitted writes using controlled records.
5. Build the three frontend screens and validate selection, save/update, null/Decimal handling and persistence against real approved data.

If approved only for reading, steps 1–2 can proceed independently of rate/delete business decisions. No feature code is authorized by the current analysis request. Await explicit approval of the analysis before implementation.


## User confirmations and live insurance check — 2026-09-06

These confirmations supersede earlier tentative exclusions: Vehicle requires full CRUD plus search, including delete. Tariff group-name maintenance requires CRUD; the group pricing screen creates/updates pricing information. Emirate uses the state → plate category → plate code lookup chain (user-confirmed intended behavior; anomalous physical FK still needs reconciliation). Fleet No maps to VHType; preserve its string database type. The policy-adjacent field is InsurancePolicyRecNo; leave it as-is initially. Implementation remains unapproved.

Read-only SELECTs against the configured local MSSQL database returned:

- Insurance company: ID 1, AL SAGR (one row).
- Insurance policy: ID 1, number 6105015305, Status=true (one row).
- Insurance type: ID 1, Comprehensive (one row; no type 3).
- VehicleId 2, VHType='34': InsuranceCompanyId=1, InsurancePolicyId=1, InsurancePolicyRecNo=0, InsuranceTypeId=3.
- Grouped vehicle records: 101 use company 1/policy 1/type 1; 20 use company 1/policy 1/type 3.
- Live foreign-key metadata returned no constraints involving the insurance master tables. Live columns confirm PolicyMaster has no InsuranceCompanyId or InsuranceTypeId, and CompanyMaster/TypeMaster have no linking keys to the other insurance masters.

Conclusion: these three insurance IDs coexist on each vehicle row; there is no direct company → policy → type relationship declared in these masters or enforced by a foreign key. All current vehicle rows use company/policy 1, which is observed data, not a universal business constraint. Type 3 is an unmatched reference in the current type master, affecting 20 vehicles, including Fleet No 34. Its intended label and historical origin are UNKNOWN; do not substitute Comprehensive or change database rows. Stored procedure/trigger behavior was not investigated in this check.

Before implementation confirm how existing unmatched type 3 should appear in the UI and whether selecting a type is required for new vehicles. Preserve existing IDs on unrelated edits; do not silently normalize them. Vehicle deletion is now requested, but dependency handling must still be defined to avoid orphaning transaction history. No DB rows, schema, generated models or feature code were changed by this check.


## Approved tariff API revision

Creating a group name now assigns its identity ID and initializes all 17 pricing values to 0.00 atomically. GET `/vehicle-tariff-groups/` lists all groups; GET `/vehicle-tariff-groups/search?q=...` searches names separately. Name and rate updates use PATCH only; PUT was removed for tariffs. Get-by-ID and guarded delete remain. Existing database rows were not backfilled. Ten isolated API tests pass, including complete listing beyond 100 rows, automatic pricing initialization and removal of PUT.
