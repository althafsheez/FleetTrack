"""Shared query and transaction helpers for vehicle and tariff master endpoints."""
from contextlib import contextmanager
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.generated_models.models import Base


@contextmanager
def database_errors(db):
    try:
        yield
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "The operation conflicts with existing database constraints or references.") from None
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(503, "Database operation failed. Check the current record before retrying or contact support.") from None


def require_reference(db, table_name, column, value, field):
    if value is None:
        return
    table = Base.metadata.tables[table_name]
    if db.execute(select(table.c[column]).where(table.c[column] == value).limit(1)).first() is None:
        raise HTTPException(422, f"{field}: selected lookup record does not exist")


def require_unused(db, candidates, value):
    """Conservatively block deletion for mapped candidate references, without cascading."""
    for table, column in candidates:
        if db.execute(select(column).where(column == value).limit(1)).first() is not None:
            raise HTTPException(409, f"Cannot delete: referenced by {table.name}.{column.name}")
