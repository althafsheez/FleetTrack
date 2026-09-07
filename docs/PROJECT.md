# FleetTrack project

FleetTrack's existing README describes a fleet and business management ERP for vehicle rental and transportation companies, including fleet operations, customers, suppliers, employees, finance, invoicing, payments, and reporting. The current client-demo MVP intentionally narrows that broader vision.

## Objective

Demonstrate a coherent customer → vehicle → tariff → contract → checkout → active rental → fines/Salik when applicable → check-in → invoice → receipt workflow using the existing MSSQL data, plus Sales Invoice and Receipt Registers. Extend the existing code quickly and preserve working functionality.

## Current implementation

The repository contains a Python FastAPI backend, SQLAlchemy generated mappings, Pydantic schemas, and pyodbc connection code. Customers, suppliers, and vehicle lookups are registered. Vehicles now have CRUD/search APIs; tariff-group name CRUD and rate read/initialize/update APIs are also implemented. Contract Agreement Add now has a backend create endpoint that writes contract header, driver snapshot, and vehicle assignment rows. Later transaction stages and a frontend are not implemented in the inspected repository. Live read-only Vehicle/Tariff/Contract lookup checks passed, alongside isolated regression tests. Live MSSQL writes remain unverified.

Frontend target specified by the user: Next.js, TypeScript, Tailwind CSS, shadcn/ui. These are targets, not installed/verified frontend components.

## Users

Intended audience: internal staff handling rental/fleet operations and billing/collections, inferred from the requested workflow. Exact job roles, permissions, branches, company boundaries, login requirements, and concurrent-user needs are UNKNOWN.

## Database dependency

The existing MSSQL database is authoritative. Current code targets database `Balance` on `localhost:1433`, using SQLAlchemy's `mssql+pyodbc` dialect and ODBC Driver 18 for SQL Server. Actual server availability, schema freshness, procedures, triggers, and production/test separation were not checked. Connection code currently embeds credentials; their values are intentionally omitted here.

## Constraints and unknowns

- Work on existing branch `mvp`; do not create a repository or rebuild the app.
- Preserve working code; generated models and database schema are read-only for this task.
- The user approved Vehicle/Tariff backend implementation; no commits or pushes were requested.
- Model declarations are evidence of the generated snapshot, not proof of current live schema or working business flows.
- Three Vehicle reference screenshots are now documented in `REFERENCE_APP.md`. Delivery date, approved demo records, other reference screens, precise pricing/status/accounting rules, and deployment environment remain UNKNOWN.

See [current state](CURRENT_STATE.md), [scope](MVP_SCOPE.md), and [demo checklist](DEMO.md).
