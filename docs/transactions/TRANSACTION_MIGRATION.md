# Transaction migration implementation

## Scope and Evidence

Implemented from the 19 supplied screenshots and read-only inspection of the live legacy SQL Server on 2026-10-09. Screenshots establish fields/actions, not hidden accounting effects. Stored-procedure definitions and existing postings were used as evidence; these new modules do not execute application stored procedures. No schema, generated mapping, master/reference record, or live business record was changed during implementation or verification.

Backend: `app/commercial_transactions` and `app/transaction_operations`, authenticated through the existing application router dependencies. Frontend: nine routes linked from the existing Financial Accounts navigation. Existing PDC, receipt, payment, contra, contract, and rental-billing implementations are preserved.

## Delivered Surface

| Page | Implemented behavior | Boundary |
| --- | --- | --- |
| `/bank-reconciliations` | Bank/date/status search, deposits/withdrawals, editable statement dates, reconciliation/reopening, optimistic conflict checks, book balance, entered bank balance and difference | Entered bank balance is a working comparison, not a new persisted statement record |
| `/purchase-orders` | Register, pending/overdue/cancelled filters, supplier/currency/due date, vehicle-linked lines, totals, cancellation, create/edit/delete/print | Invoiced orders are protected from edits/deletion |
| `/purchase-invoices` | Register with voucher/invoice date basis, supplier/mode/status filters, PO imports and remaining quantities, vendor invoice identity, tax/discount totals, transport/LR, create/edit/delete/print | Base-currency miscellaneous and fixed-asset posting supported, including discounts. Asset posting creates the verified method-1, 48-month depreciation schedule; depreciation, disposal, finance and settlement block reversal. Inventory and foreign-currency posting remain blocked |
| `/sales-quotations` | Register, approval status, customer/salesperson/pricing/currency, editable lines/narration, approval flag, create/edit/delete/print | Referenced delivery-note quotations cannot be altered |
| `/credit-notes` | Invoice credit notes in SalesReturn tables, register, source invoice/line validation, quantity ceilings, tax totals, draft create/edit/delete/print | Posting and reversal blocked pending reliable accounting evidence |
| `/debit-notes` | Register, balanced debit/credit lines, currency and cheque fields, Against allocations, save/edit/delete/print | Base-currency only; saves create balanced ledger effects. No posted legacy sample existed, so user-controlled acceptance testing remains required |
| `/traffic-fines` | Date/status/ticket search, traffic file/vehicle/authority/ticket/date/amount/black points/acknowledgment/description entry, duplicate protection | Creates fine record only; no automatic invoicing or payment |
| `/vehicle-finance` | Register, asset selection from purchase lines, financier, loan/monthly/EMI fields, month-end-safe schedule preview, save/edit/delete/finalize/print | Requires posted fixed-asset purchase; finalization follows FinanceHeaderPost's status-only behavior. Does not invent PDC generation or finance reversal |
| `/sales-invoice-register` | Date/customer/type/contract/invoice/fine/location/status filters, pagination, selection, detail, CSV/Excel XML/PDF export, browser print, Salik detail | Excel/PDF export covers selected rows or filtered results up to 10,000 invoices. Read-only register; existing invoice posting limitations remain. Sales Mode is unused in the inspected legacy procedure and was not invented |

All commercial writes are atomic with rollback, line-ownership validation, server-calculated decimal totals, and posted/downstream-reference protection. Existing detail identities are preserved. Numbered document creation is serialized and retry keys are stored in the existing extra fields. Finance relies on its unique manual number and does not have the same retry-key storage. Updates/deletes require a current version token. Reconciliation uses statement-date concurrency checks and serialized legacy marker numbering.

## Key Legacy Evidence

- `PurchaseOrderMasterAdd`, `PurchaseOrderDetailsAdd`, `PurchaseOrderRgistersearch`: order header/detail layout and register statuses. PO quantity use is calculated from purchase details; a misleading amount-as-quantity legacy projection was not copied.
- `PurchaseMasterAdd`, `PurchaseDetailsAdd`, `PurchaseMasterPost`, `PurchaseInvoiceUnPost`: draft lifecycle and flag-only posting routine. Existing miscellaneous purchase postings demonstrate supplier credit, expense debit, and the configured VAT ledger debit. A deeper read found 42 relevant historical purchases with balanced postings; all discounts credit ledger 9, validated by its configured name `Discount Received`.
- `FixedAssetDepreciationScheduleAdd`, `FixedAssetsViewByAssetLedgerNotPurchaseInvoiced`, and `PurchaseMasterReferenceCheckFixedAssets`: acquisition and depreciation linkage. All 117 asset purchase lines have quantity one, method 1, period 48 months, schedule start equal to purchase date, schedule end four years later, and schedule total equal to the tax-inclusive line amount. New posting preserves that observed rule and validates the category's asset/depreciation accounts. Unposting removes only unused schedules and blocks generated depreciation, disposal, finance and settlement. No asset master is edited.
- `SalesQuotationMasterAdd`, `SalesQuotationDetailsAdd`, `SalesQuotationRegisterSearch`, reference-check procedures: approval and delivery-note dependencies.
- `SalesReturnMasterAdd`, `SalesReturnDetailsAdd`, `SalesReturnPost`, `SalesReturnUnPost`: invoice credit notes use voucher type 39 and SalesReturn tables, not generic CreditNote tables. No posted sample was available to establish the complete accounting lifecycle.
- `DebitNoteMasterAdd`, `DebitNoteDetailsAdd`, `DebitNoteVoucherDelete`: voucher/detail lifecycle. Balanced ledger and Against behavior follows the existing application's allocation orientation. Requires business acceptance because live legacy debit-note data was empty.
- `FinanceHeaderAdd`, `FinanceDetailAdd`, `FinanceHeaderPost`, `PurchaseDetailAssetNotFinanced`: purchase-detail/asset relationship, installments, and finalization. Observed posted finance schedules contained no linked PDC IDs.
- `BankReconciliationAdd/Edit/Delete`, reconciled/unreconciled fill procedures: ledger-posting relationship and statement-date semantics.
- `VT_AddTrafficFine`: fine entry field mapping; ticket number is the business identity.
- `SalesInvoiceRegisterGridfill`: filters and invoice/register joins. Outer joins in the new register retain invoices whose historical descriptive master is missing.
- `salikDetailsPrintBySalesMasterIdInRegister`: invoice-number Salik linkage and item-type-7 administration rate. Ambiguous invoice numbers or multiple administration rates now return a conflict instead of choosing an arbitrary record.

## Verification

- 85 focused backend tests passed: new transaction workflows plus existing contra/payment/receipt/PDC suites. Includes rollback, idempotency, stale versions, line identity, source overdraw, allocation preservation across reordered updates, balanced postings, unpost protection, month-end schedules, reconciliation conflicts, duplicate fines, sales filtering, Salik ambiguity, discount accounting, acquisition schedules/reversal protection, finance finalization, and XML/PDF exports.
- Earlier full backend discovery (before five additional tests): 120 tests, 108 passed and 12 vehicle/tariff tests failed because the existing test setup did not supply authentication. Production authentication was not weakened to satisfy those tests.
- Frontend TypeScript and production Next.js webpack build passed. Two pre-existing compile issues were corrected narrowly: missing contract-print URL helper and customer field types.
- Targeted ESLint passed for the new workspaces and helpers.
- All nine pages and six commercial editors checked at desktop (1440px) and mobile (390px) with synthetic API data. No page overflow or browser JavaScript errors. Purchase-order create/save/register/reopen flow passed with synthetic responses.
- Live read-only queries passed: 1,254 purchases, 11 quotations, 16 finance records, 1,753 bank entries for the sampled bank, 1,419 fines, 7,602 sales invoices; source/lookup/detail queries passed. PO, credit-note and debit-note tables were empty at inspection.
- No live write/post/unpost/delete was submitted. SQL Server write locking, database constraints and actual posted side effects still require controlled acceptance testing on a disposable database copy.
- PDF export was rendered and visually checked with synthetic invoices. Excel XML preserves numeric cells and stores formula-like text as literal strings. Final desktop/mobile checks and a synthetic save/reopen flow were run against the integrated app on port 3000; its backend on port 8000 exposes the new routes and unauthenticated calls return 401.

## Remaining Parity Gaps

User decision on 2026-10-09: leave credit-note and inventory posting for now after the second database investigation. Their draft/register functionality remains available; posting stays blocked intentionally.

This is not a claim of complete legacy parity or production approval. Credit-note accounting, inventory stock effects, foreign-currency posting, alternative asset depreciation methods/periods, and any missing finance-to-PDC orchestration require legacy application source or accountant-approved expected entries. A second database inspection confirmed zero postings and balances for credit-note voucher types 20/22/39, zero inventory purchases, and no relevant triggers. The user was asked for source or approved examples only after that investigation. Do not remove these guards merely to enable buttons.

Sales-register exports provide Excel-compatible XML workbooks and PDF files; CSV is also available for the current/selected page. Commercial editors include print-after-save, clear, and purchase-order due-day controls. Exact legacy letterhead/signature/stamp templates, combined multi-invoice print, inline master creation, and the unused Sales Mode behavior are not implemented. No new master creation was authorized by the transaction-only database boundary.

Recommended acceptance: test each supported create/edit/delete flow on a disposable SQL Server clone; compare balances and registers against the legacy application; exercise two-user conflicts and retries; approve the remaining posting rules with accounting owners before enabling them.
