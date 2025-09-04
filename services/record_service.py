from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import select
from models.record_model import Record, OptionType, StatusType
from schemas.record_schemas import RecordCreate, RecordUpdate

def create_record(db: Session, record_in: RecordCreate) -> Record:
    """Create and persist a new Record."""
    rec = Record(
        option_type=record_in.option_type,
        description=record_in.description,
        status=record_in.status,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

def get_record(db: Session, record_id: int) -> Optional[Record]:
    """Get a record by id."""
    return db.query(Record).filter(Record.id == record_id).first()

def list_records(
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    option_type: Optional[OptionType] = None,
    status: Optional[StatusType] = None
) -> List[Record]:
    """List records with optional filters."""
    q = db.query(Record)
    if option_type:
        q = q.filter(Record.option_type == option_type)
    if status:
        q = q.filter(Record.status == status)
    return q.offset(skip).limit(limit).all()

def update_record(db: Session, record: Record, updates: RecordUpdate) -> Record:
    """Apply updates and persist."""
    if updates.option_type is not None:
        record.option_type = updates.option_type
    if updates.description is not None:
        record.description = updates.description
    if updates.status is not None:
        record.status = updates.status
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def delete_record(db: Session, record: Record) -> None:
    """Delete the record."""
    db.delete(record)
    db.commit()
