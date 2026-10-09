# MVP Status

This file summarizes the project state for a quick GitHub review. It is intentionally high-level; `docs/CURRENT_STATE.md` contains the detailed audit trail.

## Status Legend

| Status | Meaning |
| --- | --- |
| Implemented | Core workflow exists in backend and frontend, with focused verification notes |
| Partial | Useful workflow exists, but known gaps or guarded operations remain |
| Missing | No meaningful implementation found |
| Unknown | Runtime behavior has not been verified enough to claim support |

## Feature Status

| Feature | Status | Notes |
| --- | --- | --- |
| Login/session authentication | Implemented | Uses existing portal user records and session cookie |
| Customer master | Implemented | Ledger-backed pages and APIs |
| Supplier master | Implemented | Ledger-backed pages and APIs |
| Vehicle master | Implemented | CRUD/search against existing vehicle tables |
| Tariff groups and rates | Implemented | Group and rate management |
| Contract add/view/edit/print | Partial | Main workflow exists; full rental lifecycle remains larger than MVP |
| Rental invoice drafts | Partial | Contract-aware draft creation; posting lifecycle outside this slice |
| Sales invoice register | Partial | Register and exports exist; full legacy print/parity incomplete |
| Contra voucher | Implemented | Save writes accounting effects directly |
| Payment voucher | Implemented | Draft, post, unpost, allocation, print |
| Receipt voucher | Implemented | Draft, post, unpost, allocation, print |
| PDC payable | Implemented | Register, allocation, save, print |
| PDC receivable | Implemented | Register, allocation, save, print |
| PDC clearance | Implemented | Cleared/bounced workflows with guards |
| Bank reconciliation | Partial | Bank posting list and statement-date save |
| Traffic fines | Partial | List/search/add; edit/delete/detail missing |
| Purchase orders | Partial | Shared commercial document workflow |
| Purchase invoices | Partial | Draft and verified base-currency posting; inventory posting guarded |
| Sales quotations | Partial | Create/update/delete and approval flag |
| Credit notes | Partial | Draft workflow exists; posting blocked pending verification |
| Debit notes | Partial | Ledger-line workflow exists; narrower than full ERP parity |
| Vehicle finance | Partial | Schedule generation and finalize-only posting |

## Known Gaps Worth Calling Out

- Traffic fines do not yet have edit, delete, or single-ticket detail endpoints.
- Credit-note posting is intentionally blocked until legacy accounting rules are verified.
- Inventory purchase posting is intentionally blocked until stock effects are verified.
- Some foreign-currency paths are guarded or limited to verified AED/base-currency cases.
- Full legacy report/print parity is not complete.
- The backend database connection should be moved fully into environment configuration before production use.

## What Makes The MVP Credible

- It uses the existing MSSQL schema instead of inventing new tables.
- Generated SQLAlchemy mappings are treated as read-only.
- Transaction modules use explicit service/repository boundaries.
- Risky accounting operations include state checks and downstream-reference guards.
- Feature documentation records what is implemented, what is verified, and what is intentionally deferred.
