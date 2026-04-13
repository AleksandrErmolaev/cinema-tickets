from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    external_id = Column(Integer, unique=True)
    title = Column(String)
    overview = Column(String)
    poster = Column(String)

    showtimes = relationship("ShowTime", back_populates="movie")


class ShowTime(Base):
    __tablename__ = "showtimes"

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    start_time = Column(DateTime)
    hall = Column(String)

    movie = relationship("Movie", back_populates="showtimes")