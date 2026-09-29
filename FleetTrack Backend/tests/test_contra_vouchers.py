"""Contra Voucher backend tests using mocks only; no MSSQL writes occur."""
import inspect
import unittest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch

from fastapi import HTTPException
from pydantic import ValidationError

from app.contra_vouchers import repository as repo
from app.contra_vouchers import router, service
from app.contra_vouchers.schemas import ContraVoucherInput


DATE = datetime(2026, 9, 10)


def payload(**changes):
    values = {
        "voucherDate": DATE,
        "direction": "deposit",
        "headerLedgerId": 100,
        "narration": "DEPOSITED TO BANK",
        "idempotencyKey": "contra-test-0001",
        "lines": [{
            "ledgerId": 200,
            "amount": "4810.00000",
            "exchangeRateId": 1,
        }],
    }
    values.update(changes)
    return ContraVoucherInput.model_validate(values)


class ContraVoucherTests(unittest.TestCase):
    def test_static_routes_precede_dynamic_route_and_no_post_routes_exist(self):
        paths = [route.path for route in router.router.routes]
        dynamic = paths.index("/contra-vouchers/{contra_master_id}")
        self.assertLess(paths.index("/contra-vouchers/lookups/accounts"), dynamic)
        self.assertLess(paths.index("/contra-vouchers/lookups/numbering-rule"), dynamic)
        self.assertFalse(any(path.endswith("/post") or path.endswith("/unpost") for path in paths))

    def test_repository_contains_no_application_stored_procedure_calls(self):
        source = inspect.getsource(repo).upper()
        self.assertNotIn("EXEC ", source)
        self.assertNotIn("CALL ", source)

    def test_cash_bank_groups_exclude_debtors_and_include_verified_bank_groups(self):
        self.assertNotIn("sundry debtors", repo.CASH_BANK_GROUP_NAMES)
        self.assertIn("cash-in hand", repo.CASH_BANK_GROUP_NAMES)
        self.assertIn("bank account", repo.CASH_BANK_GROUP_NAMES)
        self.assertIn("bank od a/c", repo.CASH_BANK_GROUP_NAMES)

    def test_schema_rejects_incomplete_cheque_and_duplicate_detail_ids(self):
        with self.assertRaises(ValidationError):
            payload(lines=[{
                "ledgerId": 200,
                "amount": "1",
                "exchangeRateId": 1,
                "chequeNo": "ABC",
            }])
        with self.assertRaises(ValidationError):
            payload(lines=[
                {"contraDetailsId": 7, "ledgerId": 200, "amount": "1", "exchangeRateId": 1},
                {"contraDetailsId": 7, "ledgerId": 201, "amount": "1", "exchangeRateId": 1},
            ])

    def test_deposit_and_withdrawal_generate_opposite_balanced_postings(self):
        line = {
            "input": payload().lines[0],
            "baseAmount": Decimal("4810.00000"),
        }
        detail = service._line_posting_values(payload(), 1, "175", "CV175", 2, line, 9)
        balance = service._balancing_posting_values(payload(), 1, "175", "CV175", 2, Decimal("4810"))
        self.assertEqual(detail["credit"], Decimal("4810.00000"))
        self.assertEqual(balance["debit"], Decimal("4810.00000"))
        self.assertEqual(detail["credit"], balance["debit"])

        withdrawal = payload(direction="withdrawal")
        detail = service._line_posting_values(withdrawal, 1, "176", "CV176", 2, line, 9)
        balance = service._balancing_posting_values(withdrawal, 1, "176", "CV176", 2, Decimal("4810"))
        self.assertEqual(detail["debit"], Decimal("4810.00000"))
        self.assertEqual(balance["credit"], Decimal("4810.00000"))

    def test_number_format_honours_prefix_suffix_and_width(self):
        rule = {
            "prefix": "CV-",
            "suffix": "-26",
            "prefillWithZero": True,
            "widthOfNumericalPart": 5,
        }
        self.assertEqual(service._format_invoice_no(175, rule), "CV-00175-26")

    @patch.object(repo, "get_financial_year", return_value={"financialYearId": 2})
    def test_voucher_date_requires_financial_year_without_guessing_month_status(self, financial_year):
        self.assertEqual(service._validate_period(None, DATE)["financialYearId"], 2)
        financial_year.return_value = None
        with self.assertRaises(HTTPException) as invalid:
            service._validate_period(None, DATE)
        self.assertEqual(invalid.exception.status_code, 422)

    @patch.object(repo, "next_internal_voucher_number", return_value=176)
    @patch.object(repo, "get_suffix_prefix", return_value=None)
    @patch.object(repo, "get_contra_voucher_type")
    def test_automatic_numbering_without_suffix_rule_uses_plain_number(
        self, voucher_type, _suffix, _next_number
    ):
        voucher_type.return_value = {
            "voucherTypeId": 8,
            "voucherTypeName": "Contra Voucher",
            "methodOfVoucherNumbering": "Automatic",
        }

        result = service.numbering_rule(None, DATE)

        self.assertTrue(result["automatic"])
        self.assertEqual(result["suffixPrefixId"], 0)
        self.assertEqual(result["nextVoucherNo"], "176")
        self.assertEqual(result["nextInvoiceNo"], "176")

    @patch.object(repo, "ledger_balance", return_value=Decimal("50"))
    @patch.object(repo, "get_setting", return_value="Warn")
    def test_negative_balance_warn_requires_explicit_confirmation(self, _setting, _balance):
        request = payload(direction="withdrawal")
        header = {"ledgerId": 100, "ledgerName": "Cash"}
        with self.assertRaises(HTTPException) as warning:
            service._negative_balance_check(
                None, request, {"voucherTypeId": 1}, header, [], Decimal("60")
            )
        self.assertEqual(warning.exception.status_code, 409)
        self.assertEqual(warning.exception.detail["code"], "NEGATIVE_CASH_BALANCE")
        self.assertTrue(warning.exception.detail["canConfirm"])

        confirmed = payload(direction="withdrawal", confirmNegativeBalance=True)
        service._negative_balance_check(
            None, confirmed, {"voucherTypeId": 1}, header, [], Decimal("60")
        )

    @patch.object(repo, "ledger_balance", return_value=Decimal("50"))
    @patch.object(repo, "get_setting", return_value="Block")
    def test_negative_balance_block_cannot_be_confirmed(self, _setting, _balance):
        request = payload(direction="withdrawal", confirmNegativeBalance=True)
        with self.assertRaises(HTTPException) as blocked:
            service._negative_balance_check(
                None,
                request,
                {"voucherTypeId": 1},
                {"ledgerId": 100, "ledgerName": "Cash"},
                [],
                Decimal("60"),
            )
        self.assertEqual(blocked.exception.status_code, 409)
        self.assertEqual(blocked.exception.detail["code"], "NEGATIVE_CASH_BALANCE")
        self.assertFalse(blocked.exception.detail["canConfirm"])

    @patch.object(repo, "list_offset_accounts")
    @patch.object(repo, "list_vouchers")
    def test_register_combines_filters_and_returns_line_summary(self, list_vouchers, list_accounts):
        list_vouchers.return_value = ([{
            "contraMasterId": 152,
            "voucherNo": "151",
            "invoiceNo": "CV-151",
            "voucherDate": DATE,
            "type": "Deposit",
            "headerLedgerId": 138278,
            "headerLedgerName": "ADCB",
            "totalAmount": Decimal("10.00000"),
            "narration": "TEST DEPOSIT",
        }], 1)
        list_accounts.return_value = [
            {"contraMasterId": 152, "contraDetailsId": 1, "ledgerId": 1, "ledgerName": "Cash"},
            {"contraMasterId": 152, "contraDetailsId": 2, "ledgerId": 2, "ledgerName": "Petty Cash"},
        ]

        result = service.list_vouchers(
            Mock(),
            from_date=date(2026, 9, 1),
            to_date=date(2026, 9, 30),
            voucher_no=" 151 ",
            ledger_id=138278,
            direction="deposit",
            offset=25,
            limit=25,
        )

        list_vouchers.assert_called_once_with(
            unittest.mock.ANY,
            from_datetime=datetime(2026, 9, 1),
            to_datetime_exclusive=datetime(2026, 10, 1),
            voucher_no="151",
            ledger_id=138278,
            direction="Deposit",
            offset=25,
            limit=25,
        )
        list_accounts.assert_called_once_with(unittest.mock.ANY, [152])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["items"][0]["lineCount"], 2)
        self.assertEqual(result["items"][0]["offsetAccountNames"], ["Cash", "Petty Cash"])

    @patch.object(repo, "list_offset_accounts", return_value=[])
    @patch.object(repo, "list_vouchers", return_value=([], 0))
    def test_register_blank_search_loads_all_and_rejects_reversed_dates(
        self, list_vouchers, _list_accounts
    ):
        result = service.list_vouchers(Mock(), voucher_no="   ")
        self.assertEqual(result["items"], [])
        self.assertIsNone(list_vouchers.call_args.kwargs["voucher_no"])

        with self.assertRaises(HTTPException) as invalid:
            service.list_vouchers(
                Mock(), from_date=date(2026, 10, 1), to_date=date(2026, 9, 30)
            )
        self.assertEqual(invalid.exception.status_code, 422)

    @patch.object(service, "_response", return_value={"contraMasterId": 1})
    @patch.object(service, "_negative_balance_check")
    @patch.object(service, "_validate_payload")
    def test_create_writes_master_details_and_balanced_postings_once(self, validate, negative, response):
        request = payload()
        line = {
            "input": request.lines[0],
            "account": {"ledgerId": 200, "ledgerName": "Cash"},
            "exchange": {"rate": Decimal("1")},
            "baseAmount": Decimal("4810.00000"),
        }
        validate.return_value = (
            {"voucherTypeId": 1},
            {"financialYearId": 2},
            "Automatic",
            {"suffixprefixId": 3, "startIndex": 1, "prefix": "CV", "suffix": "", "prefillWithZero": False, "widthOfNumericalPart": 0},
            {"ledgerId": 100, "ledgerName": "Bank"},
            [line],
            Decimal("4810.00000"),
        )
        db = Mock()
        with patch.multiple(
            repo,
            lock_numbering_scope=Mock(),
            get_master_by_idempotency_key=Mock(return_value=None),
            next_internal_voucher_number=Mock(return_value=175),
            voucher_number_exists=Mock(return_value=False),
            insert_master=Mock(return_value=1),
            insert_detail=Mock(return_value=9),
            insert_posting=Mock(side_effect=[10, 11]),
            count_postings=Mock(return_value=2),
            get_master=Mock(return_value={}),
        ):
            result = service.create_voucher(db, request, 7)
            calls = repo.insert_posting.call_args_list

        self.assertEqual(result, {"contraMasterId": 1})
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].args[1]["credit"], Decimal("4810.00000"))
        self.assertEqual(calls[1].args[1]["debit"], Decimal("4810.00000"))
        self.assertEqual(calls[0].args[1]["date"], DATE)
        db.commit.assert_called_once_with()
        db.rollback.assert_not_called()

    @patch.object(service, "_response", return_value={"contraMasterId": 1})
    @patch.object(service, "_negative_balance_check")
    @patch.object(service, "_validate_payload")
    def test_incomplete_posting_set_rolls_back(self, validate, negative, response):
        request = payload()
        line = {
            "input": request.lines[0],
            "account": {"ledgerId": 200},
            "exchange": {"rate": Decimal("1")},
            "baseAmount": Decimal("1"),
        }
        validate.return_value = (
            {"voucherTypeId": 1}, {"financialYearId": 2}, "Automatic",
            {"suffixprefixId": 3, "startIndex": 1, "prefix": "", "suffix": "", "prefillWithZero": False, "widthOfNumericalPart": 0},
            {"ledgerId": 100}, [line], Decimal("1"),
        )
        db = Mock()
        with patch.multiple(
            repo,
            lock_numbering_scope=Mock(), get_master_by_idempotency_key=Mock(return_value=None),
            next_internal_voucher_number=Mock(return_value=1), voucher_number_exists=Mock(return_value=False),
            insert_master=Mock(return_value=1), insert_detail=Mock(return_value=9),
            insert_posting=Mock(), count_postings=Mock(return_value=1),
        ):
            with self.assertRaises(HTTPException) as failure:
                service.create_voucher(db, request, 7)
        self.assertEqual(failure.exception.status_code, 409)
        db.rollback.assert_called_once_with()
        db.commit.assert_not_called()

    @patch.object(service, "_response", return_value={"contraMasterId": 1})
    @patch.object(service, "_validate_payload")
    def test_create_idempotency_retry_returns_existing_without_writes(self, validate, response):
        request = payload()
        validate.return_value = (
            {"voucherTypeId": 1}, {"financialYearId": 2}, "Automatic",
            {"suffixprefixId": 3}, {"ledgerId": 100}, [], Decimal("1"),
        )
        db = Mock()
        existing = {"contraMasterId": 1}
        with patch.multiple(
            repo,
            lock_numbering_scope=Mock(),
            get_master_by_idempotency_key=Mock(return_value=existing),
            insert_master=Mock(),
        ):
            result = service.create_voucher(db, request, 7)
            repo.insert_master.assert_not_called()
        self.assertEqual(result, {"contraMasterId": 1})
        db.commit.assert_not_called()
        db.rollback.assert_not_called()

    @patch.object(service, "_negative_balance_check")
    @patch.object(service, "_validate_payload")
    def test_update_rejects_detail_owned_by_another_voucher(self, validate, negative):
        request = payload(lines=[{
            "contraDetailsId": 99,
            "ledgerId": 200,
            "amount": "1",
            "exchangeRateId": 1,
        }])
        existing = {
            "contraMasterId": 1, "voucherTypeId": 1, "voucherNo": "1", "invoiceNo": "CV1"
        }
        line = {
            "input": request.lines[0], "account": {"ledgerId": 200},
            "exchange": {"rate": Decimal("1")}, "baseAmount": Decimal("1"),
        }
        validate.return_value = (
            {"voucherTypeId": 1}, {"financialYearId": 2}, "Automatic",
            {"suffixprefixId": 3}, {"ledgerId": 100}, [line], Decimal("1"),
        )
        db = Mock()
        with patch.object(repo, "get_master", return_value=existing), patch.object(
            repo, "get_details", return_value=[{"contraDetailsId": 9}]
        ):
            with self.assertRaises(HTTPException) as failure:
                service.update_voucher(db, 1, request, 7)
        self.assertEqual(failure.exception.status_code, 404)
        db.rollback.assert_called_once_with()

    def test_delete_removes_postings_details_and_header_in_one_commit(self):
        existing = {
            "contraMasterId": 1, "voucherTypeId": 8, "voucherNo": "175"
        }
        db = Mock()
        with patch.multiple(
            repo,
            get_master=Mock(return_value=existing),
            delete_postings=Mock(return_value=2),
            delete_details=Mock(return_value=1),
            delete_master=Mock(return_value=1),
        ):
            service.delete_voucher(db, 1)
            repo.delete_postings.assert_called_once_with(db, 8, "175")
            repo.delete_details.assert_called_once_with(db, 1)
            repo.delete_master.assert_called_once_with(db, 1)
        db.commit.assert_called_once_with()
        db.rollback.assert_not_called()


if __name__ == "__main__":
    unittest.main()
