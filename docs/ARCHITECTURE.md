# Architecture

## Vehicle/Tariff implementation update

Vehicle and tariff routers are now registered. They follow router → service → repository; repositories use SQLAlchemy Core statements against the existing generated table objects, returning row mappings. Services validate changed references and own commit/rollback behavior through a shared database-error helper. This avoids changing the generated ORM relationships. Customer/supplier and existing lookup architecture below is preserved. No frontend was implemented.


## Current architecture

`FleetTrack Backend/app/main.py` → registered customers/suppliers/lookups routers → mostly pass-through services → repositories → generated SQLAlchemy mappings → synchronous pyodbc/MSSQL connection.

`app/database/session.py:get_db` supplies and closes a session per dependency use. Repositories commit individual mutations. Customer/supplier schemas define requests and responses; lookups return query results without explicit response schemas. The customer list currently calls a repository function exposed in the service namespace. Vehicle service/router are empty. The generated file contains the broader legacy ERP schema, not implemented ERP services.

The frontend, workflow orchestration, authentication layer, and transaction APIs are absent from inspected code. Root GET `/` is a fixed process-health message, not database readiness verification.

## Recommended MVP direction (not implemented)

Next.js / TypeScript / Tailwind CSS / shadcn/ui → FastAPI REST API → service/repository layer → SQLAlchemy/generated models → existing MSSQL.

Extend the existing folder/module layout. Routers own HTTP handling, schemas own request/response contracts, services own verified business decisions, and repositories own queries/persistence. Existing customer/supplier/lookup layering already provides a useful foundation; preserve it rather than rewriting.

For future multi-table rental/billing operations, establish a single transaction boundary around each business action in coordination with repository commits. Do not add chained commits that can leave half-completed checkout or accounting entries. Confirm legacy posting requirements before selecting the boundary. This is a future recommendation, not a refactor authorized by the documentation task.

Keep generated mappings read-only. Translate API field names/types in ordinary schemas/services when useful instead of renaming database columns. Use confirmed existing status/lookup values, preserve Decimal precision, and verify write paths with controlled data. Runtime settings and secret handling need focused follow-up; no dependency changes are required for this documentation task.

Build the first UI only after the corresponding API behavior is verified. Reference captures should guide labels/navigation/visuals without replacing database evidence. See [API proposals](API.md), [relationships](RELATIONSHIPS.md), and [reference template](REFERENCE_APP.md).
