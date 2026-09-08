"""Contract service regression tests using isolated SQLite, never the configured MSSQL."""
import unittest
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from pypdf import PdfReader
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    MetaData,
    Numeric,
    String,
    Table as TableCopy,
    create_engine,
    select,
)
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.contracts import repository as contracts
from app.contracts import service as contract_service
from app.generated_models.models import Base
from app.lookups import repository as lookups
from app.contracts.schemas import (
    ContractCreate,
    ContractDriverCreate,
    ContractDriverResponse,
    ContractDriverUpdate,
    ContractResponse,
    ContractPrintData,
    ContractViewRow,
)


def _sqlite_type(column):
    if isinstance(column.type, (Integer, BigInteger)):
        return Integer()
    if isinstance(column.type, DateTime):
        return DateTime()
    if isinstance(column.type, Boolean):
        return Boolean()
    if isinstance(column.type, Numeric):
        return Numeric(18, 5)
    return String()


def _copy_table(name, metadata):
    source = Base.metadata.tables[name]
    return TableCopy(
        name,
        metadata,
        *[
            Column(column.name, _sqlite_type(column), primary_key=column.primary_key, nullable=column.nullable)
            for column in source.c
        ],
    )


def _default_value(column):
    if isinstance(column.type, DateTime):
        return datetime(2026, 1, 1)
    if isinstance(column.type, Boolean):
        return False
    if isinstance(column.type, Numeric):
        return Decimal("1")
    if isinstance(column.type, (Integer, BigInteger)):
        return 1
    return "test"


def _required_values(table, **overrides):
    values = {
        column.name: _default_value(column)
        for column in table.c
        if column.primary_key or not column.nullable
    }
    values.update(overrides)
    return values


class ContractAPI(unittest.TestCase):
    TABLES = {
        "tbl_AccountLedger",
        "VT_Veh_VehicleMaster",
        "VT_Veh_ModelMaster",
        "VT_Veh_MakeMaster",
        "VT_Veh_ColourMaster",
        "VT_Veh_PlateCodeMaster",
        "VT_Veh_TariffGroupMaster",
        "VT_ContractMaster",
        "VT_ContractDriverDtls",
        "VT_ContractVehicleMaster",
        "tbl_VehicleContractType",
        "VT_Veh_LocationMaster",
        "tbl_PaymentMode",
        "VT_DiscountType",
        "tbl_SalesInvoiceBillingType",
        "VT_VisaType",
        "VT_DLTypes",
        "VT_Nationality",
        "VT_Veh_FuelLevelMaster",
        "tbl_Employee",
        "VT_ApplicationUsers",
        "VT_LookupTable",
        "VT_StatusMaster",
    }

    def setUp(self):
        self.engine = create_engine("sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False})
        self.metadata = MetaData()
        self.tables = {name: _copy_table(name, self.metadata) for name in self.TABLES}
        self.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self._seed_reference_data()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def _insert_required(self, table_name, **overrides):
        table = self.tables[table_name]
        self.db.execute(table.insert().values(**_required_values(table, **overrides)))

    def _seed_reference_data(self):
        self._insert_required("VT_Veh_MakeMaster", MakeId=1, MakeName="MG")
        self._insert_required("VT_Veh_ModelMaster", ModelId=1, ModelName="MG 5", MakeId=1)
        self._insert_required("VT_Veh_ColourMaster", ColourId=1, ColourName="SILVER")
        self._insert_required("VT_Veh_PlateCodeMaster", PlateCodeId=1, PlateCodeName="", Code="")
        self._insert_required(
            "VT_Veh_TariffGroupMaster",
            TariffGroupId=1,
            TariffGroupName="MG5",
            AllowedKmsPerDay=Decimal("83.33"),
        )
        self._insert_required(
            "tbl_AccountLedger",
            ledgerId=138274,
            accountGroupId=26,
            ledgerName="EZhire",
            phone="050",
            mobile="050",
            email="",
            address="AL QUOZ",
            CustomerIdNo="784198339777405",
            CustomerIdExpiry=datetime(2028, 5, 7),
            isCorporate=True,
        )
        self._insert_required(
            "VT_Veh_VehicleMaster",
            VehicleId=34,
            StatusId=1,
            LatestKmRdg=1234,
            PlateNo="DD 95117",
            VHType="34",
        )
        self._insert_required("tbl_VehicleContractType", contractType=1, contractTypeName="Daily", contractTypeCode="DLY")
        self._insert_required("VT_Veh_LocationMaster", LocationId=1, LocationName="AL QUOZ")
        self._insert_required("tbl_PaymentMode", paymentMode=1, paymentModeName="Cash")
        self._insert_required("VT_DiscountType", DiscountTypeId=1, DiscountType="%")
        self._insert_required("tbl_SalesInvoiceBillingType", invoiceTypeId=2, invoiceTypeName="Date to Date")
        self._insert_required("VT_VisaType", Id=1, Name="Residence")
        self._insert_required("VT_DLTypes", DLTypeId=1, DLTypeName="UAE")
        self._insert_required("VT_Nationality", NationalityId="SGP", NationalityName="Singapore")
        self._insert_required("VT_Veh_FuelLevelMaster", FuelLevelId=1, FuelLevel="1/4")
        self._insert_required("tbl_Employee", employeeId=1, employeeName="Sales", employeeCode="1")
        self._insert_required("VT_ApplicationUsers", UserID=12, UserName="muhsin", DisplayName="muhsin")
        for lookup_id, value, description, lookup_type in [
            (2, 2, "Referral", "CustomerSource"),
            (4, 1, "LPO", "Corporate"),
            (9, 3, "Others", "Individual"),
            (10, 1, "Corporate", "CustomerType"),
            (11, 2, "Individual", "CustomerType"),
        ]:
            self._insert_required(
                "VT_LookupTable",
                LookupId=lookup_id,
                LookupValue=value,
                LookupDescription=description,
                LookupType=lookup_type,
            )
        self._insert_required("VT_StatusMaster", StatusId=8, StatusName="OPEN", StatusTypeId=2)
        self.db.commit()

    def _payload(self, **changes):
        payload = {
            "ContractRefNo": 3407,
            "ContractType": 1,
            "ContractStartDate": "2026-09-05T00:00:00",
            "ContractExpectedEndDate": "2026-09-06T00:00:00",
            "ContractLocId": 1,
            "CustomerId": 138274,
            "UserName": "322384 - MOHAMED TASHRIQ",
            "VehicleId": 34,
            "DateOfBirth": "1997-12-04T00:00:00",
            "Nationality": "sgp",
            "VisaType": 1,
            "VisaExpiryDate": "2026-11-05T00:00:00",
            "DrivingLicenseType": 1,
            "DrivingLicenseNo": "4516550",
            "DLPlaceOfIssue": "DUBAI",
            "DLIssueDate": "2023-07-06T00:00:00",
            "DLExpiryDate": "2028-07-06T00:00:00",
            "PaymentMode": 1,
            "Rate": "100.00",
            "OtherCharges": "12.50",
            "Subtotal": "112.50",
            "DatetimeOut": "2026-09-05T12:43:00",
            "KmOut": 1234,
            "FuelLevelIdOut": 1,
            "CheckedOutBy": 12,
            "SalesPersonId": 1,
            "CreatedBy": 12,
        }
        payload.update(changes)
        return payload

    def test_contract_create_inserts_header_driver_and_vehicle_without_status_change(self):
        body = contract_service.create_contract(self.db, ContractCreate(**self._payload()))
        ContractResponse.model_validate(body)
        self.assertEqual(body["ContractRefNo"], "3407")
        self.assertEqual(body["RTACode"], "3407")
        self.assertEqual(body["CustomerId"], 138274)
        self.assertEqual(body["CustomerName"], "EZhire")
        self.assertEqual(body["UserName"], "322384 - MOHAMED TASHRIQ")
        self.assertEqual(body["PassportNo"], "784198339777405")
        self.assertEqual(body["PaymentType"], 1)
        self.assertEqual(body["PaymentMode"], 1)
        self.assertEqual(body["BillingType"], 2)
        self.assertEqual(body["Status"], contract_service.CONTRACT_STATUS_OPEN)
        self.assertEqual(body["CustomerType"], contract_service.CORPORATE_CUSTOMER_TYPE)
        self.assertEqual(body["ConfirmationRefType"], contract_service.CORPORATE_CONFIRMATION_REF)
        self.assertEqual(Decimal(body["OtherCharges"]), Decimal("12.50"))
        self.assertEqual(body["driver"]["PassportNo"], "784198339777405")
        self.assertEqual(body["driver"]["DriverStatus"], contract_service.DRIVER_STATUS_OPEN)
        self.assertEqual(body["vehicle_assignment"]["ContractVehicleStatus"], contract_service.CONTRACT_VEHICLE_STATUS_ACTIVE)
        self.assertEqual(body["vehicle_assignment"]["LocationOut"], 1)

        vehicle_status = self.db.execute(
            select(contracts.VEHICLE_TABLE.c.StatusId).where(contracts.VEHICLE_TABLE.c.VehicleId == 34)
        ).scalar_one()
        self.assertEqual(vehicle_status, 1)

    def test_contract_create_rejects_unknown_customer_and_reference(self):
        with self.assertRaisesRegex(Exception, "CustomerId"):
            contract_service.create_contract(self.db, ContractCreate(**self._payload(CustomerId=999)))
        with self.assertRaisesRegex(Exception, "PaymentMode"):
            contract_service.create_contract(self.db, ContractCreate(**self._payload(PaymentMode=99)))

    def test_contract_lookup_endpoints(self):
        contract_service.create_contract(self.db, ContractCreate(**self._payload()))
        self.assertEqual(lookups.get_contract_types(self.db)[0]["contractTypeName"], "Daily")
        self.assertEqual(lookups.get_payment_modes(self.db)[0]["paymentModeName"], "Cash")
        self.assertEqual(lookups.get_billing_types(self.db)[0]["invoiceTypeName"], "Date to Date")
        self.assertEqual(lookups.get_application_users(self.db)[0]["UserName"], "muhsin")
        self.assertEqual(lookups.get_customer_users(self.db, 138274)[0]["UserName"], "322384 - MOHAMED TASHRIQ")
        self.assertEqual(lookups.get_customer_users(self.db, 138274)[0]["PassportNo"], "784198339777405")
        self.assertEqual(lookups.get_customers_lookup(self.db, q="EZ")[0]["ledgerName"], "EZhire")

    def test_contract_view_lists_grid_fields_and_filters(self):
        contract_service.create_contract(
            self.db,
            ContractCreate(
                **self._payload(
                    Rate="400.00",
                    SalikCharges="10.00",
                    TrafficCharges="50.00",
                    Advance="100.00",
                )
            ),
        )

        rows = contract_service.list_contract_view(self.db)
        ContractViewRow.model_validate(rows[0])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["slNo"], 1)
        self.assertIsInstance(rows[0]["assignmentId"], int)
        self.assertEqual(rows[0]["agreementNo"], "3407")
        self.assertEqual(rows[0]["customer"], "EZhire")
        self.assertEqual(rows[0]["vehicle"], "DD 95117")
        self.assertEqual(rows[0]["totalDays"], 1)
        self.assertEqual(rows[0]["rent"], Decimal("400.00"))
        self.assertEqual(rows[0]["salik"], Decimal("10.00"))
        self.assertEqual(rows[0]["fine"], Decimal("50.00"))
        self.assertEqual(rows[0]["received"], Decimal("100.00"))
        self.assertEqual(rows[0]["pendingAmount"], Decimal("360.00"))

        self.assertEqual(len(contract_service.list_contract_view(self.db, customer_name="hire")), 1)
        self.assertEqual(len(contract_service.list_contract_view(self.db, agreement_no="3407")), 1)
        self.assertEqual(contract_service.list_contract_view(self.db, agreement_no="407"), [])
        self.assertEqual(len(contract_service.list_contract_view(self.db, vehicle="95117")), 1)
        self.assertEqual(contract_service.list_contract_view(self.db, vehicle="missing"), [])

    def test_contract_print_data_uses_selected_assignment_and_only_applicable_rate(self):
        contract = contract_service.create_contract(self.db, ContractCreate(**self._payload()))
        assignment_id = contract["vehicle_assignment"]["Id"]

        result = contract_service.get_contract_print_data(self.db, contract["ContractId"], assignment_id)

        ContractPrintData.model_validate(result)
        self.assertEqual(result["assignmentId"], assignment_id)
        self.assertEqual(result["agreementNo"], "3407")
        self.assertEqual(result["hirerName"], "322384 - MOHAMED TASHRIQ")
        self.assertEqual(result["nationality"], "Singapore")
        self.assertEqual(result["vehicleMake"], "MG")
        self.assertEqual(result["vehicleModel"], "MG 5")
        self.assertEqual(result["plateNumber"], "DD 95117")
        self.assertEqual(result["colour"], "SILVER")
        self.assertEqual(result["dailyPrice"], Decimal("100.00"))
        self.assertIsNone(result["weeklyPrice"])
        self.assertIsNone(result["monthlyPrice"])
        self.assertEqual(result["allowedKm"], Decimal("83.33"))
        self.assertEqual(result["otherCharges"], Decimal("12.50"))

        with self.assertRaisesRegex(Exception, "assignment"):
            contract_service.get_contract_print_data(self.db, contract["ContractId"], 999)

    def test_contract_print_pdf_preserves_two_page_template_and_adds_values(self):
        contract = contract_service.create_contract(self.db, ContractCreate(**self._payload()))
        assignment_id = contract["vehicle_assignment"]["Id"]

        content, agreement_no = contract_service.get_contract_print_pdf(
            self.db, contract["ContractId"], assignment_id
        )

        self.assertEqual(agreement_no, "3407")
        self.assertTrue(content.startswith(b"%PDF"))
        rendered = PdfReader(BytesIO(content))
        self.assertEqual(len(rendered.pages), 2)
        self.assertAlmostEqual(float(rendered.pages[0].mediabox.width), 593.343, places=2)
        self.assertAlmostEqual(float(rendered.pages[0].mediabox.height), 840.876, places=2)
        extracted = "\n".join(page.extract_text() or "" for page in rendered.pages)
        self.assertIn("3407", extracted)
        self.assertIn("DD 95117", extracted)

    def test_contract_driver_crud(self):
        contract = contract_service.create_contract(self.db, ContractCreate(**self._payload()))
        driver_payload = ContractDriverCreate(
            ContractId=contract["ContractId"],
            UserName="443322 - SECOND DRIVER",
            Address="Dubai",
            Mobile="0501234567",
            Email="driver@example.test",
            DateOfBirth=datetime(1990, 1, 1),
            NationalityId="SGP",
            PassportNo="784199000000000",
            PassportExpiryDate=datetime(2030, 1, 1),
            VisaType=1,
            VisaExpiryDate=datetime(2029, 1, 1),
            DrivingLicenseType=1,
            DrivingLicenseNo="DL123",
            DLPlaceOfIssue="DUBAI",
            DLIssueDate=datetime(2020, 1, 1),
            DLExpiryDate=datetime(2030, 1, 1),
            Phone="04",
            Fax="0",
        )
        created = contract_service.create_driver(self.db, driver_payload)
        ContractDriverResponse.model_validate(dict(created))
        self.assertEqual(created["UserName"], "443322 - SECOND DRIVER")
        self.assertEqual(len(contract_service.list_drivers(self.db, contract_id=contract["ContractId"])), 2)

        updated = contract_service.update_driver(
            self.db,
            created["ContractDriverId"],
            ContractDriverUpdate(UserName="443322 - UPDATED DRIVER", Mobile="0507654321"),
        )
        self.assertEqual(updated["UserName"], "443322 - UPDATED DRIVER")
        self.assertEqual(updated["Mobile"], "0507654321")

        contract_service.delete_driver(self.db, created["ContractDriverId"])
        with self.assertRaisesRegex(Exception, "Contract driver not found"):
            contract_service.get_driver_detail(self.db, created["ContractDriverId"])


if __name__ == "__main__":
    unittest.main()
