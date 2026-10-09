# API Map

This is a compact map of the main backend route families. See `docs/API.md` for deeper behavior notes.

## App Registration

Routes are registered from:

```text
FleetTrack Backend/app/main.py
```

Most authenticated routes depend on the current user session.

## Authentication

```text
POST /auth/login
GET  /auth/me
POST /auth/logout
```

Module:

```text
FleetTrack Backend/app/auth/
```

## Master Data

```text
/customers
/suppliers
/lookups
/vehicles
/vehicle-tariff-groups
```

Modules:

```text
FleetTrack Backend/app/customers/
FleetTrack Backend/app/suppliers/
FleetTrack Backend/app/lookups/
FleetTrack Backend/app/vehicles/
FleetTrack Backend/app/tariffs/
```

## Contracts and Rental Billing

```text
/contracts
/rental-invoices
```

Modules:

```text
FleetTrack Backend/app/contracts/
FleetTrack Backend/app/rental_billing/
FleetTrack Backend/app/sales_invoices/
```

## Voucher Workflows

```text
/contra-vouchers
/payment-vouchers
/receipt-vouchers
```

Modules:

```text
FleetTrack Backend/app/contra_vouchers/
FleetTrack Backend/app/payment_vouchers/
FleetTrack Backend/app/receipt_vouchers/
```

## PDC Workflows

```text
/pdc-payables
/pdc-receivables
/pdc-clearances
```

Modules:

```text
FleetTrack Backend/app/pdc_payables/
FleetTrack Backend/app/pdc_receivables/
FleetTrack Backend/app/pdc_clearances/
FleetTrack Backend/app/pdc_vouchers/
```

## Transaction Operations

These are operational transaction tools rather than full commercial document families.

```text
GET  /bank-reconciliations/accounts
GET  /bank-reconciliations/page
PUT  /bank-reconciliations

GET  /traffic-fines/page
GET  /traffic-fines/traffic-files
POST /traffic-fines
```

Module:

```text
FleetTrack Backend/app/transaction_operations/
```

Current traffic-fine limitation:

```text
Edit, delete, and single-ticket detail routes are not implemented yet.
```

## Commercial Transactions

Shared prefix:

```text
/transaction-documents
```

Kinds:

```text
purchase-orders
purchase-invoices
sales-quotations
credit-notes
debit-notes
vehicle-finance
```

Shared CRUD-style routes:

```text
GET    /transaction-documents/{kind}/page
GET    /transaction-documents/{kind}/{identity}
POST   /transaction-documents/{kind}
PATCH  /transaction-documents/{kind}/{identity}
DELETE /transaction-documents/{kind}/{identity}
POST   /transaction-documents/{kind}/{identity}/post
POST   /transaction-documents/{kind}/{identity}/unpost
```

Supporting routes:

```text
GET  /transaction-documents/lookups/{name}
GET  /transaction-documents/lookups/exchange-rates
GET  /transaction-documents/references
GET  /transaction-documents/sources/{kind}/{identity}
POST /transaction-documents/vehicle-finance/preview
GET  /transaction-documents/sales-register/page
POST /transaction-documents/sales-register/export
```

Module:

```text
FleetTrack Backend/app/commercial_transactions/
```

Core table mapping:

| Kind | Tables |
| --- | --- |
| `purchase-orders` | `tbl_PurchaseOrderMaster`, `tbl_PurchaseOrderDetails` |
| `purchase-invoices` | `tbl_PurchaseMaster`, `tbl_PurchaseDetails`, `tbl_PurchaseBillTax` |
| `sales-quotations` | `tbl_SalesQuotationMaster`, `tbl_SalesQuotationDetails` |
| `vehicle-finance` | `tbl_FinanceHeader`, `tbl_FinanceDetail` |
| `credit-notes` | `tbl_SalesReturnMaster`, `tbl_SalesReturnDetails`, `tbl_SalesReturnBillTax` |
| `debit-notes` | `tbl_DebitNoteMaster`, `tbl_DebitNoteDetails` |
