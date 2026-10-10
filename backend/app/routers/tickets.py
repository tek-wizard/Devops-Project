from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db
from ..models import STATUSES

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.get("", response_model=list[schemas.TicketOut])
def list_tickets(
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    if status_filter and status_filter not in STATUSES:
        raise HTTPException(status_code=422, detail=f"status must be one of {STATUSES}")
    return crud.list_tickets(db, status=status_filter)


# keep this above /{ticket_id} so "stats" isn't read as an id
@router.get("/stats/summary", response_model=schemas.StatsOut)
def ticket_stats(db: Session = Depends(get_db)):
    return crud.stats(db)


@router.post("", response_model=schemas.TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: schemas.TicketCreate, db: Session = Depends(get_db)):
    return crud.create_ticket(db, payload)


@router.get("/{ticket_id}", response_model=schemas.TicketOut)
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.put("/{ticket_id}", response_model=schemas.TicketOut)
def update_ticket(
    ticket_id: int, payload: schemas.TicketUpdate, db: Session = Depends(get_db)
):
    ticket = crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return crud.update_ticket(db, ticket, payload)


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    crud.delete_ticket(db, ticket)
    return None
