from sqlalchemy.orm import Session 
from app.generated_models.models import TblAccountLedger
from .schemas import CustomerCreate, CustomerUpdate

def get_all_customers(db:Session):
    return (
        db.query(TblAccountLedger)
        .filter(TblAccountLedger.accountGroupId == 26)  
        .all()
    )

def get_customer_by_id(db:Session, customerId:int):
    return(
        db.query(TblAccountLedger)
        .filter(TblAccountLedger.ledgerId == customerId)
        .first()
    )

def create_customer(db:Session, customer:CustomerCreate):
    db_customer = TblAccountLedger(
        **customer.model_dump(),
        accountGroupId=26,
    )

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    return db_customer

def update_customer(db:Session, customerId:int, customer:CustomerUpdate):
    db_customer = get_customer_by_id(db, customerId)
    if not db_customer:
        return None

    for key, value in customer.model_dump().items():
        setattr(db_customer, key, value)

    db.commit()
    db.refresh(db_customer)

    return db_customer

def delete_customer(db:Session, customerId:int):
    db_customer = get_customer_by_id(db, customerId)
    if not db_customer:
        return None

    db.delete(db_customer)
    db.commit()

    return True

def search_customers(db: Session, name: str = None, mobile: str = None):
    query = db.query(TblAccountLedger).filter(TblAccountLedger.accountGroupId == 26)

    if name:
        query = query.filter(TblAccountLedger.ledgerName.ilike(f"%{name}%"))
    if mobile:
        query = query.filter(TblAccountLedger.mobile.ilike(f"%{mobile}%"))

    return query.all()