# Evidence, database investigation, and dependency map

## Read-only investigation runbook

Run these checks only against the approved FleetTrack database and only with a read-only login. Save object names, parameters, result-column metadata, and dependency names; do not save credentials, personal data, cheque/card values, or full customer rows.

1. Catalog matching procedures, views, functions, and triggers using `sys.objects` and `sys.schemas`.
2. Record procedure parameters from `sys.parameters` and `sys.types`.
3. Record declared dependencies from `sys.sql_expression_dependencies`.
4. Review definitions with `OBJECT_DEFINITION(object_id)` and classify every insert/update/delete side effect.
5. Describe result sets with `sys.dm_exec_describe_first_result_set_for_object` where supported. Do not execute write procedures to discover output.
6. Compare table columns, primary keys, foreign keys, defaults, checks, triggers, and indexes through `sys.tables`, `sys.columns`, `sys.key_constraints`, `sys.foreign_keys`, `sys.default_constraints`, `sys.check_constraints`, `sys.triggers`, and `sys.indexes`.
7. Inspect only sanitized representative rows approved for analysis, including one complete posted/unposted lifecycle where possible.

Search terms per object family: `Contra`, `Payment`, `Receipt`, `Journal`, `PDC`, `CreditNote`, `DebitNote`, `BankReconciliation`, `PurchaseOrder`, `Purchase`, `Quotation`, `Contract`, `TrafficFine`, `Finance`, `SalesMaster`, and `SalesInvoice`.

For each discovered procedure record: exact schema/name, parameters and defaults, result columns, tables read, tables written, transaction handling, numbering behavior, posted-state behavior, archive behavior, error behavior, and callers. A name match alone is not proof that FleetTrack should call it.

## Shared transaction spine

```text
tbl_VoucherType
       |
       +--> tbl_SuffixPrefix --------+
       |                              |
tbl_FinancialYear                     v
       |                       transaction master --> transaction details/tax
       |                              |
tbl_AccountLedger <-------------------+
       |                              |
tbl_ExchangeRate                      +--> tbl_LedgerPosting
                                      +--> tbl_PartyBalance
                                      +--> source/status side effects
```

The arrows are implementation candidates based on repeated ID-shaped columns. The generated snapshot declares no foreign keys for these transaction tables. Every join must therefore be validated by procedure definitions or representative records before writes are implemented.

## Shared tables and responsibilities

| Concern | Candidate tables | Required confirmation |
| --- | --- | --- |
| Voucher identity/type | `tbl_VoucherType` | Active IDs, type labels, posting semantics, correct master table. |
| Numbering | `tbl_SuffixPrefix` | Date-range selection, start index, concurrency, prefix/suffix formatting, who increments. |
| Accounting period | `tbl_FinancialYear`, `tbl_FinancialYearMonthStatus` | Open period rule and rejection behavior. |
| Parties/accounts | `tbl_AccountLedger`, `tbl_AccountGroup` | Customer, supplier, cash, bank, revenue, expense and control-account filters. |
| Currency | `tbl_ExchangeRate`, `tbl_Currency` | Base currency, rate direction, rounding and historical rate rule. |
| Posting | `tbl_LedgerPosting` | Debit/credit construction, `detailsId`, idempotency, reversal/deletion. |
| Bill settlement | `tbl_PartyBalance` | `New`/`Against` reference types, partial allocations, advance/credit handling. |
| Tax | `tbl_Tax`, `tbl_TaxDetails`, `tbl_VoucherTypeTax` | Availability, calculation mode, control ledgers and rounding. |
| Audit | Transaction `userId`/created fields | Authenticated actor mapping and immutable audit behavior. |
| Vehicle dimension | `VT_Veh_VehicleMaster` and transaction `Vehicle`/`vehicleId` fields | Whether vehicle attribution is required, optional, or reporting-only. |

## Confirmed and blocked procedure evidence

Previously captured live evidence confirms `dbo.SalesMasterAdd`, `dbo.SalesInvoicePost`, `dbo.SalesInvoiceUnPost`, and `dbo.SalesInvoiceDelete`; details and cautions are in [Sales Invoice](SALES_INVOICE.md). No other procedure inventory in this directory is live-confirmed because SQL Server was unavailable during this pass.

Posting remains blocked until each family proves all of the following as one coherent operation:

- Header/detail/tax persistence and voucher numbering.
- Balanced `tbl_LedgerPosting` rows.
- Correct `tbl_PartyBalance` creation/allocation/reversal.
- Source flags and operational status changes.
- Idempotent retries and atomic rollback.
- Posted-document edit/delete restrictions.
- Complete unpost reversal, including source and operational state.

## Cross-module dependencies

| Module | Depends on | Provides to later modules |
| --- | --- | --- |
| Contract Agreement | Customer, vehicle, tariff, status, user/location lookups | Contract and assignment identity, billing schedule. |
| Sales Invoice | Contract/source data, sales accounts, tax, numbering | Customer debt/open item and invoice register. |
| Receipt Voucher | Open invoices/party balance, cash/bank accounts | Settlement and receipt register. |
| Contra/Payment/Journal | Shared posting and numbering rules | Proven accounting foundation. |
| Credit/Debit Note | Posting and open-item rules | Adjustments against parties/documents. |
| Bank Reconciliation | Posted bank ledger rows | Statement-cleared state. |
| PDC modules | Party, bank, payment/receipt and clearance rules | Deferred instrument lifecycle. |
| Vehicle Finance | Purchase/asset identity plus PDC/bank | Installment schedule/payment state. |
| Purchase Invoice | Supplier, product/vehicle, tax, posting | Supplier liability and asset/inventory cost. |
| Purchase Order | Supplier and item/vehicle lookups | Optional source for Purchase Invoice. |
| Sales Quotation | Customer, units, pricing | Optional pre-sales document; conversion is UNKNOWN. |

## Global failure rules for future implementation

- Use one database transaction for a business command; rollback every side effect on error.
- Lock or rely on a verified atomic numbering procedure to prevent duplicate voucher numbers.
- Reject repeated post/unpost/clear commands or make them demonstrably idempotent.
- Do not silently repair orphaned rows; report them and preserve evidence.
- Do not expose physical delete for posted or allocated documents.
- Never infer a relationship only because two columns have similar names.
