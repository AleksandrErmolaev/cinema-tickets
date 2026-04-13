from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..schemas import ShowTimeCreate
from ..services.showtime_service import create_showtime
from ..models import ShowTime

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/showtimes")
def add_showtime(data: ShowTimeCreate, db: Session = Depends(get_db)):
    return create_showtime(db, data)

@router.get("/showtimes/{movie_id}")
def get_showtimes(movie_id: int, db: Session = Depends(get_db)):
    return db.query(ShowTime).filter_by(movie_id=movie_id).all()