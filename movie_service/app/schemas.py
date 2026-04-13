from pydantic import BaseModel
from datetime import datetime

class MovieOut(BaseModel):
    id: int
    title: str
    overview: str
    poster: str

    class Config:
        from_attributes = True


class ShowTimeCreate(BaseModel):
    movie_id: int
    start_time: datetime
    hall: str