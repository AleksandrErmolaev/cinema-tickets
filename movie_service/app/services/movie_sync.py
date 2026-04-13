from sqlalchemy.orm import Session
from ..models import Movie
from ..tvmaze_client import get_popular_shows

def sync_movies(db: Session):
    shows = get_popular_shows()

    for show in shows[:50]:
        exists = db.query(Movie).filter(Movie.tmdb_id == show["id"]).first()
        if exists:
            continue

        movie = Movie(
            external_id=show["id"],
            title=show["name"],
            overview=show["summary"] or "No description",
            poster=show["image"]["medium"] if show["image"] else ""
        )

        db.add(movie)

    db.commit()