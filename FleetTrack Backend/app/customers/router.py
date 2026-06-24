
from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.orm import Session
from .schemas import CustomerCreate, CustomerUpdate , CustomerResponse
from app.database.session import get_db
from .service import ( get_all_customers,
                      get_customer_by_id_service,
                        create_customer_service, 
                        update_customer_service, 
                        delete_customer_service 
                        ,search_customers_service)

router = APIRouter(prefix="/customers", tags=["Customers"])

@router.get("/search",response_model=list[CustomerResponse])
def search_customer(
    name: str = None,
    mobile: str = None,
    db: Session = Depends(get_db)
):
    return search_customers_service(
        db,
        name,
        mobile
    )

@router.get("/", response_model=list[CustomerResponse])
def get_customers(db:Session = Depends(get_db)):
    return get_all_customers(db)

@router.get("/{customerId}",response_model=CustomerResponse)
def get_customer(customerId:int, db:Session = Depends(get_db)):
    customer = get_customer_by_id_service(db, customerId)

    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.post("/", response_model=CustomerResponse)
def add_customer(customer:CustomerCreate, db:Session = Depends(get_db)):
    return create_customer_service(db, customer)

@router.put("/{customerId}", response_model=CustomerResponse)
def update_customer(customerId:int, customer:CustomerUpdate, db:Session = Depends(get_db)):
    updated_customer = update_customer_service(db, customerId, customer)

    if not updated_customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated_customer 

@router.delete("/{customerId}")
def delete_customer(customerId:int, db:Session = Depends(get_db)):
    deleted = delete_customer_service(db, customerId)

    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}

