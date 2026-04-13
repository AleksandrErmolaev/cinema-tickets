CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_booking_id ON payments(booking_id);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_status ON payments(status);
