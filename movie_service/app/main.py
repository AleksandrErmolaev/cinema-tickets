from fastapi import FastAPI
from .database import Base, engine
from .routers import movies, showtimes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Movie Service")

app.include_router(movies.router)
app.include_router(showtimes.router)