# Reference application captures

## Evidence and sources

Updated 2026-09-06 for the Vehicle feature slice. Three user-supplied screenshots are now stored unchanged in `reference/screenshots/vehicle/`; originals in the user's Pictures/Screenshots directory were preserved. They show a legacy desktop application inside an AnyDesk session viewed through a browser video frame. The browser path identifies a screencast, but the video was not supplied or reviewed for this task. Only these three still frames and repository code were analyzed.

| Capture | Original screenshot basename | Repository copy |
| --- | --- | --- |
| Vehicle Master / Add Vehicle | Screenshot from 2026-09-06 20-14-26.png | [vehicle-master.png](../reference/screenshots/vehicle/vehicle-master.png) |
| Vehicle Tariff Group / Tariff Group | Screenshot from 2026-09-06 20-16-02.png | [vehicle-tariff-group.png](../reference/screenshots/vehicle/vehicle-tariff-group.png) |
| Vehicle Group Tariff | Screenshot from 2026-09-06 20-16-23.png | [vehicle-group-tariff.png](../reference/screenshots/vehicle/vehicle-group-tariff.png) |

Observed means visible pixels; inferred means a plausible interpretation, not a tested action. UI-to-column matches below are candidates unless supported by declared constraints or existing query code. A red marker suggests mandatory entry; it does not prove backend validation. White fields are editable-looking, not interaction-tested. No save/delete/search outcome or navigation sequence was observed.

## Vehicle — screen 1: Vehicle Master (window title “Add Vehicle”)

Purpose: maintain vehicle master details; the captured populated form appears to be editing an existing selection because its primary button says Update. Create is suggested by the title only, not demonstrated.

Visible sections: Plate Details; Make Details; Veh Registration Details; Veh Insurance Details; RTA Details followed by operational fields; right-hand Search and vehicle list. Two form columns, compact label/control rows, blue section labels, red mandatory markers, blue action buttons, pale background and blue selection highlight are visible. These are visual references, not a requirement to reproduce the browser/AnyDesk chrome.

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

Actions and selection:

- Update, Clear and Close buttons are visible. The window also has title-bar controls. Update success and Clear's exact reset behavior are unknown.
- A selected vehicle row is highlighted in the right list. Rows contain a leading number and plate-related text separated by vertical bars; the leading number's identity is unknown. Do not assert it is Fleet No or VehicleId.
- Search input and a vertical scrollbar are visible. Search fields, sorting, pagination, filtering trigger and result loading behavior cannot be determined from the still.
- Create: suggested, not demonstrated. Update: explicit visible action. Delete: no visible action. Clear/reset: explicit visible action. Search and existing-record selection: visible affordances, behavior untested.
- Required-looking marker is visible beside a blank Location, while Status looks disabled. The loaded state does not establish whether this form can currently be saved or how requirements are enforced.

Dependencies: Make → Model → Engine Capacity is supported by current repository query filters and generated make/model constraints, but change/reset behavior was not observed. Emirate → Plate Code is suggested by the fields; current APIs introduce a Plate Category step not visible here. Policy/company linkage, branch/location filtering, automatic status changes and tariff-driven calculations are UNKNOWN.

Lookup-looking values include Emirate, plate code, make/model/capacity, year, vehicle/fuel types, fuel unit, transmission, colour, insurance policy/company, TC number, tariff group, branch, location and status. Year may be locally generated; no dedicated year master was identified. ON CONTRACT is a displayed label, not evidence for a numeric status ID or editable status rule.

Open questions: Fleet No storage; unlabeled insurance box; missing Insurance Type control despite required DB field; source of latest odometer/audit values; state/category selection; status editing; Location and Narration mappings; duplicate/expiry validation; availability of create mode; behavior of Clear/Close with unsaved edits. See [Vehicle analysis](features/VEHICLE_ANALYSIS.md) for implementation gates.

## Vehicle — screen 2: Vehicle Tariff Group (window title “Tariff Group”)

Purpose: maintain the names of vehicle tariff groups. Visible sections are a Tariff Group entry area and Details grid. The single Tariff Group field is a text input with a red mandatory marker; it is blank in this frame. Grid columns are Sl.No and Tariff Group Name. The selected first row is MG5; other visible names include ACCENT, CRETA, PICANTO, C, C1, G, G1 and NISSAN SUNNY 2020, with another row partly visible below. Serial numbers are display values, not demonstrated database IDs.

Buttons: Save, Clear, a dim/disabled-looking Delete button (label appears to read Delete at this resolution), and Close. No explicit Update button or search field is visible. A vertical grid scrollbar and highlighted row support existing-record selection. Selection-to-input population was not observed; the highlighted row and blank input caution against assuming it.

Capability assessment: create suggested by Save and blank required field; read/list/select explicit; rename/update UNKNOWN (Save could have multiple modes); delete affordance appears present but enablement and safeguards UNKNOWN; clear/reset and close explicit; search not shown. Inferred workflow is enter a name → Save, or select a group → inspect/edit, subject to confirmation. No actual persistence was observed.

Candidate store: `VT_Veh_TariffGroupMaster` / `VTVehTariffGroupMaster`, `TariffGroupId` PK and `TariffGroupName`. The screen shows no rate controls. Duplicate-name, whitespace/case, delete-in-use and initial-rate behavior are unknown. Group names also occur in the vehicle selector and rate screen: business-level association is visible; exact persisted IDs are not.

Visual notes: small centered dialog, single input/action row, grid below with coloured header and selection. Navigation from a menu to this dialog is not captured; do not claim a specific menu path.

## Vehicle — screen 3: Vehicle Group Tariff

Purpose: maintain the rate/discount/charge values associated with a selected vehicle group. A left-hand selectable group list and right-hand numeric-looking input rows are visible. MG5 is highlighted; group names include those on the previous screen, plus SENTRA 2014, LANCER EX 2015, TOYOTA FORTUNER and KIA CARNIVAL. No search field or group-name edit field is shown.

All 17 rate inputs are numeric-looking text controls, not proven numeric widgets. They display two decimal places. No mandatory markers or clearly read-only rate fields are visible. Values below are examples from one selected group, not defaults, formulas or global rules.

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

Actions: Update and Close. Read/list/select and update affordances are explicit. Create/delete/clear/search are not shown. Inferred workflow: select a group, review/change rates, Update, then Close; no action outcome or selection change was observed.

Candidate persistence: all 17 fields and the group name occur on the same generated `VT_Veh_TariffGroupMaster` row keyed by `TariffGroupId`. The model has one rate set per group ID; actual reference-app write behavior and uniqueness of group names are not verified. No separate group-rate/history table is needed by the current mapping evidence, but historical pricing behavior remains UNKNOWN.

The generated fields are nullable DECIMAL(18,2) with no declared server defaults or percentage/range checks. Do not treat the displayed zeros as schema defaults or infer a 6-day week/other rental formula from the sample amounts. Currency, percent bounds, discount interaction, allowed-km rounding, fuel unit basis, CDW/PAI meaning/application, null-versus-zero, and impact on existing contracts need confirmation. No customer-tariff precedence can be established from this screen.

Visual notes: compact list-and-form dialog, vertically aligned values, bottom action pair. Navigation to it from Tariff Group or a menu is not captured.

## Capture template for future evidence

- Feature/page: TODO
- Source screenshot/video and timestamp: TODO
- Purpose: TODO
- Visible fields/control types/mandatory markers: TODO
- Actions and observed outcomes: TODO
- Workflow and entry/exit conditions: TODO
- Navigation actually observed: TODO
- Relevant API/data and confidence: TODO
- Visual notes: TODO
- Unanswered questions: TODO
- Observation date/source/reviewer: TODO

Remaining capture queue: Vehicle create mode and demonstrated group save/delete behavior; customer, contract, checkout, active rental, fines/Salik, check-in, invoice/register and receipt/register. Exclude credentials or unnecessary personal/payment data from future captures.
