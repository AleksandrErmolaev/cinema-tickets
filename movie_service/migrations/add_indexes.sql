CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_showtimes_movie_id ON showtimes(movie_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_showtimes_start_time ON showtimes(start_time);
