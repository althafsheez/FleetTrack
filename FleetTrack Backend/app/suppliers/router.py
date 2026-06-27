
from fastapi import APIRouter, Depends , HTTPException
from sqlalchemy.orm import Session
from .schemas import SupplierCreate, SupplierUpdate , SupplierResponse
from app.database.session import get_db
from .service import ( get_all_suppliers_service,
                      get_supplier_by_id_service,
                        create_supplier_service, 
                        update_supplier_service, 
                        delete_supplier_service 
                        ,search_suppliers_service)

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.get("/search",response_model=list[SupplierResponse])
def search_supplier(
    name: str = None,
    mobile: str = None,
    db: Session = Depends(get_db)
):
    return search_suppliers_service(
        db,
        name,
        mobile
    )

@router.get("/", response_model=list[SupplierResponse])
def get_suppliers(db:Session = Depends(get_db)):
    return get_all_suppliers_service(db)

@router.get("/{supplierId}",response_model=SupplierResponse)
def get_supplier(supplierId:int, db:Session = Depends(get_db)):
    supplier = get_supplier_by_id_service(db, supplierId)

    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier

@router.post("/", response_model=SupplierResponse)
def add_supplier(supplier:SupplierCreate, db:Session = Depends(get_db)):
    return create_supplier_service(db, supplier)

@router.put("/{supplierId}", response_model=SupplierResponse)
def update_supplier(supplierId:int, supplier:SupplierUpdate, db:Session = Depends(get_db)):
    updated_supplier = update_supplier_service(db, supplierId, supplier)

    if not updated_supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return updated_supplier 

@router.delete("/{supplierId}")
def delete_supplier(supplierId:int, db:Session = Depends(get_db)):
    deleted = delete_supplier_service(db, supplierId)

    if not deleted:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return {"message": "Supplier deleted successfully"}

