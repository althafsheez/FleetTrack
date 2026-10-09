import unittest
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from pydantic import ValidationError
from fastapi import HTTPException

from app.main import app
from app.pdc_vouchers import service
from app.pdc_vouchers.schemas import PDCClearanceInput, PDCVoucherInput


def voucher_payload(**overrides):
    values = {
        "voucherDate": "2026-09-20T00:00:00", "controlLedgerId": 10, "partyLedgerId": 30,
        "bankLedgerId": 20, "amount": "100.00000", "chequeNo": "CHQ-1",
        "chequeDate": "2026-10-20T00:00:00",
        "allocations": [{"ledgerId": 30, "sourceVoucherTypeId": 31, "sourceVoucherNo": "INV-1", "amount": "100.00000"}],
    }
    values.update(overrides)
    return PDCVoucherInput.model_validate(values)


def registration_effects(kind):
    postings = []
    master = {
        "date": datetime(2026, 9, 20), "voucherTypeId": 7 if kind == "payable" else 8,
        "voucherNo": "1", "invoiceNo": "1", "ledgerId": 10,
        "amount": Decimal("100"), "financialYearId": 3,
        "chequeNo": "CHQ-1", "chequeDate": datetime(2026, 10, 20),
    }
    def totals(*_):
        return {"debit": sum(x["debit"] for x in postings),
                "credit": sum(x["credit"] for x in postings)}

    with patch.object(service.repo, "insert_posting", side_effect=lambda db, row: postings.append(row)), \
         patch.object(service.repo, "posting_totals", side_effect=totals):
        service._save_effects(object(), kind, master, 30)
    return postings


def clearance_effects(kind, status):
    postings = []
    row = {"status": status, "date": datetime(2026, 10, 20), "voucherTypeId": 9,
           "voucherNo": "1", "invoiceNo": "1", "financialYearId": 3}
    source = {"ledgerId": 10, "bankId": 20, "amount": Decimal("100"),
              "chequeNo": "CHQ-1", "chequeDate": datetime(2026, 10, 20)}

    def totals(*_):
        return {"rows": len(postings), "debit": sum(x["debit"] for x in postings),
                "credit": sum(x["credit"] for x in postings)}

    with patch.object(service.repo, "insert_posting", side_effect=lambda db, value: postings.append(value)), \
         patch.object(service.repo, "posting_totals", side_effect=totals):
        service._save_clearance_postings(object(), row, source, kind)
    return postings


class PDCVoucherTests(unittest.TestCase):
    def test_against_allocation_uses_the_selected_account_and_pdc_reference(self):
        master = {
            "date": datetime(2026, 9, 20), "voucherTypeId": 7,
            "voucherNo": "15", "invoiceNo": "15", "financialYearId": 3,
        }
        item = type("Allocation", (), {
            "ledgerId": 30, "amount": Decimal("100"),
        })()
        source = {
            "sourceVoucherTypeId": 31, "sourceVoucherNo": "001234",
            "sourceInvoiceNo": "PI-001234", "exchangeRateId": 1,
        }
        payable = service._allocation_values(master, item, source, "payable")
        receivable = service._allocation_values(master, item, source, "receivable")
        self.assertEqual((payable["ledgerId"], payable["debit"], payable["credit"]), (30, Decimal("100.00000"), Decimal("0")))
        self.assertEqual((receivable["ledgerId"], receivable["debit"], receivable["credit"]), (30, Decimal("0"), Decimal("100.00000")))
        self.assertEqual((payable["againstVoucherTypeId"], payable["againstVoucherNo"]), (7, "15"))

    def test_cleared_clearance_cannot_be_changed_or_deleted(self):
        @contextmanager
        def transaction(_db):
            yield

        cleared = {"status": "Cleared"}
        with patch.object(service, "write_transaction", transaction), \
             patch.object(service.repo, "get_clearance", return_value=cleared):
            with self.assertRaisesRegex(HTTPException, "final and cannot be edited"):
                service.update_clearance(object(), 1, object(), 1)
            with self.assertRaisesRegex(HTTPException, "final and cannot be deleted"):
                service.delete_clearance(object(), 1)

    def test_payload_requires_an_against_allocation(self):
        with self.assertRaisesRegex(ValidationError, "at least 1 item"):
            voucher_payload(allocations=[])

    def test_payload_rejects_cheque_before_voucher_date(self):
        with self.assertRaisesRegex(ValidationError, "chequeDate cannot be earlier"):
            voucher_payload(chequeDate="2026-09-19T00:00:00")

    def test_clearance_status_is_limited_to_legacy_values(self):
        with self.assertRaises(ValidationError):
            PDCClearanceInput.model_validate({
                "clearanceDate": "2026-09-20T00:00:00", "status": "Pending"
            })

    def test_payable_registration_debits_party_and_credits_control(self):
        postings = registration_effects("payable")
        self.assertEqual((postings[0]["ledgerId"], postings[0]["debit"]), (30, Decimal("100.00000")))
        self.assertEqual((postings[1]["ledgerId"], postings[1]["credit"]), (10, Decimal("100.00000")))

    def test_receivable_registration_credits_party_and_debits_control(self):
        postings = registration_effects("receivable")
        self.assertEqual((postings[0]["ledgerId"], postings[0]["credit"]), (30, Decimal("100.00000")))
        self.assertEqual((postings[1]["ledgerId"], postings[1]["debit"]), (10, Decimal("100.00000")))

    def test_payable_clearance_debits_control_and_credits_bank(self):
        rows = clearance_effects("payable", "Cleared")
        self.assertEqual((rows[0]["ledgerId"], rows[0]["debit"]), (10, Decimal("100.00000")))
        self.assertEqual((rows[1]["ledgerId"], rows[1]["credit"]), (20, Decimal("100.00000")))

    def test_receivable_clearance_debits_bank_and_credits_control(self):
        rows = clearance_effects("receivable", "Cleared")
        self.assertEqual((rows[0]["ledgerId"], rows[0]["credit"]), (10, Decimal("100.00000")))
        self.assertEqual((rows[1]["ledgerId"], rows[1]["debit"]), (20, Decimal("100.00000")))

    def test_bounced_clearance_is_status_only(self):
        self.assertEqual(clearance_effects("payable", "Bounced"), [])
        self.assertEqual(clearance_effects("receivable", "Bounced"), [])

    def test_three_route_families_are_registered(self):
        paths = app.openapi()["paths"]
        self.assertIn("/pdc-payables/", paths)
        self.assertIn("/pdc-receivables/", paths)
        self.assertIn("/pdc-payables/lookups/accounts", paths)
        self.assertIn("/pdc-receivables/lookups/accounts", paths)
        self.assertIn("/pdc-clearances/{source_type}/{source_id}", paths)
        self.assertIn("/pdc-clearances/lookups/pending-instruments", paths)
        self.assertIn("/pdc-clearances/lookups/statuses", paths)


if __name__ == "__main__":
    unittest.main()
