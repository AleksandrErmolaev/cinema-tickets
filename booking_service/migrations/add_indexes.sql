CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_user_id_status ON bookings(user_id, status);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_session_id ON bookings(session_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bookings_expires_at ON bookings(expires_at) WHERE status = 'pending';
