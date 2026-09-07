from sqlalchemy import select
from sqlalchemy.orm import Session

from app.generated_models.models import t_VT_ApplicationUsers


def get_user_by_username(db: Session, username: str):
    table = t_VT_ApplicationUsers
    return db.execute(
        select(
            table.c.UserID,
            table.c.UserName,
            table.c.Password,
            table.c.DisplayName,
            table.c.Status,
        ).where(table.c.UserName == username)
    ).mappings().first()
