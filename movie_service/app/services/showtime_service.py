from sqlalchemy.orm import Session
from ..models import ShowTime

def create_showtime(db: Session, data):
    showtime = ShowTime(**data.dict())
    db.add(showtime)
    db.commit()
    db.refresh(showtime)
    return showtime