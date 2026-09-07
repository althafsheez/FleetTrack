from sqlalchemy import select
from app.generated_models.models import VTVehTariffGroupMaster

TABLE = VTVehTariffGroupMaster.__table__


def list_groups(db, q=None):
    query = select(TABLE.c.TariffGroupId, TABLE.c.TariffGroupName)
    if q:
        query = query.where(TABLE.c.TariffGroupName.icontains(q, autoescape=True))
    return db.execute(query.order_by(TABLE.c.TariffGroupId)).mappings().all()


def get_group(db, group_id):
    return db.execute(select(TABLE).where(TABLE.c.TariffGroupId == group_id)).mappings().first()


def create_group(db, values):
    return db.execute(TABLE.insert().values(**values)).inserted_primary_key[0]


def update_group(db, group_id, values):
    db.execute(TABLE.update().where(TABLE.c.TariffGroupId == group_id).values(**values))


def delete_group(db, group_id):
    db.execute(TABLE.delete().where(TABLE.c.TariffGroupId == group_id))
