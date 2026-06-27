from sqlalchemy.orm import Session

from .repository import (
get_all_suppliers,
get_supplier_by_id,
create_supplier,
update_supplier,delete_supplier,
search_suppliers
)

from .schemas import SupplierCreate, SupplierUpdate

def get_all_suppliers_service(db: Session):
    return get_all_suppliers(db)

def get_supplier_by_id_service(
    db: Session,
    supplierId: int
):
    return get_supplier_by_id(db, supplierId)

def create_supplier_service(
db: Session,
supplier: SupplierCreate
):
    return create_supplier(db, supplier)

def update_supplier_service(
db: Session,
supplierId: int,
supplier: SupplierUpdate
):
    return update_supplier(
db,
supplierId,
supplier
)

def delete_supplier_service(
db: Session,
supplierId: int
):
    return delete_supplier(
db,
supplierId
)

def search_suppliers_service(
    db: Session,
    name: str = None,
    mobile: str = None
):
    return search_suppliers(
        db,
        name,
        mobile
    )