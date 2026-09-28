# Sales Invoice dossier

## Purpose and evidence

Creates and manages customer invoices for Rental, Salik, Fine, Miscellaneous, and Vehicle Sale transactions. The menu shows **Sales Invoice - F8**. Existing detailed evidence is in `docs/features/SALES_INVOICE_ANALYSIS.md` and `SALES_INVOICE_LOOKUPS.md`.

Status: **PARTIAL / MVP REQUIRED**. Register, detail, lookup, source, draft create/update/delete, and rental-billing routes exist. Posting/unposting deliberately return 501 because full side effects are not proven. Generic draft creation rejects Rental Invoice so contract billing owns its schedule.

## UI and lifecycle

Legacy evidence confirms a type selection followed by invoice header, line grid, tax selection, totals, and draft/post actions. Fine and Salik screens can show source-derived lines; captured posted examples expose UnPost. Line taxes can differ, and taxable service-charge lines can coexist with untaxed underlying fine/toll lines.

```text
select type/customer/source -> compose lines/tax -> save draft
draft -> edit/delete OR post -> posted -> unpost (only with complete reversal)
```

Current frontend exposes Rental Invoice due review, preview, draft creation/deletion, and register rows at `/rental-invoices`. A complete generic Sales Invoice entry page is MISSING.

## Data map

| Role | Table |
| --- | --- |
| Header/status/totals | `tbl_SalesMaster` |
| Lines | `tbl_SalesDetails` |
| Invoice tax summary | `tbl_SalesBillTax` |
| Types/items/tax | `tbl_VoucherType`, `tbl_SalesDetailItemType`, `tbl_Tax`, `tbl_VoucherTypeTax` |
| Numbering/period/currency | `tbl_SuffixPrefix`, `tbl_FinancialYear`, `tbl_ExchangeRate` |
| Customer/revenue/vehicle | `tbl_AccountLedger`, `VT_Veh_VehicleMaster` |
| Rental source | `VT_ContractMaster`, `VT_ContractVehicleMaster` |
| Fine source | `Traffic_Fine` |
| Salik source | `Salik_Toll` plus vehicle Salik tag and assignment window |
| Posting/open item | `tbl_LedgerPosting`, `tbl_PartyBalance` |
| Delete archive | `tbl_SalesMaster_Deleted`, `tbl_SalesDetails_Deleted` |

Voucher IDs currently used by code and prior live evidence: Rental `31`, Salik `32`, Fine `33`, Misc `34`, Vehicle `38`.

## Procedures and code flow

Previously live-verified procedures:

- `dbo.SalesMasterAdd`: owns master creation and invoice/voucher numbering; accepts draft posted state.
- `dbo.SalesInvoicePost`: only marks the identified invoice posted; it does not prove full accounting/source side effects.
- `dbo.SalesInvoiceUnPost`: reverses some invoice/ledger state but does not visibly prove full source/allocation reversal.
- `dbo.SalesInvoiceDelete`: archives header/details and removes known party-balance, ledger, cost, tax, detail, and header rows.

Current API flow: `/sales-invoices` router -> service validation/calculation -> repository -> `SalesMasterAdd` plus detail/tax inserts. Delete calls `SalesInvoiceDelete`. Rental billing wraps the same draft creation inside contract-aware scheduling.

Current endpoints: paginated register; numbering and lookup APIs; Rental/Fine/Salik source APIs; create/detail/update/delete; post/unpost placeholders; contract Rental Invoice preview/create/delete; due-rental list.

## Relationships and side effects

- Detail/tax `salesMasterId` joins are used by code but not declared FKs.
- `contractId` and `contractRefNo` associate rental/fine/salik billing; consistency must be validated.
- Fine/Salik duplicate prevention cannot rely only on source `ISPOSTED`; source-to-line identity is incomplete and `trafficFineNo` may not represent multiple tickets. Final design is `UNKNOWN`.
- Posting must balance customer debit, revenue/tax credit, create/update party balance, mark source charges consumed, and change Vehicle Invoice vehicle status to the verified Sold value.
- Unpost must reverse every one of those effects. Delete is draft-only and must use the archival procedure.

## Implementation and tests

1. Reconcile existing draft/register/detail behavior with approved data; fix only demonstrated defects.
2. Build generic UI for Fine, Salik, Misc, and Vehicle invoices; keep Rental under rental billing.
3. Establish stable source-link/duplicate protection for Fine and Salik without schema changes.
4. Verify VAT output ledger, revenue defaults, party-balance rules, Sold status, and full post/unpost transaction before enabling commands.
5. Make posting idempotent and atomic; reject edit/delete of posted or allocated invoices.

Acceptance tests: per-line tax/rounding; invalid lookup/type combinations; customer-contract ownership; registered vehicle requirement; duplicate source; create rollback; draft update replacement; archive delete; post retry; complete unpost; multiple/partial receipts; register filters and totals.

Estimate: **4-7 days** for draft/UI stabilization; **5-10 additional days** for posting after database rules are proven.

Primary risk: the legacy desktop client appears to orchestrate effects around narrow stored procedures. Calling only the procedure named "Post" would produce an incomplete accounting transaction.
