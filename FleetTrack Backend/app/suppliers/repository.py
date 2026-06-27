from sqlalchemy.orm import Session 
from app.generated_models.models import TblAccountLedger
from .schemas import SupplierCreate, SupplierUpdate

def get_all_suppliers(db:Session):
    return (
        db.query(TblAccountLedger)
        .filter(TblAccountLedger.accountGroupId == 22)  
        .all()
    )

def get_supplier_by_id(db:Session, supplierId:int):
    return(
        db.query(TblAccountLedger)
        .filter(TblAccountLedger.ledgerId == supplierId,
                TblAccountLedger.accountGroupId == 22)
        .first()
    )

def create_supplier(db:Session, supplier:SupplierCreate):
    supplier_data = supplier.model_dump()
    supplier_data["ledgerName"] = supplier_data["ledgerName"].upper()
    db_supplier = TblAccountLedger(
        **supplier_data,
        accountGroupId=22,
    )

    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)

    return db_supplier
def update_supplier(db: Session, supplierId: int, supplier: SupplierUpdate):
    db_supplier = get_supplier_by_id(db, supplierId)

    if not db_supplier:
        return None

    supplier_data = supplier.model_dump()

    supplier_data["ledgerName"] = supplier_data["ledgerName"].upper()

    for key, value in supplier_data.items():
        setattr(db_supplier, key, value)

    db.commit()
    db.refresh(db_supplier)

    return db_supplier

def delete_supplier(db:Session, supplierId:int):
    db_supplier = get_supplier_by_id(db, supplierId)
    if not db_supplier:
        return None

    db.delete(db_supplier)
    db.commit()

    return True

def search_suppliers(db: Session, name: str = None, mobile: str = None):
    query = db.query(TblAccountLedger).filter(TblAccountLedger.accountGroupId == 22)

    if name:
        query = query.filter(TblAccountLedger.ledgerName.ilike(f"%{name}%"))
    if mobile:
        query = query.filter(TblAccountLedger.mobile.ilike(f"%{mobile}%"))

    return query.all()