from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models, schemas


def list_tickets(db: Session, status: str | None = None) -> list[models.Ticket]:
    stmt = select(models.Ticket).order_by(models.Ticket.created_at.desc())
    if status:
        stmt = stmt.where(models.Ticket.status == status)
    return list(db.scalars(stmt).all())


def get_ticket(db: Session, ticket_id: int) -> models.Ticket | None:
    return db.get(models.Ticket, ticket_id)


def create_ticket(db: Session, data: schemas.TicketCreate) -> models.Ticket:
    ticket = models.Ticket(**data.model_dump())
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket(
    db: Session, ticket: models.Ticket, data: schemas.TicketUpdate
) -> models.Ticket:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket


def delete_ticket(db: Session, ticket: models.Ticket) -> None:
    db.delete(ticket)
    db.commit()


def stats(db: Session) -> schemas.StatsOut:
    total = db.scalar(select(func.count()).select_from(models.Ticket)) or 0

    status_rows = db.execute(
        select(models.Ticket.status, func.count()).group_by(models.Ticket.status)
    ).all()
    priority_rows = db.execute(
        select(models.Ticket.priority, func.count()).group_by(models.Ticket.priority)
    ).all()

    return schemas.StatsOut(
        total=total,
        by_status={status: count for status, count in status_rows},
        by_priority={priority: count for priority, count in priority_rows},
    )
