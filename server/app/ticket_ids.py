import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LearningProject

TICKET_ID_PREFIX = "VELODESK-"
TICKET_ID_PATTERN = re.compile(r"^VELODESK-(\d+)$", re.IGNORECASE)


def parse_ticket_number(ticket_id: str) -> int | None:
    match = TICKET_ID_PATTERN.match(ticket_id.strip())
    if not match:
        return None
    return int(match.group(1))


def format_ticket_id(number: int) -> str:
    return f"{TICKET_ID_PREFIX}{number}"


def next_ticket_id(db: Session) -> str:
    ticket_ids = db.scalars(select(LearningProject.id)).all()
    max_number = 0
    for ticket_id in ticket_ids:
        number = parse_ticket_number(ticket_id)
        if number is not None and number > max_number:
            max_number = number
    return format_ticket_id(max_number + 1)
