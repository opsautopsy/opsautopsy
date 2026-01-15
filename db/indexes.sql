CREATE INDEX IF NOT EXISTS idx_events_time
ON events (event_time);

CREATE INDEX IF NOT EXISTS idx_events_cluster
ON events (cluster_id);
