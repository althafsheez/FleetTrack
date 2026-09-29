# FleetTrack agent instructions

## Project and priorities

FleetTrack is an existing, partially implemented vehicle/rental management application. Complete it quickly as production-bound client-demo code by extending its existing implementation.

Priority order: (1) production-safe working client demo, (2) correct real MSSQL data, (3) correct core business workflow, (4) reliable APIs, (5) working frontend, (6) visual similarity to the reference application, (7) UX polish, (8) code elegance. Speed matters; avoid overengineering.

## Start here

Read `docs/PROJECT.md`, `docs/CURRENT_STATE.md`, `docs/MVP_SCOPE.md`, and the documents relevant to the task before editing. Inspect Git status and existing code. The working branch for production-bound implementation is `prod` unless the user explicitly chooses another checkpoint or branch. Preserve all pre-existing user changes.

Continue from the existing repository. Do not rebuild the application, rewrite working modules without a concrete reason, perform unrelated cleanup, or refactor solely for consistency. Keep changes focused on the authorized task.

## Technology

Current backend: Python, FastAPI, SQLAlchemy, Pydantic, and pyodbc against existing Microsoft SQL Server. Frontend target: Next.js, TypeScript, Tailwind CSS, shadcn/ui. No frontend implementation was found in the initial audit.

## Database and generated code

MSSQL is authoritative. Application code must adapt to it. Do not redesign the database, rename tables/columns, drop/recreate tables, or modify constraints/foreign keys. Do not invent relationships from similar column names. See `docs/DATABASE.md` and `docs/RELATIONSHIPS.md` for evidence and unresolved questions.

`FleetTrack Backend/app/generated_models/models.py` contains the generated SQLAlchemy mappings. Treat it as generated/read-only code. Do not edit it manually unless explicitly instructed, and never place business logic there. A suspicious mapping is a question to investigate, not permission to change the mapping or schema.

Do not copy credentials or customer data into documentation, logs, or reference captures. Existing hard-coded connection credentials are a documented issue, not a template for new code.

## Backend architecture

Prefer router → service → repository → SQLAlchemy/generated model → MSSQL.

- `router.py`: HTTP paths, dependencies, status codes, request handling.
- `schemas.py`: Pydantic request/response contracts.
- `service.py`: business logic and workflow coordination.
- `repository.py`: database queries and persistence.

Do not force working code into this structure merely for consistency. Refactor only where it helps the MVP. Preserve current customer/supplier group filtering and lookup behavior unless a verified requirement warrants a change.

## Core MVP workflow

Customer → Vehicle → Tariff → Contract → Checkout → Active Rental → Fines / Salik → Check-in → Invoice → Receipt.

Sales Invoice Register and Receipt Register are also in scope. Detailed status values, pricing rules, charge allocation, and accounting behavior remain subject to confirmation; do not invent them.

## Verification and documentation

After future implementation changes, run relevant backend checks, test affected endpoints, verify affected database queries, and run frontend typecheck/build when applicable. Fix errors introduced by the change. Use controlled test data for writes. Never claim functionality works merely because code exists. Record what was actually tested, outcomes, and limits; use UNKNOWN when runtime behavior is unverified. Update the relevant context documents when implementation or evidence changes.

## User notification preference

When a substantial FleetTrack task finishes, send a short Gmail notification to `me` so the user gets a phone notification. Include what was completed, what was verified, and any important blocker or follow-up. Do not include credentials, customer data, or long command output in the email. If Gmail is unavailable in a future session, clearly mention that in the final response.

## Current task boundary

The initial repository-preparation task is documentation and analysis only. Do not implement features, build frontend pages, change application code or schema, upgrade dependencies, commit, or push as part of that task. Wait for the user's explicit approval before starting implementation. Later explicit user authorization determines the scope of subsequent tasks.
