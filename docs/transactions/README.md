# Transaction dossier index

Status date: 2026-09-28

This directory is the implementation handoff for every item visible in the supplied legacy **Transactions** menu. It is documentation only: no application code, generated model, database object, lookup value, or business record was changed while preparing it.

## Evidence rules

- **OBSERVED UI** means visible in a supplied capture. The current menu capture proves names, order, and shortcuts only; it does not prove a screen's fields or behavior.
- **CURRENT CODE** means present in the checked-out `prod` workspace. It does not by itself prove successful MSSQL runtime behavior.
- **GENERATED MODEL** means mapped in `FleetTrack Backend/app/generated_models/models.py`. The mapping is read-only evidence and does not establish a business relationship.
- **LIVE VERIFIED** means previously demonstrated with read-only MSSQL metadata/data or a live endpoint and recorded in an existing project document.
- **INFERRED** is a candidate design supported by names or common accounting practice, not an established FleetTrack rule.
- **UNKNOWN** is an explicit implementation gate. It must not be guessed.

The initial read-only MSSQL inspection on 2026-09-26 was unavailable. Targeted Contra, Payment, and Receipt inspection was subsequently completed against the local database; their dossiers record the verified procedures and sanitized behavior. Procedure inventories for the remaining uninvestigated modules remain `UNKNOWN`.

## Status matrix

| Menu item | Shortcut | Current status | Main mapped stores | Dossier |
| --- | --- | --- | --- | --- |
| Contra Voucher | F4 | MISSING | `tbl_ContraMaster`, `tbl_ContraDetails` | [Contra Voucher](CONTRA_VOUCHER.md) |
| Payment Voucher | F5 | MISSING | `tbl_PaymentMaster`, `tbl_PaymentDetails` | [Payment Voucher](PAYMENT_VOUCHER.md) |
| Receipt Voucher | F6 | BACKEND IMPLEMENTED / LIVE WRITES UNVERIFIED | `tbl_ReceiptMaster`, `tbl_ReceiptDetails`, `tbl_PartyBalance` | [Receipt Voucher](RECEIPT_VOUCHER.md) |
| Journal Voucher | F7 | MISSING | `tbl_JournalMaster`, `tbl_JournalDetails` | [Journal Voucher](JOURNAL_VOUCHER.md) |
| PDC Payable | Alt+P | MISSING | `tbl_PDCPayableMaster` | [PDC Payable](PDC_PAYABLE.md) |
| PDC Receivable | Alt+R | MISSING | `tbl_PDCReceivableMaster` | [PDC Receivable](PDC_RECEIVABLE.md) |
| PDC Clearance | No shortcut observed | MISSING | `tbl_PDCClearanceMaster` | [PDC Clearance](PDC_CLEARANCE.md) |
| Bank Reconciliation | Alt+B | MISSING | `tbl_BankReconciliation`, `tbl_LedgerPosting` | [Bank Reconciliation](BANK_RECONCILIATION.md) |
| Purchase Order | Shift+F9 | MISSING / OUTSIDE RENTAL MVP | `tbl_PurchaseOrderMaster`, `tbl_PurchaseOrderDetails` | [Purchase Order](PURCHASE_ORDER.md) |
| Purchase Invoice | No shortcut observed | MISSING / OUTSIDE RENTAL MVP | `tbl_PurchaseMaster`, `tbl_PurchaseDetails`, `tbl_PurchaseBillTax` | [Purchase Invoice](PURCHASE_INVOICE.md) |
| Sales Quotation | Alt+Q | MISSING / OUTSIDE RENTAL MVP | `tbl_SalesQuotationMaster`, `tbl_SalesQuotationDetails` | [Sales Quotation](SALES_QUOTATION.md) |
| Contract Agreement | Submenu indicator | PARTIAL | `VT_ContractMaster`, driver/document/vehicle tables | [Contract Agreement](CONTRACT_AGREEMENT.md) |
| Sales Invoice | F8 | PARTIAL / MVP REQUIRED | `tbl_SalesMaster`, `tbl_SalesDetails`, `tbl_SalesBillTax` | [Sales Invoice](SALES_INVOICE.md) |
| Credit Note (Invoice) | No shortcut observed | MISSING | `tbl_CreditNoteMaster`, `tbl_CreditNoteDetails` | [Credit Note](CREDIT_NOTE.md) |
| Debit Note | Ctrl+F9 | MISSING | `tbl_DebitNoteMaster`, `tbl_DebitNoteDetails` | [Debit Note](DEBIT_NOTE.md) |
| Vehicle Finance | No shortcut observed | MISSING | `tbl_FinanceHeader`, `tbl_FinanceDetail` | [Vehicle Finance](VEHICLE_FINANCE.md) |
| Traffic Fine | Submenu indicator | MISSING as a screen; PARTIAL as invoice source | `Traffic_Fine` | [Traffic Fine](TRAFFIC_FINE.md) |
| View Contracts | No shortcut observed | SUBSTANTIALLY IMPLEMENTED | Contract tables plus computed billing columns | [View Contracts](VIEW_CONTRACTS.md) |

`Salik Invoice` is not a separate item in the supplied Transactions menu, but Salik is part of Sales Invoice and the rental workflow. Its source mapping is documented in [Sales Invoice](SALES_INVOICE.md) and the dependency map.

## Recommended execution order

1. Resolve the MSSQL/procedure unknowns in this package and attach sanitized evidence to the affected dossier.
2. Stabilize Contract Agreement, View Contracts, Rental Invoice, and generic Sales Invoice draft behavior.
3. Complete Checkout, Active Rental, Fine/Salik allocation, Check-in, final invoice, Receipt Voucher, and the two registers.
4. Establish the shared accounting posting contract through Contra, Payment, Receipt, and Journal.
5. Add Credit/Debit Notes and Bank Reconciliation.
6. Add PDC Payable, PDC Receivable, PDC Clearance, and Vehicle Finance.
7. Add Sales Quotation, Purchase Order, and Purchase Invoice.

## Realistic schedule

| Delivery | One engineer | Parallel backend/frontend/research |
| --- | ---: | ---: |
| Close all documentation/procedure unknowns | 8-12 working days | 4-7 working days |
| Stable rental demo through receipt/registers | 5-8 weeks total | 4-6 weeks total |
| Full Transactions menu with verified accounting | 12-18 weeks total | 8-12 weeks total |

Parallel work is appropriate for independent read-only research, dossiers, isolated modules, frontend screens after API contracts are fixed, and test preparation. Posting rules, numbering, party balance, source consumption, contract status transitions, and shared modified files require a single owner and serial integration.

## Completion rule

A menu item moves to `COMPLETE` only when its dossier, API, frontend, automated tests, controlled MSSQL verification, and `docs/CURRENT_STATE.md` agree. Anything not demonstrated remains `UNKNOWN`.
