# Sales Quotation dossier

## Purpose and evidence

Records a non-accounting customer offer with descriptive lines, pricing, approval, and optional later conversion. The menu shows **Sales Quotation - Alt+Q**. No current module or screen capture exists.

Status: **MISSING / OUTSIDE RENTAL MVP**.

## Candidate UI and lifecycle

Mapped fields support voucher/date/numbering, pricing level, customer ledger, employee, approval, total, narration, currency/year/user, and detail description/unit/quantity/rate/amount.

```text
new quotation -> select customer/pricing -> enter descriptive lines
-> save -> approve/reject/expire behavior UNKNOWN -> print/send
-> optional conversion to Sales Invoice or Contract Agreement UNKNOWN
```

Validity dates, terms, versioning, tax, discount, vehicle, contract-specific rental terms, and conversion tracking are not present in the mapped master/detail and remain `UNKNOWN`.

## Data and relationships

- Header: `tbl_SalesQuotationMaster`.
- Lines: `tbl_SalesQuotationDetails`.
- Customer/employee/pricing/unit/currency: `tbl_AccountLedger`, `tbl_Employee`, `tbl_PricingLevel`, `tbl_Unit`, `tbl_ExchangeRate`.
- Numbering/period: `tbl_VoucherType`, `tbl_SuffixPrefix`, `tbl_FinancialYear`.
- Candidate conversion targets: `tbl_SalesMaster` or contract tables; no mapped source quotation ID proves either relationship.

No generated FKs enforce these joins. A quotation should not create ledger or party-balance rows unless verified legacy behavior says otherwise.

## Procedures and target code flow

Quotation add/edit/delete/approve/register/print/conversion procedures are `UNKNOWN`. Target `/sales-quotations` module provides register/detail/lookups/draft CRUD, verified approval command, and print. Conversion must remain absent until source identity and duplicate-prevention rules are proven.

## Safety and state rules

- Validate customer, employee, pricing, unit, quantities/rates, currency and totals.
- Approval should be explicit, auditable, and idempotent; define edit restrictions after approval.
- Delete only eligible drafts; retain approved/history records under verified behavior.
- Conversion must produce at most the allowed number of downstream documents and retain traceability using existing schema.
- Do not retrofit rental-specific Contract Agreement terms into this generic quotation without screen/database evidence.

## Implementation and tests

Capture create/edit/approve/print/delete and any conversion flow. Inspect whether this screen is actually used for rental offers or general sales.

Acceptance tests: invalid customer/unit; zero/negative line rules; total/rounding; approval replay; edit/delete approved record; duplicate number; conversion retry; no accounting side effects; register filters and print.

Estimate: **4-7 working days** without conversion, plus **2-4 days** if a verified conversion workflow exists. Risks are ambiguous business scope and no mapped downstream link.
