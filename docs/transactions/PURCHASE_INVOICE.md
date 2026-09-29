# Purchase Invoice dossier

## Purpose and evidence

Records supplier invoices for miscellaneous, fixed-asset, or inventory purchases and creates supplier liability/accounting/tax effects. The menu shows **Purchase Invoice** with no shortcut observed. No current module or screen capture exists.

Status: **MISSING / OUTSIDE RENTAL MVP**.

## Candidate UI and lifecycle

Mapped fields support voucher/date, supplier and vendor invoice number/date, credit period, currency, narration, purchase account, optional Purchase Order, tax/discount/totals, transport fields, financial year, posting state, and category flags. Lines support source order detail, product, description, vehicle, quantity/rate/unit/tax and totals.

```text
new -> choose purchase category/supplier -> optional PO import
    -> lines and taxes -> save draft -> post supplier liability
    -> payment/credit note/allocation -> optional unpost under restrictions
```

Goods receipt, stock updates, fixed-asset creation, duplicate vendor-invoice rules, and category-specific UI are `UNKNOWN`.

## Data and relationships

| Role | Table |
| --- | --- |
| Header | `tbl_PurchaseMaster` |
| Lines | `tbl_PurchaseDetails` |
| Tax summary | `tbl_PurchaseBillTax` |
| Order source | `tbl_PurchaseOrderMaster`, `tbl_PurchaseOrderDetails` |
| Supplier/purchase account | `tbl_AccountLedger`, `tbl_AccountGroup` |
| Product/unit/vehicle | `tbl_Product`, `tbl_Unit`, `VT_Veh_VehicleMaster` |
| Tax/currency/numbering | `tbl_Tax`, exchange rate, voucher type, suffix, financial year |
| Accounting/open payable | `tbl_LedgerPosting`, `tbl_PartyBalance` |
| Downstream finance | `tbl_FinanceHeader.purchaseMasterId/purchaseDetailId` |

No generated FKs enforce these joins.

## Procedures and target code flow

Purchase add/edit/delete/post/unpost/register/print/order-import procedures are `UNKNOWN`. Target `/purchase-invoices` module follows router -> schemas -> service -> repository and uses verified procedures where they own numbering/archive/posting.

## Accounting and operational effects

- Verify debit destination by category: expense/purchase, fixed asset, or inventory.
- Verify supplier/control and input-tax postings, bill-by-bill payable creation, discount/freight treatment, and rounding.
- Verify whether inventory quantity/cost or fixed-asset masters are updated at draft or posting.
- Enforce supplier vendor-invoice duplicate policy and Purchase Order remaining quantities atomically.
- Vehicle/asset identity is required only for verified categories.
- Unpost must reverse stock/asset/tax/payable effects; otherwise reject.

## Implementation and tests

Trace one example for each used category (`isMiscPurchase`, `isFaPurchase`, `isInvPurchase`), PO and non-PO, taxed/untaxed, post/unpost/delete, supplier payment, and Vehicle Finance linkage.

Acceptance tests: mutually valid category flags; duplicate vendor invoice; PO over-conversion; product/unit/vehicle validation; tax/discount totals; currency; payable creation; post retry; unpost after payment/finance; full rollback; register filters.

Estimate: **8-12 working days** after procedure and category effects are known. Risks are broad stock/fixed-asset side effects and hidden client orchestration similar to Sales Invoice.
