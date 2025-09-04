from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from schemas.record_schemas import RecordCreate, RecordOut, RecordUpdate, OptionType, StatusType
from services.record_service import create_record, get_record, list_records, update_record, delete_record
from auth.jwt_handler import get_current_user, get_current_username
from database import get_db
from fastapi_cache.decorator import cache

router = APIRouter(prefix="/records", tags=["records"])


@router.post("/", response_model=RecordOut, status_code=status.HTTP_201_CREATED)
def create(record_in: RecordCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Create a new record. Requires authentication.
    """
    rec = create_record(db, record_in)
    return rec


@router.get("/", response_model=List[RecordOut])
@cache(expire=120)
def read_records(
    username: str = Depends(get_current_username),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    option_type: Optional[OptionType] = None,
    status: Optional[StatusType] = None,
):
    """
    List records. Cached 2 minutes per user (username included in dependencies).
    """
    return list_records(db, skip=skip, limit=limit, option_type=option_type, status=status)


@router.get("/{record_id}", response_model=RecordOut)
@cache(expire=120)
def read_record(record_id: int, username: str = Depends(get_current_username), db: Session = Depends(get_db)):
    """
    Get a single record by id. Cached 2 minutes per user.
    """
    rec = get_record(db, record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    return rec


@router.put("/{record_id}", response_model=RecordOut)
def put_record(record_id: int, updates: RecordUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Update a record. Authentication required. Cache will not be auto-invalidated (for production implement cache invalidation).
    """
    rec = get_record(db, record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    updated = update_record(db, rec, updates)
    return updated


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_record(record_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """
    Delete a record. Authentication required.
    """
    rec = get_record(db, record_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Record not found")
    delete_record(db, rec)
    return None
