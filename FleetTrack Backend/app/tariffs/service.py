from decimal import Decimal
from fastapi import HTTPException
from app.generated_models.models import Base
from app.master_data import database_errors, require_unused
from . import repository as repo
from .schemas import TariffRatesUpdate


def get_group(db, group_id):
    with database_errors(db):
        row = repo.get_group(db, group_id)
        if row is None:
            raise HTTPException(404, "Tariff group not found")
        return row


def list_groups(db, **filters):
    with database_errors(db):
        return repo.list_groups(db, **filters)


def create_group(db, payload):
    with database_errors(db):
        values = {name: Decimal("0.00") for name in TariffRatesUpdate.model_fields}
        values.update(payload.model_dump())
        group_id = repo.create_group(db, values)
        row = repo.get_group(db, group_id)
        db.commit()
        return row


def update_group(db, group_id, payload):
    with database_errors(db):
        get_group(db, group_id)
        values = payload.model_dump(exclude_unset=True)
        if values:
            repo.update_group(db, group_id, values)
        row = repo.get_group(db, group_id)
        db.commit()
        return row


def delete_group(db, group_id):
    with database_errors(db):
        get_group(db, group_id)
        candidates = [(t, c) for t in Base.metadata.tables.values() if t is not repo.TABLE
                      for c in t.c if c.name.lower() == "tariffgroupid"]
        require_unused(db, candidates, group_id)
        repo.delete_group(db, group_id)
        db.commit()
