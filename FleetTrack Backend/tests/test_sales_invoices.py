"""Sales Invoice lookup/source tests using mocks only; no MSSQL writes occur."""
import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from fastapi import HTTPException

from app.sales_invoices import repository as repo
from app.sales_invoices import router, service


class SalesInvoiceLookupAndSourceTests(unittest.TestCase):
    def test_numbering_rule_route_precedes_dynamic_lookup_route(self):
        paths = [route.path for route in router.router.routes]
        self.assertLess(paths.index("/sales-invoices/lookups/numbering-rule"), paths.index("/sales-invoices/lookups/{name}"))

    @patch.object(repo, "get_suffix_prefix")
    @patch.object(repo, "get_voucher_type")
    def test_numbering_rule_returns_configured_rule(self, voucher_type, suffix_prefix):
        voucher_type.return_value = {"voucherTypeId": 31}
        suffix_prefix.return_value = {
            "suffixprefixId": 7,
            "prefix": "RI",
            "suffix": None,
            "startIndex": 1000,
            "widthOfNumericalPart": 6,
            "prefillWithZero": True,
            "fromDate": datetime(2026, 1, 1),
            "toDate": datetime(2026, 12, 31),
        }

        result = service.numbering_rule(None, "rental", datetime(2026, 9, 22))

        self.assertEqual(result["suffixPrefixId"], 7)
        self.assertEqual(result["prefix"], "RI")
        self.assertEqual(result["widthOfNumericalPart"], 6)

    @patch.object(repo, "taxes")
    @patch.object(repo, "get_voucher_type")
    def test_tax_lookup_requires_invoice_type_and_returns_allowed_rows(self, voucher_type, taxes):
        with self.assertRaises(HTTPException) as missing_type:
            service.lookups(None, "taxes")
        self.assertEqual(missing_type.exception.status_code, 422)

        voucher_type.return_value = {"voucherTypeId": 33}
        taxes.return_value = [
            {"taxId": 1, "taxName": "NA", "rate": Decimal("0")},
            {"taxId": 2, "taxName": "VAT @ 5%", "rate": Decimal("5")},
        ]
        result = service.lookups(None, "taxes", "fine")

        self.assertEqual([row["id"] for row in result], [1, 2])
        taxes.assert_called_once_with(None, 33)

    @patch.object(repo, "contract_vehicles")
    @patch.object(repo, "get_unit_by_name")
    @patch.object(repo, "get_item_type_by_name")
    @patch.object(repo, "get_voucher_type")
    @patch.object(repo, "get_contract")
    def test_rental_source_uses_contract_rate_without_writing(
        self, get_contract, voucher_type, item_type, unit, contract_vehicles
    ):
        get_contract.return_value = {"ContractId": 3000, "ContractRefNo": "3000", "Rate": Decimal("1905"), "ContractExpectedEndDate": datetime(2026, 10, 17)}
        voucher_type.return_value = {"voucherTypeId": 31}
        item_type.return_value = {"ItemType": 1, "TaxId": 2}
        unit.return_value = {"unitId": 2}
        contract_vehicles.return_value = [{"VehicleId": 88}]

        result = service.rental_source(None, 3000, datetime(2026, 9, 18))

        self.assertEqual(result["contractRefNo"], "3000")
        self.assertEqual(result["lines"][0]["vehicleId"], 88)
        self.assertEqual(result["lines"][0]["rate"], Decimal("1905"))
        self.assertEqual(result["lines"][0]["taxId"], 2)

    def test_salik_source_rejects_inverted_date_range_before_database_work(self):
        with self.assertRaises(HTTPException) as invalid_range:
            service.salik_source(None, 3000, datetime(2026, 9, 20), datetime(2026, 9, 18))
        self.assertEqual(invalid_range.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
