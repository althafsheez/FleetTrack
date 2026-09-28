"""Rental billing calculation tests; all database calls are mocked."""
import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from fastapi import HTTPException

from app.rental_billing import service
from app.rental_billing.schemas import RentalInvoiceSettings


def _contract(**changes):
    values = {
        "ContractId": 42,
        "ContractRefNo": "R-42",
        "RTACode": "R-42",
        "Status": 8,
        "PaymentType": 3,
        "BillingType": 2,
        "IsAdvanceInvoice": True,
        "ContractStartDate": datetime(2026, 9, 10),
        "NextInvStDate": datetime(2026, 9, 10),
        "LastInvoiceDate": None,
        "Rate": Decimal("3000"),
        "DiscountType": 1,
        "Discount": Decimal("10"),
        "DriverCharges": Decimal("100"),
        "AddDriverCharges": Decimal("0"),
        "CDW": Decimal("50"),
        "PAI": Decimal("0"),
        "CustomerId": 11,
        "SalesPersonId": 3,
        "ContractLocId": 4,
    }
    values.update(changes)
    return values


class RentalBillingTests(unittest.TestCase):
    def test_monthly_date_to_date_advance_period(self):
        start, end, invoice_date, next_date = service._schedule(_contract(), initial=True)
        self.assertEqual(start, datetime(2026, 9, 10))
        self.assertEqual(end, datetime(2026, 10, 9))
        self.assertEqual(invoice_date, datetime(2026, 9, 10))
        self.assertEqual(next_date, datetime(2026, 10, 10))

    def test_month_end_non_advance_period(self):
        contract = _contract(
            BillingType=1,
            IsAdvanceInvoice=False,
            ContractStartDate=datetime(2026, 9, 18),
            LastInvoiceDate=datetime(2026, 9, 18),
            NextInvStDate=datetime(2026, 10, 1),
        )
        start, end, invoice_date, next_date = service._schedule(contract, initial=False)
        self.assertEqual(start, datetime(2026, 9, 18))
        self.assertEqual(end, datetime(2026, 9, 30))
        self.assertEqual(invoice_date, datetime(2026, 10, 1))
        self.assertEqual(next_date, datetime(2026, 11, 1))

    def test_weekly_period(self):
        contract = _contract(
            PaymentType=2,
            IsAdvanceInvoice=False,
            ContractStartDate=datetime(2026, 9, 1),
            LastInvoiceDate=datetime(2026, 9, 1),
            NextInvStDate=datetime(2026, 9, 8),
        )
        start, end, invoice_date, next_date = service._schedule(contract, initial=False)
        self.assertEqual(start, datetime(2026, 9, 1))
        self.assertEqual(end, datetime(2026, 9, 7))
        self.assertEqual(invoice_date, datetime(2026, 9, 8))
        self.assertEqual(next_date, datetime(2026, 9, 15))

    def test_advance_monthly_recurring_period_uses_the_next_anniversary(self):
        contract = _contract(
            ContractStartDate=datetime(2026, 9, 10),
            NextInvStDate=datetime(2026, 10, 10),
            LastInvoiceDate=datetime(2026, 9, 10),
        )
        start, end, invoice_date, next_date = service._schedule(contract, initial=False)
        self.assertEqual(start, datetime(2026, 10, 10))
        self.assertEqual(end, datetime(2026, 11, 9))
        self.assertEqual(invoice_date, datetime(2026, 10, 10))
        self.assertEqual(next_date, datetime(2026, 11, 10))

    def test_daily_contract_is_not_billable_in_this_release(self):
        with self.assertRaises(HTTPException) as error:
            service._require_contract(_contract(PaymentType=1))
        self.assertEqual(error.exception.status_code, 422)

    @patch("app.rental_billing.service.sales_repo.get_item_type_by_name")
    @patch("app.rental_billing.service.sales_repo.get_unit_by_name")
    @patch("app.rental_billing.service.sales_repo.get_voucher_type")
    @patch("app.rental_billing.service.repo.get_current_vehicle_assignment")
    def test_builds_legacy_charge_lines_from_contract_values(self, assignment, voucher, unit, item):
        assignment.return_value = {"VehicleId": 99}
        voucher.return_value = {"voucherTypeId": 31}
        unit.return_value = {"unitId": 2}
        item.side_effect = [
            {"ItemType": 1, "TaxId": 2},
            {"ItemType": 2, "TaxId": 2},
            {"ItemType": 4, "TaxId": 2},
        ]
        payload, start, end, next_date, names = service._build_input(
            None,
            _contract(),
            RentalInvoiceSettings(salesAccountId=50, exchangeRateId=1),
            initial=True,
        )

        self.assertEqual((start, end, next_date), (datetime(2026, 9, 10), datetime(2026, 10, 9), datetime(2026, 10, 10)))
        self.assertEqual([line.itemTypeId for line in payload.lines], [1, 2, 4])
        self.assertEqual([line.rate for line in payload.lines], [Decimal("2700"), Decimal("100"), Decimal("50")])
        self.assertEqual(names[1], "Rental Rate")
        self.assertEqual(names[2], "Rental Driver Charges")
        self.assertEqual(names[4], "Rental CDW")

    @patch("app.rental_billing.service.sales_service.create_draft_in_transaction")
    @patch("app.rental_billing.service.repo.has_rental_invoice_for_schedule", return_value=False)
    @patch("app.rental_billing.service.repo.update_schedule")
    @patch("app.rental_billing.service._preview")
    @patch("app.rental_billing.service.repo.get_contract")
    def test_creation_advances_next_due_date_but_records_actual_invoice_date(
        self, get_contract, preview, update_schedule, _duplicate, create_draft
    ):
        contract = _contract(
            IsAdvanceInvoice=False,
            ContractStartDate=datetime(2026, 9, 1),
            LastInvoiceDate=datetime(2026, 9, 1),
            NextInvStDate=datetime(2026, 10, 1),
        )
        payload = Mock(invoiceDate=datetime(2026, 10, 1))
        get_contract.return_value = contract
        preview.return_value = ({}, payload, datetime(2026, 11, 1))
        create_draft.return_value = {"salesMasterId": 99}
        db = Mock()

        service._create_invoice(
            db, 42, RentalInvoiceSettings(salesAccountId=50, exchangeRateId=1), 7, initial=False,
            as_of_date=datetime(2026, 10, 1),
        )

        update_schedule.assert_called_once_with(db, 42, datetime(2026, 11, 1), datetime(2026, 10, 1))

    @patch("app.rental_billing.service.sales_repo.delete_draft")
    @patch("app.rental_billing.service.repo.update_schedule")
    @patch("app.rental_billing.service.repo.previous_rental_invoice")
    @patch("app.rental_billing.service.repo.latest_rental_invoice")
    @patch("app.rental_billing.service.sales_repo.get_invoice_header")
    @patch("app.rental_billing.service.repo.get_contract")
    def test_deleting_latest_nonadvance_draft_restores_the_previous_period(
        self, get_contract, get_header, latest, previous, update_schedule, delete_draft
    ):
        db = Mock()
        invoice_date = datetime(2026, 11, 1)
        previous_date = datetime(2026, 10, 1)
        get_contract.return_value = _contract(IsAdvanceInvoice=False)
        get_header.return_value = {
            "salesMasterId": 99, "voucherTypeId": 31, "contractId": 42,
            "isPosted": False, "date": invoice_date, "voucherNo": "RI000099",
        }
        latest.return_value = {"salesMasterId": 99}
        previous.return_value = {"salesMasterId": 98, "date": previous_date}

        service.delete_invoice(db, 42, 99)

        delete_draft.assert_called_once_with(db, 99, 31, "RI000099")
        update_schedule.assert_called_once_with(db, 42, invoice_date, previous_date)
        db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
