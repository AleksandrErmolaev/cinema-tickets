from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Movie
from ..services.movie_sync import sync_movies

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/sync")
def sync(db: Session = Depends(get_db)):
    sync_movies(db)
    return {"status": "movies synced"}

@router.get("/movies")
def list_movies(db: Session = Depends(get_db)):
    return db.query(Movie).all()