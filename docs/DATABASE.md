# MVP database catalogue

Source: `FleetTrack Backend/app/generated_models/models.py` and `app/database/session.py`, inspected 2026-09-06 using static parsing. All names, types, keys, constraints and indexes below are facts about the generated mapping snapshot. Live MSSQL metadata, stored procedures, triggers, data contents and schema freshness are UNKNOWN. Absence of a declared FK here does not prove absence in the current live database.

MSSQL is authoritative. Connection target is `Balance` at localhost port 1433 through pyodbc/ODBC Driver 18; credentials are intentionally not reproduced. Generated models are read-only. Do not create/drop tables or repair unusual FKs during this task.

## Interpretation and blockers

Customers/suppliers use `tbl_AccountLedger` in implemented code. Other core table purposes are candidates inferred from fields unless explicitly described as queried. Relationships are classified separately in [RELATIONSHIPS.md](RELATIONSHIPS.md).

There is no dedicated active-rental application implementation; likely state comes from contract/assignment/vehicle status and dates. No separately named checkout/check-in mapping was found; the contract-vehicle table has out/in fields. Do not create new tables to fill these conceptual stages.

Most monetary fields are Decimal (often 18,2 in rental tables and 18,5 in accounting). Many ledger/accounting IDs are Numeric(18,0), unlike integer vehicle/contract IDs. Preserve exact field casing and scale. Optional in a mapping is a nullability fact, not a business permission. PK identity values must not be manually guessed.

ContractMaster has many non-null identity/contact/date fields, including ContractActualEndDate. Verify the legacy open-contract representation and all required inputs/defaults before inserts. Vehicle creation also requires latest odometer and audit values. The current draft vehicle schema does not match these requirements.

The generated FK on plate code PlateCategoryId targets StateMaster.StateId. Vehicle FuelCapacityUnitId has FKs to both FuelCapacityUnitMaster and FleetTypeMaster. Preserve these declarations, verify live metadata, and resolve semantics before writes.

## Core tables

### `tbl_AccountLedger` — `TblAccountLedger`

Source: generated model line 1248. Purpose: Customer/supplier master confirmed by repository queries; customer group 26, supplier group 22.

Primary key: `ledgerId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `ledgerId` | `Numeric(18, 0)` | NOT NULL |
| `accountGroupId` | `Numeric(18, 0)` | Nullable |
| `ledgerName` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `mobile` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `email` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `emirateId` | `Numeric(18, 0)` | Nullable |
| `openingBalance` | `DECIMAL(18, 5)` | Nullable |
| `creditPeriod` | `Integer` | Nullable |
| `creditLimit` | `DECIMAL(18, 5)` | Nullable |
| `billByBill` | `Boolean` | Nullable |
| `routeId` | `Numeric(18, 0)` | Nullable |
| `areaId` | `Numeric(18, 0)` | Nullable |
| `Nationality` | `NCHAR(3, 'SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `CustomerIdNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `CustomerIdExpiry` | `DateTime` | Nullable |
| `isCorporate` | `Boolean` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('ledgerId', name='PK_tbl_AccountLedger_1')
Index('IX_tbl_AccountLedger', 'ledgerId', 'accountGroupId', mssql_clustered=False)
Index('IX_tbl_AccountLedger_1', 'accountGroupId', mssql_clustered=False)
Index('IX_tbl_AccountLedger_2', 'accountGroupId', 'billByBill', mssql_clustered=False)
Index('IX_tbl_AccountLedger_3', 'areaId', mssql_clustered=False)
Index('IX_tbl_AccountLedger_4', 'routeId', mssql_clustered=False)
Index('IX_tbl_AccountLedger_5', 'areaId', 'routeId', mssql_clustered=False)
Index('IX_tbl_AccountLedger_6', 'accountGroupId', 'areaId', 'ledgerId', 'routeId', 'billByBill', 'pricinglevelId', mssql_clustered=False)
Index('IX_tbl_AccountLedger_7', 'pricinglevelId', mssql_clustered=False)
```

Foreign keys: none declared on this table in the generated snapshot.

### `VT_Veh_VehicleMaster` — `VTVehVehicleMaster`

Source: generated model line 3919. Purpose: Fleet master candidate; application module incomplete.

Primary key: `VehicleId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `VehicleId` | `Integer` | NOT NULL |
| `ModelId` | `Integer` | NOT NULL |
| `EngineCapacityId` | `Integer` | NOT NULL |
| `PlateCodeId` | `Integer` | NOT NULL |
| `PlateNo` | `Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')` | NOT NULL |
| `VHType` | `Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `TariffGroupId` | `Integer` | NOT NULL |
| `StatusId` | `Integer` | NOT NULL |
| `InitialKmRdg` | `Integer` | NOT NULL |
| `LatestKmRdg` | `Integer` | NOT NULL |
| `FuelCapacityUnitId` | `Integer` | NOT NULL |
| `FuelLevel` | `Integer` | Nullable |
| `SalikTag` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | NOT NULL |
| `BranchId` | `Integer` | Nullable |
| `LocId` | `Integer` | Nullable |
| `CreatedBy` | `Integer` | NOT NULL |
| `CreatedDate` | `DateTime` | NOT NULL |
| `LastUpdatedBy` | `Integer` | NOT NULL |
| `LastUpdatedDate` | `DateTime` | NOT NULL |

Declared constraints/indexes (verbatim semantics from mapping):

```python
ForeignKeyConstraint(['ColourId'], ['VT_Veh_ColourMaster.ColourId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_ColourMaster')
ForeignKeyConstraint(['FuelCapacityUnitId'], ['VT_Veh_FuelCapacityUnitMaster.FuelCapUnitId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_FuelCapacityUnitMaster')
ForeignKeyConstraint(['FuelCapacityUnitId'], ['VT_Veh_FleetTypeMaster.FleetTypeId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_FleetTypeMaster')
ForeignKeyConstraint(['ModelId'], ['VT_Veh_ModelMaster.ModelId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_ModelMaster')
ForeignKeyConstraint(['PlateCodeId'], ['VT_Veh_PlateCodeMaster.PlateCodeId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_PlateCodeMaster')
ForeignKeyConstraint(['TransmissionId'], ['VT_Veh_TransmissionMaster.TransmissionId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_TransmissionMaster')
ForeignKeyConstraint(['TypeId'], ['VT_Veh_TypeMaster.TypeId'], name='FK_VT_Veh_VehicleMaster_VT_Veh_TypeMaster')
PrimaryKeyConstraint('VehicleId', name='PK_VT_Veh_VehicleMaster')
```

### `VT_Veh_TariffGroupMaster` — `VTVehTariffGroupMaster`

Source: generated model line 936. Purpose: Group pricing; queried by existing tariff-group lookup. Pricing application rules unknown.

Primary key: `TariffGroupId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `TariffGroupId` | `Integer` | NOT NULL |
| `TariffGroupName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | NOT NULL |
| `DailyRate` | `DECIMAL(18, 2)` | Nullable |
| `WeeklyRate` | `DECIMAL(18, 2)` | Nullable |
| `MonthlyRate` | `DECIMAL(18, 2)` | Nullable |
| `FuelCharges` | `DECIMAL(18, 2)` | Nullable |
| `AllowedKmsPerDay` | `DECIMAL(18, 2)` | Nullable |
| `ExtraKmCharges` | `DECIMAL(18, 2)` | Nullable |
| `DailyCDW` | `DECIMAL(18, 2)` | Nullable |
| `WeeklyCDW` | `DECIMAL(18, 2)` | Nullable |
| `MonthlyCDW` | `DECIMAL(18, 2)` | Nullable |
| `DailyPAI` | `DECIMAL(18, 2)` | Nullable |
| `WeeklyPAI` | `DECIMAL(18, 2)` | Nullable |
| `MonthlyPAI` | `DECIMAL(18, 2)` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('TariffGroupId', name='PK_VT_Veh_TariffGroupMaster')
```

Foreign keys: none declared on this table in the generated snapshot.

### `tbl_CustomerTariff` — `TblCustomerTariff`

Source: generated model line 1656. Purpose: Customer-specific pricing candidate; precedence/join unknown.

Primary key: `customerTariffId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `customerTariffId` | `Numeric(18, 0)` | NOT NULL |
| `customerTariff` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `customer` | `Numeric(18, 0)` | Nullable |
| `dailyRent` | `DECIMAL(18, 2)` | Nullable |
| `weeklyRent` | `DECIMAL(18, 2)` | Nullable |
| `monthlyRent` | `DECIMAL(18, 2)` | Nullable |
| `dailyCDW` | `DECIMAL(18, 2)` | Nullable |
| `weeklyCDW` | `DECIMAL(18, 2)` | Nullable |
| `monthlyCDW` | `DECIMAL(18, 2)` | Nullable |
| `dailyPAI` | `DECIMAL(18, 2)` | Nullable |
| `weeklyPAI` | `DECIMAL(18, 2)` | Nullable |
| `monthlyPAI` | `DECIMAL(18, 2)` | Nullable |
| `dailyDriverCharges` | `DECIMAL(18, 2)` | Nullable |
| `excessKMcharges` | `DECIMAL(18, 2)` | Nullable |
| `excessInscharges` | `DECIMAL(18, 2)` | Nullable |
| `isDiscountable` | `Boolean` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('customerTariffId', name='PK_tbl_CustomerTariff')
```

Foreign keys: none declared on this table in the generated snapshot.

### `VT_ContractMaster` — `VTContractMaster`

Source: generated model line 394. Purpose: Rental agreement candidate; many required identity/contact/date/payment fields. No contract API.

Primary key: `ContractId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `ContractId` | `Integer` | NOT NULL |
| `ContractType` | `Integer` | NOT NULL |
| `ContractRefNo` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | NOT NULL |
| `CustomerId` | `Numeric(18, 0)` | Nullable |
| `CustomerName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | NOT NULL |
| `VehicleId` | `Integer` | Nullable |
| `ContractStartDate` | `DateTime` | NOT NULL |
| `ContractExpectedEndDate` | `DateTime` | NOT NULL |
| `ContractActualEndDate` | `DateTime` | NOT NULL |
| `ContractLocId` | `Integer` | NOT NULL |
| `Rate` | `DECIMAL(18, 2)` | NOT NULL; default `text('((0))')` |
| `Status` | `Integer` | NOT NULL |
| `PaymentType` | `Integer` | NOT NULL |
| `PaymentMode` | `Integer` | NOT NULL |
| `BillingType` | `Integer` | Nullable |
| `RentalInvoiced` | `Boolean` | Nullable; default `text('((0))')` |
| `SalikInvoiced` | `Boolean` | Nullable; default `text('((0))')` |
| `FineInvoiced` | `Boolean` | Nullable; default `text('((0))')` |
| `LastInvoiceDate` | `DateTime` | Nullable |
| `Advance` | `DECIMAL(18, 2)` | NOT NULL; default `text('((0))')` |
| `Subtotal` | `DECIMAL(18, 2)` | NOT NULL; default `text('((0))')` |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('ContractId', name='PK_VT_VehicleContractMaster')
```

Foreign keys: none declared on this table in the generated snapshot.

### `VT_ContractVehicleMaster` — `VTContractVehicleMaster`

Source: generated model line 500. Purpose: Candidate assignment, checkout and check-in storage; not proof of workflow semantics.

Primary key: `Id`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `Id` | `Integer` | NOT NULL |
| `ContractId` | `Integer` | NOT NULL |
| `VehicleId` | `Integer` | NOT NULL |
| `ContractVehicleStatus` | `Integer` | NOT NULL |
| `DatetimeOut` | `DateTime` | Nullable |
| `DatetimeIn` | `DateTime` | Nullable |
| `DTIN` | `DateTime` | Nullable |
| `KmOut` | `Integer` | Nullable |
| `KmIn` | `Integer` | Nullable |
| `FuelLevelIdOut` | `Integer` | Nullable |
| `FuelLevelIdIn` | `Integer` | Nullable |
| `CheckedOutBy` | `Integer` | Nullable |
| `CheckedInBy` | `Integer` | Nullable |
| `LocationOut` | `Integer` | Nullable |
| `LocationIn` | `Integer` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('Id', name='PK_VT_ContractVehicleMaster')
```

Foreign keys: none declared on this table in the generated snapshot.

### `VT_Veh_StatusChangeDetails` — `VTVehStatusChangeDetails`

Source: generated model line 908. Purpose: Candidate vehicle/contract status history; requirement for rental transitions unknown.

Primary key: `Id`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `Id` | `Integer` | NOT NULL |
| `VehicleId` | `Integer` | Nullable |
| `ContractId` | `Integer` | Nullable |
| `StatusId` | `Integer` | Nullable |
| `VehKm` | `Integer` | Nullable |
| `DateTimeIn` | `DateTime` | Nullable |
| `DateTimeOut` | `DateTime` | Nullable |
| `LocationId` | `Integer` | Nullable |
| `CreatedDate` | `DateTime` | Nullable |
| `CreatedBy` | `Integer` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('Id', name='PK_VT_Veh_StatusChangeDetails')
```

Foreign keys: none declared on this table in the generated snapshot.

### `VT_Veh_VehicleMovements` — `VTVehVehicleMovements`

Source: generated model line 1028. Purpose: Candidate movement history; distinct from contract assignment, role in checkout unknown.

Primary key: `MovementId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `MovementId` | `Integer` | NOT NULL |
| `VehicleId` | `Integer` | NOT NULL |
| `StaffId` | `Integer` | NOT NULL |
| `StartDatetime` | `DateTime` | NOT NULL |
| `EndDatetime` | `DateTime` | NOT NULL |
| `LocationFrom` | `Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')` | NOT NULL |
| `LocationTo` | `Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')` | NOT NULL |
| `kmFrom` | `Integer` | NOT NULL |
| `kmTo` | `Integer` | NOT NULL |
| `MovementType` | `Integer` | NOT NULL |
| `LocId` | `Integer` | Nullable |
| `DiscardedFlag` | `Boolean` | NOT NULL |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('MovementId', name='PK_VT_Veh_VehicleMovements')
```

Foreign keys: none declared on this table in the generated snapshot.

### `Traffic_Fine` — `TrafficFine`

Source: generated model line 197. Purpose: Traffic fine source candidate. TICKETNO is PK; identity Id is not PK. Rental allocation unknown.

Primary key: `TICKETNO`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `Id` | `Integer` | NOT NULL |
| `TICKETNO` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | NOT NULL |
| `VEHICLEID` | `Integer` | NOT NULL |
| `FINEDATETIME` | `DateTime` | Nullable |
| `AMOUNT` | `DECIMAL(18, 2)` | Nullable |
| `PAID` | `Boolean` | Nullable |
| `ISPOSTED` | `Boolean` | Nullable |
| `VOUCHERNO` | `Unicode(255, 'SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `INVOICE_REMARKS` | `String(50, 'SQL_Latin1_General_CP1_CI_AS')` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('TICKETNO', name='PK_TRAFFIC_FINE')
```

Foreign keys: none declared on this table in the generated snapshot.

### `Salik_Toll` — `SalikToll`

Source: generated model line 129. Purpose: Toll source candidate; match to rental/vehicle unknown.

Primary key: `TRANSID`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `TRANSID` | `Numeric(18, 0)` | NOT NULL |
| `SALIKTRANSID` | `Unicode(255, 'SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `DATEANDTIME` | `DateTime` | Nullable |
| `TAGNO` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `PLATENO` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `AMOUNT` | `MONEY` | Nullable |
| `ISPOSTED` | `Boolean` | Nullable |
| `INVOICENO` | `String(50, 'SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `INVOICEGENDATE` | `DateTime` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('TRANSID', name='PK_Salik_Toll')
Index('IX_TBL_TOLL_UniqueRecord', 'DATEANDTIME', 'TAGNO', mssql_clustered=False, unique=True)
```

Foreign keys: none declared on this table in the generated snapshot.

### `Staging_Invoice_Header` — `StagingInvoiceHeader`

Source: generated model line 167. Purpose: Candidate invoice staging header; whether mandatory before sales posting unknown.

Primary key: `SIH_ID`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `SIH_ID` | `Integer` | NOT NULL |
| `SIH_LOCATION_ID` | `Integer` | NOT NULL |
| `SIH_INVOICE_TYPE` | `String(2, 'SQL_Latin1_General_CP1_CI_AS')` | NOT NULL |
| `SIH_TRANS_ID` | `Integer` | Nullable |
| `SIH_CONTRACT_ID` | `Integer` | Nullable |
| `SIH_CUST_ID` | `Numeric(18, 0)` | Nullable |
| `SIH_TOTAL_COST` | `DECIMAL(18, 2)` | Nullable |
| `SIH_TAX_AMOUNT` | `DECIMAL(18, 2)` | Nullable |
| `SIH_INVOICE_NO` | `String(50, 'SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `IS_POSTED` | `Boolean` | NOT NULL; default `text('((0))')` |
| `CREATED_BY` | `Integer` | NOT NULL |
| `CREATED_ON` | `DateTime` | NOT NULL |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('SIH_ID', name='PK_Staging_Invoice_Header')
```

Foreign keys: none declared on this table in the generated snapshot.

### `Staging_Invoice_Detail` — `StagingInvoiceDetail`

Source: generated model line 3855. Purpose: Staging lines; explicit header FK present.

Primary key: `SID_ID`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `SID_ID` | `Integer` | NOT NULL |
| `SID_SIH_ID` | `Integer` | NOT NULL |
| `SID_LINE_NO` | `Integer` | NOT NULL |
| `SID_DESCRIPTION` | `Unicode(900, 'SQL_Latin1_General_CP1_CI_AS')` | NOT NULL |
| `SID_AMOUNT` | `DECIMAL(18, 2)` | NOT NULL |
| `SID_VEHICLE_ID` | `Integer` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
ForeignKeyConstraint(['SID_SIH_ID'], ['Staging_Invoice_Header.SIH_ID'], name='FK_SIH_SID')
PrimaryKeyConstraint('SID_ID', name='PK_Staging_Invoice_Detail')
```

### `tbl_SalesMaster` — `TblSalesMaster`

Source: generated model line 3222. Purpose: Candidate sales invoice header and Sales Invoice Register source.

Primary key: `salesMasterId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `salesMasterId` | `Numeric(18, 0)` | NOT NULL |
| `invoiceNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `voucherNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `voucherTypeId` | `Numeric(18, 0)` | Nullable |
| `suffixPrefixId` | `Numeric(18, 0)` | Nullable |
| `date` | `DateTime` | Nullable |
| `ledgerId` | `Numeric(18, 0)` | Nullable |
| `creditPeriod` | `Integer` | NOT NULL |
| `contractId` | `Numeric(18, 0)` | Nullable |
| `contractRefNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `trafficFineNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `taxAmount` | `DECIMAL(18, 5)` | Nullable |
| `totalAmount` | `DECIMAL(18, 5)` | Nullable |
| `grandTotal` | `DECIMAL(18, 5)` | Nullable |
| `isPosted` | `Boolean` | Nullable |
| `financialYearId` | `Numeric(18, 0)` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('salesMasterId', name='PK__tbl_Sale__036BDC222F7AE026')
```

Foreign keys: none declared on this table in the generated snapshot.

### `tbl_SalesDetails` — `TblSalesDetails`

Source: generated model line 3166. Purpose: Candidate invoice lines; master join not enforced by generated FK.

Primary key: `salesDetailsId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `salesDetailsId` | `Numeric(18, 0)` | NOT NULL |
| `salesMasterId` | `Numeric(18, 0)` | Nullable |
| `itemTypeId` | `Numeric(18, 0)` | Nullable |
| `vehicleId` | `Numeric(18, 0)` | Nullable |
| `description` | `Unicode(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `qty` | `DECIMAL(18, 5)` | Nullable |
| `rate` | `DECIMAL(18, 5)` | Nullable |
| `discount` | `DECIMAL(18, 5)` | Nullable |
| `taxId` | `Numeric(18, 0)` | Nullable |
| `taxAmount` | `DECIMAL(18, 5)` | Nullable |
| `netAmount` | `DECIMAL(18, 5)` | Nullable |
| `amount` | `DECIMAL(18, 5)` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('salesDetailsId', name='PK__tbl_Sale__541370DA371C01EE')
```

Foreign keys: none declared on this table in the generated snapshot.

### `tbl_ReceiptMaster` — `TblReceiptMaster`

Source: generated model line 2991. Purpose: Candidate customer collection header / Receipt Register; invoiceNo semantics unconfirmed.

Primary key: `receiptMasterId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `receiptMasterId` | `Numeric(18, 0)` | NOT NULL |
| `voucherNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `invoiceNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `date` | `DateTime` | Nullable |
| `ledgerId` | `Numeric(18, 0)` | Nullable |
| `totalAmount` | `DECIMAL(18, 5)` | Nullable |
| `voucherTypeId` | `Numeric(18, 0)` | Nullable |
| `suffixPrefixId` | `Numeric(18, 0)` | Nullable |
| `financialYearId` | `Numeric(18, 0)` | Nullable |
| `isPosted` | `Boolean` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('receiptMasterId', name='PK__tbl_Rece__B974C2984925A390')
```

Foreign keys: none declared on this table in the generated snapshot.

### `tbl_ReceiptDetails` — `TblReceiptDetails`

Source: generated model line 2973. Purpose: Candidate receipt lines, not a proven direct invoice allocation table.

Primary key: `receiptDetailsId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `receiptDetailsId` | `Numeric(18, 0)` | NOT NULL |
| `receiptMasterId` | `Numeric(18, 0)` | Nullable |
| `ledgerId` | `Numeric(18, 0)` | Nullable |
| `amount` | `DECIMAL(18, 5)` | Nullable |
| `exchangeRateId` | `Numeric(18, 0)` | Nullable |
| `chequeNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `chequeDate` | `DateTime` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('receiptDetailsId', name='PK__tbl_Rece__C0FF33FB6EA14102')
```

Foreign keys: none declared on this table in the generated snapshot.

### `tbl_PartyBalance` — `TblPartyBalance`

Source: generated model line 2519. Purpose: Candidate bill-by-bill settlement bridge; joins/posting rules unknown.

Primary key: `partyBalanceId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `partyBalanceId` | `Numeric(18, 0)` | NOT NULL |
| `ledgerId` | `Numeric(18, 0)` | Nullable |
| `date` | `DateTime` | Nullable |
| `voucherTypeId` | `Numeric(18, 0)` | Nullable |
| `voucherNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `invoiceNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `againstVoucherTypeId` | `Numeric(18, 0)` | Nullable |
| `againstVoucherNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `againstInvoiceNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `referenceType` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `debit` | `DECIMAL(18, 5)` | Nullable |
| `credit` | `DECIMAL(18, 5)` | Nullable |
| `contractId` | `Numeric(18, 0)` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('partyBalanceId', name='PK__tbl_Part__69824BB71C680BB2')
Index('IND1_tbl_PartyBalance', 'date', mssql_clustered=False, mssql_include=['ledgerId', 'againstVoucherTypeId', 'againstVoucherNo', 'againstInvoiceNo', 'debit', 'credit', 'extra1'])
Index('IND2_tbl_PartyBalance', 'ledgerId', 'date', mssql_clustered=False, mssql_include=['againstVoucherTypeId', 'againstVoucherNo', 'againstInvoiceNo', 'debit', 'credit', 'extra1'])
```

Foreign keys: none declared on this table in the generated snapshot.

### `tbl_LedgerPosting` — `TblLedgerPosting`

Source: generated model line 2311. Purpose: Candidate accounting side effect of invoice/receipt posting; not implemented.

Primary key: `ledgerPostingId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `ledgerPostingId` | `Numeric(18, 0)` | NOT NULL |
| `date` | `DateTime` | Nullable |
| `voucherTypeId` | `Numeric(18, 0)` | Nullable |
| `voucherNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `ledgerId` | `Numeric(18, 0)` | Nullable |
| `debit` | `DECIMAL(18, 5)` | Nullable |
| `credit` | `DECIMAL(18, 5)` | Nullable |
| `detailsId` | `Numeric(18, 0)` | Nullable |
| `yearId` | `Numeric(18, 0)` | Nullable |
| `invoiceNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('ledgerPostingId', name='PK__tbl_Ledg__730FE2D769FBBC1F')
Index('IND1_tbl_LedgerPosting', 'date', 'voucherTypeId', mssql_clustered=False, mssql_include=['ledgerId', 'debit', 'credit'])
```

Foreign keys: none declared on this table in the generated snapshot.

### `tbl_PaymentMaster` — `TblPaymentMaster`

Source: generated model line 2606. Purpose: Payment voucher candidate; do not assume this represents customer receipts.

Primary key: `paymentMasterId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `paymentMasterId` | `Numeric(18, 0)` | NOT NULL |
| `voucherNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `invoiceNo` | `String(collation='SQL_Latin1_General_CP1_CI_AS')` | Nullable |
| `ledgerId` | `Numeric(18, 0)` | Nullable |
| `date` | `DateTime` | Nullable |
| `totalAmount` | `DECIMAL(18, 5)` | Nullable |
| `isPosted` | `Boolean` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('paymentMasterId', name='PK__tbl_Paym__F6D0847167001F3A')
```

Foreign keys: none declared on this table in the generated snapshot.

### `tbl_PaymentDetails` — `TblPaymentDetails`

Source: generated model line 2587. Purpose: Payment voucher line candidate; distinct from receipt detail.

Primary key: `paymentDetailsId`. Identity generation is declared for the primary key except Traffic_Fine (identity is on Id).

| Important column | Mapped type | Nullability/default evidence |
| --- | --- | --- |
| `paymentDetailsId` | `Numeric(18, 0)` | NOT NULL |
| `paymentMasterId` | `Numeric(18, 0)` | Nullable |
| `ledgerId` | `Numeric(18, 0)` | Nullable |
| `amount` | `DECIMAL(18, 5)` | Nullable |
| `Vehicle` | `Numeric(18, 0)` | Nullable |

Declared constraints/indexes (verbatim semantics from mapping):

```python
PrimaryKeyConstraint('paymentDetailsId', name='PK__tbl_Paym__2549CB8A6AD0B01E')
```

Foreign keys: none declared on this table in the generated snapshot.

## Required or potentially required lookup/master tables

Selection is limited to existing lookup endpoints and likely prerequisites for the approved workflow. Actual required values are UNKNOWN. Fields shown are mapped scalar columns; no inferred joins are promoted to constraints.

| Actual table / mapped class | Primary key | Important fields | FK / index evidence |
| --- | --- | --- | --- |
| `tbl_AccountGroup` / `TblAccountGroup` | `accountGroupId` | `accountGroupId`, `accountGroupName`, `groupUnder`, `isDefault`, `nature`, `affectGrossProfit` | No FK/additional index declared; PK constraint present. |
| `tbl_Emirate` / `TblEmirate` | `EmirateId` | `EmirateId`, `EmirateName` | No FK/additional index declared; PK constraint present. |
| `tbl_Nationality` / `TblNationality` | `nationality` | `nationality`, `nationalityName` | No FK/additional index declared; PK constraint present. |
| `tbl_Route` / `TblRoute` | `routeId` | `routeId`, `routeName`, `areaId` | `Index('IX_tbl_Route', 'areaId', mssql_clustered=False)` |
| `tbl_Area` / `TblArea` | `areaId` | `areaId`, `areaName` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_StateMaster` / `VTVehStateMaster` | `StateId` | `StateId`, `StateName` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_PlateCategoryMaster` / `VTVehPlateCategoryMaster` | `PlateCategoryId` | `PlateCategoryId`, `PlateCategoryName`, `StateId` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_PlateCodeMaster` / `VTVehPlateCodeMaster` | `PlateCodeId` | `PlateCodeId`, `PlateCodeName`, `PlateCategoryId`, `Code` | `ForeignKeyConstraint(['PlateCategoryId'], ['VT_Veh_StateMaster.StateId'], name='FK_VT_Veh_PlateCodeMaster_VT_Veh_StateMaster')` |
| `VT_Veh_MakeMaster` / `VTVehMakeMaster` | `MakeId` | `MakeId`, `MakeName` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_ModelMaster` / `VTVehModelMaster` | `ModelId` | `ModelId`, `ModelName`, `MakeId` | `ForeignKeyConstraint(['MakeId'], ['VT_Veh_MakeMaster.MakeId'], name='FK_VT_Veh_ModelMaster_VT_Veh_MakeMaster')` |
| `VT_Veh_EngineCapacityMaster` / `VTVehEngineCapacityMaster` | `EngineCapacityId` | `EngineCapacityId`, `EngineCapacity`, `ModelId` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_TypeMaster` / `VTVehTypeMaster` | `TypeId` | `TypeId`, `TypeName` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_FleetTypeMaster` / `VTVehFleetTypeMaster` | `FleetTypeId` | `FleetTypeId`, `FleetTypeName` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_FuelTypeMaster` / `VTVehFuelTypeMaster` | `FuelTypeId` | `FuelTypeId`, `FuelTypeName` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_FuelCapacityUnitMaster` / `VTVehFuelCapacityUnitMaster` | `FuelCapUnitId` | `FuelCapUnitId`, `FuelCapUnit` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_FuelLevelMaster` / `VTVehFuelLevelMaster` | `FuelLevelId` | `FuelLevelId`, `FuelLevel` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_TransmissionMaster` / `VTVehTransmissionMaster` | `TransmissionId` | `TransmissionId`, `TransmissionName` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_ColourMaster` / `VTVehColourMaster` | `ColourId` | `ColourId`, `ColourName` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_InsurancePolicyMaster` / `VTVehInsurancePolicyMaster` | `InsurancePolicyId` | `InsurancePolicyId`, `InsurancePolicyNo`, `Status` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_InsuranceCompanyMaster` / `VTVehInsuranceCompanyMaster` | `InsuranceCompanyId` | `InsuranceCompanyId`, `InsuranceCompanyName` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_InsuranceTypeMaster` / `VTVehInsuranceTypeMaster` | `InsuranceTypeId` | `InsuranceTypeId`, `InsuranceTypeName` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_TCNoMaster` / `VTVehTCNoMaster` | `TCNoId` | `TCNoId`, `TCNo` | No FK/additional index declared; PK constraint present. |
| `VT_Company_BranchMaster` / `VTCompanyBranchMaster` | `BranchId` | `BranchId`, `BranchName`, `CompanyId` | No FK/additional index declared; PK constraint present. |
| `VT_Veh_LocationMaster` / `VTVehLocationMaster` | `LocationId` | `LocationId`, `LocationName` | No FK/additional index declared; PK constraint present. |
| `VT_StatusMaster` / `VTStatusMaster` | `StatusId` | `StatusId`, `StatusName`, `StatusTypeId` | No FK/additional index declared; PK constraint present. |
| `VT_StatusTypeMaster` / `VTStatusTypeMaster` | `StatusTypeId` | `StatusTypeId`, `StatusTypeName` | No FK/additional index declared; PK constraint present. |
| `VT_VehContractStatusMaster` / `VTVehContractStatusMaster` | `VehicleContractStatusId` | `VehicleContractStatusId`, `VehicleContractStatusName` | No FK/additional index declared; PK constraint present. |
| `VT_ContractTypeMaster` / `VTContractTypeMaster` | `ContractTypeId` | `ContractTypeId`, `ContractType`, `ContractTypeDesc`, `LatestCount` | No FK/additional index declared; PK constraint present. |
| `tbl_PaymentMode` / `TblPaymentMode` | `paymentMode` | `paymentMode`, `paymentModeName` | No FK/additional index declared; PK constraint present. |
| `tbl_Tax` / `TblTax` | `taxId` | `taxId`, `taxName`, `applicableOn`, `rate`, `calculatingMode`, `isActive` | `Index('IX_tbl_Tax', 'applicableOn', mssql_clustered=False)`; `Index('IX_tbl_Tax_1', 'taxId', mssql_clustered=False)` |
| `tbl_SalesDetailItemType` / `TblSalesDetailItemType` | `ItemType` | `ItemType`, `ItemTypeName`, `ItemTypeNameArabic`, `VoucherType`, `IsActive`, `TaxId`, `updatedBy` | No FK/additional index declared; PK constraint present. |
| `tbl_VoucherType` / `TblVoucherType` | `voucherTypeId` | `voucherTypeId`, `voucherTypeName`, `typeOfVoucher`, `methodOfVoucherNumbering`, `isTaxApplicable`, `isActive`, `isDefault`, `masterId`, `declaration` | No FK/additional index declared; PK constraint present. |
| `tbl_SuffixPrefix` / `TblSuffixPrefix` | `suffixprefixId` | `suffixprefixId`, `voucherTypeId`, `fromDate`, `toDate`, `startIndex`, `prefix`, `suffix`, `widthOfNumericalPart`, `prefillWithZero` | No FK/additional index declared; PK constraint present. |
| `tbl_FinancialYear` / `TblFinancialYear` | `financialYearId` | `financialYearId`, `fromDate`, `toDate` | No FK/additional index declared; PK constraint present. |

## Additional candidates needing evidence

Generated Core tables such as `INSALIK`, `Salik_Invoice_Temp` and contract history/closing-charge tables also exist. They are not selected as authoritative workflow stores without evidence of their use. `tbl_AdvancePayment` contains employee/salary fields; do not assume it is a rental-deposit table based on its name. Broad ERP/payroll/inventory tables are intentionally omitted.

Next database investigation: read-only live metadata comparison, then trace one approved completed rental through customer, vehicle, tariff, contract, out/in, charges, invoice, receipt and postings. Confirm procedures/triggers and status values before implementing writes. No live queries were made by this audit.

## Vehicle screen-to-database addendum — 2026-09-06

This section supplements the earlier catalogue with every Vehicle screenshot field and the complete relevant master columns. Evidence is generated source plus three still screenshots, not live MSSQL. Primary keys and constraints below are confirmed in the snapshot only; UI matches are candidates and relationship classifications follow [RELATIONSHIPS.md](RELATIONSHIPS.md).

### Screen fields → candidate persistence

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

### Group name and rate storage

Both tariff screens match `VT_Veh_TariffGroupMaster` / `VTVehTariffGroupMaster`: identity integer PK `TariffGroupId`, required Unicode(100) `TariffGroupName`, plus these 17 nullable DECIMAL(18,2) fields. No server defaults, name-uniqueness index, range/check constraint, or FK is declared on that model. PK enforces one mapped row/rate set per group ID, not one row per unique name. Separate screens do not imply separate tables.

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

The columns all exist. Null/zero distinction, rate validation, rounding/currency and effects on current contracts are unconfirmed. Existing GET `/lookups/tariff-groups` queries this model, but actual response serialization was not tested. Vehicle.TariffGroupId is required but has no declared FK to it. Do not delete groups based only on absent constraints.

### Vehicle master constraints and non-screen requirements

The existing core entry records every declared VehicleMaster FK and PK. No additional index/unique constraint for PlateNo, ChasisNo or EngineNo appears in the generated mapping; duplicate records are a possibility, not an observed fact. Live defaults/triggers may differ from the snapshot.

There is no FleetNo, EmirateId, StateId, MakeId or Narration column on VehicleMaster. InsuranceTypeId is NOT NULL but no distinct insurance-type control is visible. InsurancePolicyRecNo may match the unlabeled box but that is unconfirmed. LatestKmRdg, CreatedBy, CreatedDate, LastUpdatedBy and LastUpdatedDate are NOT NULL without declared server defaults and are not shown as controls. Create must obtain verified values through normal application logic rather than arbitrary placeholders. Optional mapped fields include Remarks, BranchId, LocId, VHType, FuelLevel and other operational fields. Do not overwrite them accidentally when implementing edits to this screen.

### Relevant lookup/master metadata and UI association

All listed lookup primary keys declare identity generation. No additional indexes/check constraints are declared on these lookup classes; FK/PK constraints shown below are the complete `__table_args__` for each selected class. This absence applies to the mapping snapshot only.

#### `VT_Veh_StateMaster` / `VTVehStateMaster`

UI role: Emirate candidate; current GET states. Source model line 896. PK: `StateId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `StateId` | `Integer` | Yes |
| `StateName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('StateId', name='PK_VT_StateMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `tbl_Emirate` / `TblEmirate`

UI role: Alternative Emirate source; current customer field domain, not a proven Vehicle source. Source model line 1934. PK: `EmirateId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `EmirateId` | `Numeric(18, 0)` | Yes |
| `EmirateName` | `String(50, 'SQL_Latin1_General_CP1_CI_AS')` | No |

```python
PrimaryKeyConstraint('EmirateId', name='PK_tbl_Emirate')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_PlateCategoryMaster` / `VTVehPlateCategoryMaster`

UI role: Intermediate plate category absent from screenshot. Source model line 850. PK: `PlateCategoryId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `PlateCategoryId` | `Integer` | Yes |
| `PlateCategoryName` | `String(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |
| `StateId` | `Integer` | Yes |

```python
PrimaryKeyConstraint('PlateCategoryId', name='PK_VT_Veh_PlateCategoryMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_PlateCodeMaster` / `VTVehPlateCodeMaster`

UI role: Plate Code. Source model line 3903. PK: `PlateCodeId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `PlateCodeId` | `Integer` | Yes |
| `PlateCodeName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |
| `PlateCategoryId` | `Integer` | Yes |
| `Code` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | No |

```python
ForeignKeyConstraint(['PlateCategoryId'], ['VT_Veh_StateMaster.StateId'], name='FK_VT_Veh_PlateCodeMaster_VT_Veh_StateMaster')
PrimaryKeyConstraint('PlateCodeId', name='PK_VT_PlateCodeMaster')
```

CONFIRMED DATABASE RELATIONSHIP for the explicit FK above (snapshot only). UI binding still needs validation.

#### `VT_Veh_MakeMaster` / `VTVehMakeMaster`

UI role: Make. Source model line 838. PK: `MakeId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `MakeId` | `Integer` | Yes |
| `MakeName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('MakeId', name='PK_VT_Veh_Make')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_ModelMaster` / `VTVehModelMaster`

UI role: Model and derived Make. Source model line 3888. PK: `ModelId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `ModelId` | `Integer` | Yes |
| `ModelName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |
| `MakeId` | `Integer` | Yes |

```python
ForeignKeyConstraint(['MakeId'], ['VT_Veh_MakeMaster.MakeId'], name='FK_VT_Veh_ModelMaster_VT_Veh_MakeMaster')
PrimaryKeyConstraint('ModelId', name='PK_VT_Veh_ModelMaster')
```

CONFIRMED DATABASE RELATIONSHIP for the explicit FK above (snapshot only). UI binding still needs validation.

#### `VT_Veh_EngineCapacityMaster` / `VTVehEngineCapacityMaster`

UI role: Engine capacity. Source model line 742. PK: `EngineCapacityId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `EngineCapacityId` | `Integer` | Yes |
| `EngineCapacity` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |
| `ModelId` | `Integer` | Yes |

```python
PrimaryKeyConstraint('EngineCapacityId', name='PK_VT_Veh_EngineCapacityMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_TypeMaster` / `VTVehTypeMaster`

UI role: Veh Type candidate. Source model line 975. PK: `TypeId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `TypeId` | `Integer` | Yes |
| `TypeName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('TypeId', name='PK_VT_Veh_TypeMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_FuelTypeMaster` / `VTVehFuelTypeMaster`

UI role: Fuel Type. Source model line 787. PK: `FuelTypeId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `FuelTypeId` | `Integer` | Yes |
| `FuelTypeName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('FuelTypeId', name='PK_VT_Veh_FuelTypeMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_FuelCapacityUnitMaster` / `VTVehFuelCapacityUnitMaster`

UI role: Fuel capacity unit. Source model line 765. PK: `FuelCapUnitId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `FuelCapUnitId` | `Integer` | Yes |
| `FuelCapUnit` | `Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('FuelCapUnitId', name='PK_VT_Veh_FuelCapacityUnitMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_FleetTypeMaster` / `VTVehFleetTypeMaster`

UI role: No proven screen field; second FK on FuelCapacityUnitId, not Fleet No evidence. Source model line 753. PK: `FleetTypeId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `FleetTypeId` | `Integer` | Yes |
| `FleetTypeName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('FleetTypeId', name='PK_VT_Veh_FleetTypeMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_TransmissionMaster` / `VTVehTransmissionMaster`

UI role: Transmission. Source model line 963. PK: `TransmissionId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `TransmissionId` | `Integer` | Yes |
| `TransmissionName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('TransmissionId', name='PK_VT_Veh_TransmissionMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_ColourMaster` / `VTVehColourMaster`

UI role: Color. Source model line 730. PK: `ColourId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `ColourId` | `Integer` | Yes |
| `ColourName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('ColourId', name='PK_VT_Veh_ColourMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_InsurancePolicyMaster` / `VTVehInsurancePolicyMaster`

UI role: Policy. Source model line 807. PK: `InsurancePolicyId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `InsurancePolicyId` | `Integer` | Yes |
| `InsurancePolicyNo` | `Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |
| `Status` | `Boolean` | No |

```python
PrimaryKeyConstraint('InsurancePolicyId', name='PK_VT_Veh_InsurancePolicyMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_InsuranceCompanyMaster` / `VTVehInsuranceCompanyMaster`

UI role: Insurance Company. Source model line 797. PK: `InsuranceCompanyId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `InsuranceCompanyId` | `Integer` | Yes |
| `InsuranceCompanyName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('InsuranceCompanyId', name='PK_VT_Veh_InsuranceCompanyMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_InsuranceTypeMaster` / `VTVehInsuranceTypeMaster`

UI role: Required model field with no separate visible control. Source model line 818. PK: `InsuranceTypeId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `InsuranceTypeId` | `Integer` | Yes |
| `InsuranceTypeName` | `Unicode(100, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('InsuranceTypeId', name='PK_VT_Veh_InsuranceTypeMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_TCNoMaster` / `VTVehTCNoMaster`

UI role: Vehicle TC No. Source model line 926. PK: `TCNoId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `TCNoId` | `Integer` | Yes |
| `TCNo` | `Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('TCNoId', name='PK_VT_Veh_TCNoMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Company_BranchMaster` / `VTCompanyBranchMaster`

UI role: Branch. Source model line 317. PK: `BranchId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `BranchId` | `Integer` | Yes |
| `BranchName` | `Unicode(150, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |
| `CompanyId` | `Integer` | Yes |

```python
PrimaryKeyConstraint('BranchId', name='PK_VT_Company_BranchMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_Veh_LocationMaster` / `VTVehLocationMaster`

UI role: Location candidate. Source model line 828. PK: `LocationId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `LocationId` | `Integer` | Yes |
| `LocationName` | `String(50, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('LocationId', name='PK_VT_Veh_LocationMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_StatusMaster` / `VTStatusMaster`

UI role: Vehicle Status candidate. Source model line 651. PK: `StatusId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `StatusId` | `Integer` | Yes |
| `StatusName` | `Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |
| `StatusTypeId` | `Integer` | Yes |

```python
PrimaryKeyConstraint('StatusId', name='PK_VT_StatusMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

#### `VT_StatusTypeMaster` / `VTStatusTypeMaster`

UI role: Status-domain filter candidate; no visible control. Source model line 662. PK: `StatusTypeId`.

| Column | Type | Required in mapping |
| --- | --- | --- |
| `StatusTypeId` | `Integer` | Yes |
| `StatusTypeName` | `Unicode(50, 'SQL_Latin1_General_CP1_CI_AS')` | Yes |

```python
PrimaryKeyConstraint('StatusTypeId', name='PK_VT_StatusTypeMaster')
```

No FK declared on this lookup. Any proposed association beyond a separately documented inbound FK is SUSPECTED RELATIONSHIP or UNKNOWN.

### Lookup/data verification gaps

The existing API exposes states, categories, codes, makes, models, capacities, types, fuel types/units, transmission, colours, insurance policies/companies, TC numbers, tariff groups, branches, locations and statuses. It does not expose insurance types, status types or a dedicated year list. Whether fleet type needs a control is UNKNOWN; do not add one based on the anomalous FK alone. LocationMaster has no BranchId, and InsurancePolicyMaster has no InsuranceCompanyId in the mapping, so those filtered dropdown dependencies cannot be assumed.

Before writes, compare live metadata read-only for the two anomalous FKs and inspect approved sample rows for missing lookup references, duplicate plate/group names, status domains and null pricing values. Check actual triggers/procedures and referencing transactions. No live data anomaly has been established by this documentation task.
