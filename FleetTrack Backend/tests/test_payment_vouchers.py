"""Payment Voucher backend tests using mocks only; no MSSQL writes occur."""
import inspect
import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from fastapi import HTTPException
from pydantic import ValidationError

from app.payment_vouchers import repository as repo
from app.payment_vouchers import router, service
from app.payment_vouchers.schemas import PaymentVoucherInput


DATE = datetime(2026, 9, 27)


def payload(**changes):
    values = {
        "voucherTypeId": 35,
        "voucherDate": DATE,
        "payingLedgerId": 100,
        "narration": "Supplier payment",
        "idempotencyKey": "payment-test-0001",
        "lines": [{
            "ledgerId": 200,
            "amount": "100.00000",
            "exchangeRateId": 1,
        }],
    }
    values.update(changes)
    return PaymentVoucherInput.model_validate(values)


def validation_result(request, *, party=False, allocations=None, base=Decimal("100"), forex=Decimal("0")):
    line = {
        "input": request.lines[0],
        "account": {"ledgerId": 200, "ledgerName": "Expense", "isParty": party},
        "exchange": {"exchangeRateId": 1, "currencyId": 18, "rate": Decimal("1")},
        "baseAmount": base,
        "postingBaseAmount": base - forex,
        "forexDifference": forex,
        "allocations": allocations or [],
    }
    return (
        {"voucherTypeId": 35, "methodOfVoucherNumbering": "Automatic"},
        {"financialYearId": 3},
        "Automatic",
        None,
        {"ledgerId": 100, "ledgerName": "Bank"},
        [line],
        base,
    )


class PaymentVoucherTests(unittest.TestCase):
    def test_static_routes_precede_dynamic_route(self):
        paths = [route.path for route in router.router.routes]
        dynamic = paths.index("/payment-vouchers/{payment_master_id}")
        self.assertLess(paths.index("/payment-vouchers/lookups/voucher-types"), dynamic)
        self.assertLess(paths.index("/payment-vouchers/lookups/party-ledgers"), dynamic)
        self.assertLess(paths.index("/payment-vouchers/party-ledgers/{ledger_id}/open-references"), dynamic)
        self.assertIn("/payment-vouchers/{payment_master_id}/post", paths)
        self.assertIn("/payment-vouchers/{payment_master_id}/unpost", paths)

    def test_repository_contains_no_application_stored_procedure_calls(self):
        source = inspect.getsource(repo).upper()
        self.assertNotIn("EXEC ", source)
        self.assertNotIn("CALL ", source)

    def test_schema_requires_against_source_and_complete_cheque(self):
        with self.assertRaises(ValidationError):
            payload(lines=[{
                "ledgerId": 200, "amount": "1", "exchangeRateId": 1,
                "allocations": [{"referenceType": "against", "amount": "1"}],
            }])
        with self.assertRaises(ValidationError):
            payload(lines=[{
                "ledgerId": 200, "amount": "1", "exchangeRateId": 1,
                "chequeNo": "CHK-1",
            }])

    def test_schema_rejects_duplicate_detail_ledgers_and_references(self):
        with self.assertRaises(ValidationError):
            payload(lines=[
                {"ledgerId": 200, "amount": "1", "exchangeRateId": 1},
                {"ledgerId": 200, "amount": "2", "exchangeRateId": 1},
            ])
        with self.assertRaises(ValidationError):
            payload(lines=[{
                "ledgerId": 200, "amount": "2", "exchangeRateId": 1,
                "allocations": [
                    {"referenceType": "against", "sourceVoucherTypeId": 41,
                     "sourceVoucherNo": "1", "amount": "1"},
                    {"referenceType": "against", "sourceVoucherTypeId": 41,
                     "sourceVoucherNo": "1", "amount": "1"},
                ],
            }])

    def test_register_normalizes_dates_and_passes_all_filters(self):
        row = {
            "paymentMasterId": 9, "voucherNo": "790", "invoiceNo": "BP0790",
            "voucherTypeId": 35, "voucherTypeName": "Bank Payment Voucher",
            "voucherDate": datetime(2026, 9, 20, 19, 30),
            "payingLedgerId": 100, "payingLedgerName": "ADCB",
            "totalAmount": Decimal("487.50000"), "narration": "Supplier payment",
            "isPosted": True, "detailAccountNames": ["Supplier A"], "lineCount": 1,
        }
        db = Mock()
        with patch.object(repo, "list_vouchers", return_value=([row], 1)) as listing:
            result = service.list_vouchers(
                db,
                from_date=datetime(2026, 9, 20, 8, 15),
                to_date=datetime(2026, 9, 20, 8, 15),
                voucher_no="  BP0790  ", voucher_type_id=35,
                paying_ledger_id=100, amount=Decimal("487.50000"),
                party_ledger_id=200, cheque_no="  CHQ-88  ",
                posted=True, offset=20, limit=10,
            )
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["paymentMasterId"], 9)
        self.assertEqual(result["items"][0]["detailAccountNames"], ["Supplier A"])
        listing.assert_called_once_with(
            db,
            datetime(2026, 9, 20), datetime(2026, 9, 21),
            "BP0790", 35, 100, Decimal("487.50000"), 200, "CHQ-88",
            True, 20, 10,
        )

    def test_register_rejects_reversed_dates(self):
        with self.assertRaises(HTTPException) as failure:
            service.list_vouchers(
                Mock(),
                from_date=datetime(2026, 9, 21),
                to_date=datetime(2026, 9, 20),
            )
        self.assertEqual(failure.exception.status_code, 422)

    def test_register_detail_filters_use_exists_without_duplicate_master_rows(self):
        count_result = Mock()
        count_result.scalar_one.return_value = 0
        rows_result = Mock()
        rows_result.mappings.return_value.all.return_value = []
        db = Mock()
        db.execute.side_effect = [count_result, rows_result]

        rows, total = repo.list_vouchers(
            db,
            from_date=datetime(2026, 9, 20),
            to_date_exclusive=datetime(2026, 9, 21),
            amount=Decimal("10.00000"),
            party_ledger_id=200,
            cheque_no="CHQ-1",
        )

        count_sql = str(db.execute.call_args_list[0].args[0]).upper()
        self.assertEqual(rows, [])
        self.assertEqual(total, 0)
        self.assertGreaterEqual(count_sql.count("EXISTS"), 2)
        self.assertIn("TBL_PAYMENTDETAILS", count_sql)
        self.assertNotIn("JOIN TBL_PAYMENTDETAILS", count_sql)

    @patch.object(repo, "list_party_ledgers", return_value=[{
        "ledgerId": 200, "ledgerName": "Supplier A", "accountGroupId": 22,
        "accountGroupName": "Sundry Creditors", "isParty": True,
    }])
    def test_party_lookup_returns_only_bill_by_bill_projection(self, lookup):
        result = service.party_ledgers(Mock(), "supplier", 25)
        lookup.assert_called_once()
        self.assertEqual(result, [{
            "id": 200, "name": "Supplier A", "accountGroupId": 22,
            "accountGroupName": "Sundry Creditors", "billByBill": True,
        }])

    @patch.object(repo, "get_voucher_type")
    @patch.object(repo, "get_financial_year", return_value={"financialYearId": 3})
    @patch.object(repo, "get_suffix_prefix", return_value=None)
    @patch.object(repo, "get_paying_account", return_value={"ledgerId": 100})
    @patch.object(repo, "get_detail_account")
    @patch.object(repo, "get_exchange_rate", return_value={
        "exchangeRateId": 1, "currencyId": 18, "rate": Decimal("1")
    })
    def test_allocations_allowed_only_for_party_ledgers(
        self, _rate, detail, _paying, _suffix, _year, voucher
    ):
        voucher.return_value = {"voucherTypeId": 35, "methodOfVoucherNumbering": "Automatic"}
        detail.return_value = {"ledgerId": 200, "isParty": False}
        request = payload(lines=[{
            "ledgerId": 200, "amount": "10", "exchangeRateId": 1,
            "allocations": [{"referenceType": "new", "amount": "10"}],
        }])
        with self.assertRaises(HTTPException) as failure:
            service._validate_payload(None, request)
        self.assertEqual(failure.exception.status_code, 422)

    @patch.object(repo, "get_voucher_type", return_value={
        "voucherTypeId": 35, "methodOfVoucherNumbering": "Automatic"
    })
    @patch.object(repo, "get_financial_year", return_value={"financialYearId": 3})
    @patch.object(repo, "get_suffix_prefix", return_value=None)
    @patch.object(repo, "get_paying_account", return_value={"ledgerId": 100})
    @patch.object(repo, "get_detail_account", return_value={"ledgerId": 200, "isParty": True})
    @patch.object(repo, "get_exchange_rate", return_value={
        "exchangeRateId": 2, "currencyId": 18, "rate": Decimal("1.20")
    })
    @patch.object(repo, "list_open_references")
    def test_party_allocation_validates_pending_and_calculates_forex(
        self, references, _rate, _detail, _paying, _suffix, _year, _voucher
    ):
        references.return_value = [{
            "ledgerId": 200, "sourceVoucherTypeId": 41, "sourceVoucherNo": "3639",
            "sourceInvoiceNo": "PI3639", "pendingAmount": Decimal("100"),
            "exchangeRateId": 1, "exchangeRate": Decimal("1.00"),
            "currencyId": 18, "contractId": 7,
        }]
        request = payload(lines=[{
            "ledgerId": 200, "amount": "100", "exchangeRateId": 2,
            "allocations": [{
                "referenceType": "against", "sourceVoucherTypeId": 41,
                "sourceVoucherNo": "3639", "amount": "100",
            }],
        }])
        result = service._validate_payload(None, request)
        line = result[5][0]
        self.assertEqual(line["baseAmount"], Decimal("120.00000"))
        self.assertEqual(line["postingBaseAmount"], Decimal("100.00000"))
        self.assertEqual(line["forexDifference"], Decimal("20.00000"))

        overpaid = payload(lines=[{
            "ledgerId": 200, "amount": "101", "exchangeRateId": 2,
            "allocations": [{
                "referenceType": "against", "sourceVoucherTypeId": 41,
                "sourceVoucherNo": "3639", "amount": "101",
            }],
        }])
        with self.assertRaises(HTTPException) as failure:
            service._validate_payload(None, overpaid)
        self.assertEqual(failure.exception.status_code, 409)

    @patch.object(service, "_response", return_value={"paymentMasterId": 1})
    @patch.object(service, "_validate_payload")
    def test_create_saves_unposted_draft_without_ledger_postings(self, validate, response):
        request = payload()
        validate.return_value = validation_result(request)
        db = Mock()
        with patch.multiple(
            repo,
            lock_numbering_scope=Mock(),
            get_master_by_idempotency_key=Mock(return_value=None),
            next_internal_voucher_number=Mock(return_value=790),
            voucher_number_exists=Mock(return_value=False),
            insert_master=Mock(return_value=1),
            insert_detail=Mock(return_value=10),
            insert_draft_allocation=Mock(),
            insert_posting=Mock(),
            get_master=Mock(return_value={}),
        ):
            result = service.create_voucher(db, request, 14)
            self.assertFalse(repo.insert_master.call_args.args[1]["isPosted"])
            repo.insert_posting.assert_not_called()
        self.assertEqual(result, {"paymentMasterId": 1})
        db.commit.assert_called_once_with()

    @patch.object(service, "_response")
    @patch.object(service, "_validate_payload")
    def test_post_creates_header_credit_and_detail_debit_then_marks_posted(self, validate, response):
        request = payload(lines=[{
            "paymentDetailsId": 10, "ledgerId": 200,
            "amount": "100", "exchangeRateId": 1,
        }])
        response.return_value = {
            "paymentMasterId": 1, "voucherNo": "790", "invoiceNo": "BP0790",
            "voucherTypeId": 35, "voucherDate": DATE, "payingLedgerId": 100,
            "narration": "Supplier payment", "idempotencyKey": "payment-test-0001",
            "lines": [{
                "paymentDetailsId": 10, "ledgerId": 200, "amount": Decimal("100"),
                "exchangeRateId": 1, "chequeNo": None, "chequeDate": None,
                "vehicleId": None, "allocations": [],
            }],
        }
        validate.return_value = validation_result(request)
        master = {
            "paymentMasterId": 1, "voucherNo": "790", "invoiceNo": "BP0790",
            "voucherTypeId": 35, "date": DATE, "ledgerId": 100,
            "financialYearId": 3, "isPosted": False, "extra1": "payment-test-0001",
        }
        db = Mock()
        with patch.multiple(
            repo,
            get_master=Mock(side_effect=[master, {**master, "isPosted": True}]),
            posting_totals=Mock(side_effect=[
                {"rowCount": 0, "debit": 0, "credit": 0},
                {"rowCount": 2, "debit": Decimal("100"), "credit": Decimal("100")},
            ]),
            get_allocations=Mock(return_value=[]),
            insert_posting=Mock(side_effect=[1, 2]),
            update_master=Mock(return_value=1),
        ), patch.object(service, "_voucher_type", return_value={
            "methodOfVoucherNumbering": "Automatic"
        }):
            result = service.post_voucher(db, 1)
            posting_calls = repo.insert_posting.call_args_list
            repo.update_master.assert_called_once_with(db, 1, {"isPosted": True})
        self.assertEqual(result, response.return_value)
        self.assertEqual(posting_calls[0].args[1]["credit"], Decimal("100.00000"))
        self.assertEqual(posting_calls[1].args[1]["debit"], Decimal("100.00000"))
        db.commit.assert_called_once_with()

    def test_update_rejects_posted_voucher(self):
        db = Mock()
        with patch.object(repo, "get_master", return_value={"isPosted": True}):
            with self.assertRaises(HTTPException) as failure:
                service.update_voucher(db, 1, payload(), 14)
        self.assertEqual(failure.exception.status_code, 409)
        db.rollback.assert_called_once_with()

    def test_unpost_rejects_reconciled_voucher(self):
        master = {
            "paymentMasterId": 1, "voucherTypeId": 35,
            "voucherNo": "790", "isPosted": True,
        }
        db = Mock()
        with patch.multiple(
            repo,
            get_master=Mock(return_value=master),
            has_external_party_reference=Mock(return_value=False),
            has_bank_reconciliation=Mock(return_value=True),
        ):
            with self.assertRaises(HTTPException) as failure:
                service.unpost_voucher(db, 1)
        self.assertEqual(failure.exception.status_code, 409)
        db.rollback.assert_called_once_with()

    def test_delete_draft_removes_allocations_details_and_master(self):
        master = {
            "paymentMasterId": 1, "voucherTypeId": 35,
            "voucherNo": "790", "isPosted": False,
        }
        db = Mock()
        with patch.multiple(
            repo,
            get_master=Mock(return_value=master),
            has_external_party_reference=Mock(return_value=False),
            has_bank_reconciliation=Mock(return_value=False),
            posting_totals=Mock(return_value={"rowCount": 0, "debit": 0, "credit": 0}),
            get_allocations=Mock(return_value=[]),
            delete_draft_allocations=Mock(),
            delete_details=Mock(),
            delete_master=Mock(return_value=1),
        ):
            service.delete_voucher(db, 1)
            repo.delete_draft_allocations.assert_called_once_with(db, 35, "790")
            repo.delete_details.assert_called_once_with(db, 1)
            repo.delete_master.assert_called_once_with(db, 1)
        db.commit.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
