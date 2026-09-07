# Relationships and evidence

## Evidence categories

- CONFIRMED DATABASE RELATIONSHIP: explicit `ForeignKeyConstraint` in generated mappings. Here this means confirmed in the repository snapshot only; live MSSQL has not been queried.
- CONFIRMED BUSINESS RELATIONSHIP: explicit application query or supplied workflow establishes the association. This does not assert a database foreign key or prove a join.
- SUSPECTED RELATIONSHIP: plausible from columns/table structure, without enforcing constraint or implementing business code.
- UNKNOWN: target, join, meaning, cardinality, or business rule cannot yet be established.

The user confirms the desired workflow stages; that alone does not confirm their physical table joins.

## Core workflow associations

| Association | Category | Evidence and unresolved detail |
| --- | --- | --- |
| Customer records ↔ account group 26 | CONFIRMED BUSINESS RELATIONSHIP | `customers/repository.py` explicitly filters/creates `TblAccountLedger` with group 26. Live group label not verified. |
| Supplier records ↔ account group 22 | CONFIRMED BUSINESS RELATIONSHIP | `suppliers/repository.py` uses group 22. |
| Customer → Contract | SUSPECTED RELATIONSHIP | `VT_ContractMaster.CustomerId` may join `tbl_AccountLedger.ledgerId`; no declared FK or contract query. Customer snapshots also exist in contract fields. |
| Vehicle → Contract | SUSPECTED RELATIONSHIP | Contract master `VehicleId` and `VT_ContractVehicleMaster.ContractId/VehicleId` are candidates. No declared FKs; source of truth and replacement/cardinality rules UNKNOWN. |
| Vehicle → tariff group | SUSPECTED RELATIONSHIP | Vehicle `TariffGroupId` and tariff group PK correspond by name only; no declared FK or pricing service. |
| Customer → customer tariff | SUSPECTED RELATIONSHIP | `tbl_CustomerTariff.customer` may reference ledgerId; no declared FK. |
| Tariff → Contract | UNKNOWN | Contract has `Rate`, CDW/PAI, mileage/charge fields but no explicit tariff ID mapping. Copying/snapshotting and customer-vs-group rate precedence UNKNOWN. |
| Contract → Checkout | SUSPECTED RELATIONSHIP | Contract vehicle row has `ContractId`, `DatetimeOut`, `KmOut`, `FuelLevelIdOut`, `CheckedOutBy`, `LocationOut`. No declared FK or workflow code. |
| Contract → Check-in | SUSPECTED RELATIONSHIP | Same row has `DatetimeIn`, `KmIn`, `FuelLevelIdIn`, `CheckedInBy`, `LocationIn`, and separate `DTIN`. Their exact semantics UNKNOWN. |
| Contract → Active rental | UNKNOWN | Contract `Status`, assignment `ContractVehicleStatus`, vehicle `StatusId`, and dates are candidate inputs; do not invent a filter. |
| Vehicle/Contract → Fine | SUSPECTED RELATIONSHIP | `Traffic_Fine.VEHICLEID` may join vehicle PK. No ContractId on fine table; allocation by rental time is a hypothesis. `tbl_SalesMaster.trafficFineNo` may refer to TICKETNO. |
| Vehicle/Contract → Salik | SUSPECTED RELATIONSHIP | `Salik_Toll.TAGNO/PLATENO/DATEANDTIME` and vehicle `SalikTag/PlateNo` suggest matching. No vehicle/contract FK in toll model; matching/overlap rules UNKNOWN. |
| Contract → Invoice | SUSPECTED RELATIONSHIP | `tbl_SalesMaster.contractId` and `Staging_Invoice_Header.SIH_CONTRACT_ID` are candidates; no declared FKs. Staging-to-posted transformation UNKNOWN. |
| Invoice → Receipt | UNKNOWN | No direct salesMasterId in receipt master/details. Receipt `invoiceNo` must not be assumed to identify the sales invoice; it may number the receipt itself. |
| Invoice/receipt settlement → party balance | SUSPECTED RELATIONSHIP | `tbl_PartyBalance` has voucher/against-voucher, invoice/against-invoice, ledger and contract references; allocation queries/constraints absent. |
| Sales/receipt details → their masters | SUSPECTED RELATIONSHIP | `salesMasterId` and `receiptMasterId` exist in details; no declared foreign keys in generated snapshot. |

## Confirmed database relationships in relevant mappings

Exact declarations (including constraint names) are in [DATABASE.md](DATABASE.md).

| Source | Target |
| --- | --- |
| `Staging_Invoice_Detail.SID_SIH_ID` | `Staging_Invoice_Header.SIH_ID` |
| `VT_Veh_ModelMaster.MakeId` | `VT_Veh_MakeMaster.MakeId` |
| `VT_Veh_PlateCodeMaster.PlateCategoryId` | `VT_Veh_StateMaster.StateId` — unusual; NOT plate category master |
| `VT_Veh_VehicleMaster.ModelId` | `VT_Veh_ModelMaster.ModelId` |
| `VT_Veh_VehicleMaster.PlateCodeId` | `VT_Veh_PlateCodeMaster.PlateCodeId` |
| `VT_Veh_VehicleMaster.ColourId` | `VT_Veh_ColourMaster.ColourId` |
| `VT_Veh_VehicleMaster.FuelCapacityUnitId` | `VT_Veh_FuelCapacityUnitMaster.FuelCapUnitId` |
| `VT_Veh_VehicleMaster.FuelCapacityUnitId` | `VT_Veh_FleetTypeMaster.FleetTypeId` — second FK on same source column |
| `VT_Veh_VehicleMaster.TransmissionId` | `VT_Veh_TransmissionMaster.TransmissionId` |
| `VT_Veh_VehicleMaster.TypeId` | `VT_Veh_TypeMaster.TypeId` |

Do not repair the unusual constraints or generated relationships during MVP application work without explicit instruction and authoritative investigation.

## Confirmed business lookup associations

`lookups/repository.py` filters plate categories by StateId, plate codes by PlateCategoryId, models by MakeId, and engine capacities by ModelId. These query dependencies are confirmed code behavior. The plate-code query's intended category association differs from its generated FK target; the database truth must be checked before relying on it for writes. No FK is declared for category StateId or engine capacity ModelId in the snapshot.

## Questions to resolve before transactional writes

1. Does the current MSSQL schema match these mappings, especially the two unusual FKs? Inspect metadata read-only; do not alter it.
2. Is ContractMaster.CustomerId always an account ledger in group 26? How are customer detail snapshots populated?
3. Which vehicle association controls availability: master VehicleId or contract vehicle rows? Can a contract have multiple/replacement rows?
4. Which status table/values apply to contract, assignment, and fleet availability? What changes atomically at checkout/check-in?
5. Which tariff takes precedence? What rental duration, partial-day, mileage, discount, CDW/PAI and fuel rules apply?
6. How is required ContractActualEndDate stored for an open contract? What does DTIN mean compared with DatetimeIn?
7. How are fine/toll charges attributed to a rental, deduplicated, marked billed, and handled after check-in?
8. Are staging invoices mandatory? Which sales, tax, ledger-posting and party-balance writes constitute posting?
9. How are receipts allocated, including partial payments/advances, and how are voucher/invoice numbers generated?
10. Which procedures/triggers, actor IDs, branch/location, and financial-year values are required? These are not captured adequately by generated tables alone.

## Vehicle screenshot evidence addendum — 2026-09-06

Screenshots confirm a business-level vehicle tariff-group selector and a rate editor with a selected group. They do not display persisted IDs. Therefore vehicle ↔ tariff group and selected group ↔ displayed rates are CONFIRMED BUSINESS RELATIONSHIP at the UI level; the exact `VehicleMaster.TariffGroupId → TariffGroupMaster.TariffGroupId` join remains SUSPECTED RELATIONSHIP, with no declared FK or implemented vehicle join. Storing name and rates on the same TariffGroupMaster row is a confirmed mapping fact, not a separate FK relationship.

| Association | Classification | Evidence / limit |
| --- | --- | --- |
| Vehicle.ModelId → Model.ModelId → Make.MakeId | CONFIRMED DATABASE RELATIONSHIP | Both FKs declared in generated snapshot; no direct Vehicle.MakeId. |
| Vehicle.PlateCodeId → PlateCode.PlateCodeId | CONFIRMED DATABASE RELATIONSHIP | Generated FK. Exact label formatting unknown. |
| PlateCode.PlateCategoryId → State.StateId | CONFIRMED DATABASE RELATIONSHIP | Actual generated FK target; conflicts with intuitive category meaning. Live verification required. |
| Vehicle.ColourId / TransmissionId / TypeId → respective masters | CONFIRMED DATABASE RELATIONSHIP | Generated FKs. Screenshot Veh Type → TypeId is still a UI mapping candidate. |
| Vehicle.FuelCapacityUnitId → FuelCapacityUnit.FuelCapUnitId AND FleetType.FleetTypeId | CONFIRMED DATABASE RELATIONSHIP | Both generated FKs; shared-column semantics unknown. |
| State → category → plate code; Make → Model → EngineCapacity | CONFIRMED BUSINESS RELATIONSHIP | Existing repository filter chains; not all hops have declared FKs. Screens do not show a plate-category field or change events. |
| Vehicle.EngineCapacityId / FuelTypeId / InsurancePolicyId / InsuranceCompanyId / InsuranceTypeId / TCNoId | SUSPECTED RELATIONSHIP | Named master PK candidates exist, but these vehicle FKs are absent in snapshot. |
| Vehicle.BranchId → CompanyBranch.BranchId; Vehicle.LocId → Location.LocationId | SUSPECTED RELATIONSHIP | Candidate joins; no vehicle constraints. LocationToRemove is another legacy location field. |
| Vehicle.StatusId → Status.StatusId; Status.StatusTypeId → StatusType.StatusTypeId | SUSPECTED RELATIONSHIP | No declared FKs; ON CONTRACT label gives no ID/domain/edit permission. |
| Branch → Location; Policy → Company | UNKNOWN | Relevant lookup models contain no direct branch-location or policy-company key. No dependency demonstrated. |
| Emirate control → StateMaster versus tbl_Emirate | UNKNOWN | Vehicle has no direct EmirateId/StateId; derived path must be confirmed. |
| Fleet No → persisted value | UNKNOWN | No FleetNo field in vehicle mapping; a numeric UI value does not establish VehicleId or VHType. |
| Unlabeled policy box → InsurancePolicyRecNo; Narration → Remarks | SUSPECTED RELATIONSHIP | Semantic field mapping candidates only, not database joins. |

Existing contract, movement, fine, service, replacement and accounting mappings reference candidate vehicle IDs without comprehensive FK coverage. Their presence makes physical vehicle deletion unsafe to assume. No duplicates, orphan rows, or inconsistent live data were queried or confirmed. See [Vehicle analysis](features/VEHICLE_ANALYSIS.md) for scope-specific questions and gates.
