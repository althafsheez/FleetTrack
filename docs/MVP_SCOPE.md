# MVP scope

This is the user's target scope, not an implementation-complete checklist. The broader ERP README does not expand the client demo automatically.

## IN MVP

| Area | Included |
| --- | --- |
| Masters | Customer, Vehicle, Tariff and required lookup/master selections. |
| Rental workflow | Contract, Checkout, Active rental, Check-in. |
| Charges | Fines/Salik, when applicable to the rental. |
| Billing/collection | Invoice, Receipt. |
| Registers | Sales Invoice Register, Receipt Register. |
| UI target | Next.js, TypeScript, Tailwind CSS, shadcn/ui screens supporting the approved flow, guided by reference captures. |

## OUT OF MVP

Full ERP rebuild; database redesign/migrations; generated-model rewrite; broad dependency upgrades; unrelated refactoring; payroll/HR, purchasing/inventory, fixed-asset accounting, workshop/maintenance systems, and general ERP reporting beyond the two requested registers. Existing supplier functionality remains preserved; expanding supplier workflows is not part of the requested core demo.

## UNKNOWN / NEEDS CONFIRMATION

Exact screen fields and required CRUD actions; tariff rule coverage; rental/lease variants; extensions/replacements/cancellations; login/roles and multi-company/branch permissions; fine/Salik manual entry versus automated import; late-charge handling; invoice printing/export; receipt allocation, deposits, partial payments and refunds; mandatory legacy accounting side effects; demo dataset, delivery date, and hosting.

Resolve only what the approved demo requires. Accounting writes required for valid invoices/receipts are not excluded simply because the full finance module is out of scope. Do not expand scope or guess those dependencies.
