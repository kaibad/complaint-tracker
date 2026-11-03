"""Database operations and business rules live here, away from the HTTP layer."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models, schemas

FINAL_STATUSES = {models.Status.RESOLVED, models.Status.REJECTED}


class ClosedComplaintError(Exception):
    """Raised when someone tries to change a complaint that is already closed."""


def create_complaint(
    db: Session, data: schemas.ComplaintCreate, owner_id: int | None = None
) -> models.Complaint:
    complaint = models.Complaint(**data.model_dump(), owner_id=owner_id)
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


def get_complaint(db: Session, complaint_id: int) -> models.Complaint | None:
    return db.get(models.Complaint, complaint_id)


def list_complaints(
    db: Session,
    status: models.Status | None = None,
    category: models.Category | None = None,
    skip: int = 0,
    limit: int = 20,
    owner_id: int | None = None,
) -> list[models.Complaint]:
    query = select(models.Complaint)
    if owner_id is not None:
        query = query.where(models.Complaint.owner_id == owner_id)
    if status:
        query = query.where(models.Complaint.status == status)
    if category:
        query = query.where(models.Complaint.category == category)
    query = query.order_by(models.Complaint.id.desc()).offset(skip).limit(limit)
    return list(db.scalars(query))


def update_status(
    db: Session, complaint: models.Complaint, data: schemas.ComplaintUpdate
) -> models.Complaint:
    if complaint.status in FINAL_STATUSES:
        raise ClosedComplaintError(f"Complaint is already {complaint.status.value}")
    complaint.status = data.status
    complaint.remarks = data.remarks
    db.commit()
    db.refresh(complaint)
    return complaint


def delete_complaint(db: Session, complaint: models.Complaint) -> None:
    db.delete(complaint)
    db.commit()


def stats(db: Session, owner_id: int | None = None) -> dict[str, int]:
    query = select(models.Complaint.status, func.count()).group_by(models.Complaint.status)
    if owner_id is not None:
        query = query.where(models.Complaint.owner_id == owner_id)
    rows = db.execute(query).all()
    result = {s.value: 0 for s in models.Status}
    for status, count in rows:
        result[status.value] = count
    result["total"] = sum(result.values())
    return result


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.scalar(select(models.User).where(models.User.username == username))
