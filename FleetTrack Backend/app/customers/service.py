from sqlalchemy.orm import Session

from .repository import (
get_all_customers,
get_customer_by_id,
create_customer,
update_customer,
delete_customer,
search_customers
,
get_customers_page,
search_customers_page
)

from .schemas import CustomerCreate, CustomerUpdate

def get_all_customers_service(db: Session):
    return get_all_customers(db)


def get_customers_page_service(db: Session, offset: int, limit: int):
    items, total = get_customers_page(db, offset, limit)
    return {"items": items, "total": total, "offset": offset, "limit": limit}

def get_customer_by_id_service(
    db: Session,
    customerId: int
):
    return get_customer_by_id(db, customerId)

def create_customer_service(
db: Session,
customer: CustomerCreate
):
    return create_customer(db, customer)

def update_customer_service(
db: Session,
customerId: int,
customer: CustomerUpdate
):
    return update_customer(
db,
customerId,
customer
)

def delete_customer_service(
db: Session,
customerId: int
):
    return delete_customer(
db,
customerId
)

def search_customers_service(
    db: Session,
    name: str = None,
    mobile: str = None
):
    return search_customers(
        db,
        name,
        mobile
    )


def search_customers_page_service(
    db: Session,
    offset: int,
    limit: int,
    name: str = None,
    mobile: str = None,
):
    items, total = search_customers_page(db, offset, limit, name, mobile)
    return {"items": items, "total": total, "offset": offset, "limit": limit}
