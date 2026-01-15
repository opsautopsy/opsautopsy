CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
    cluster_id TEXT NOT NULL,
    namespace TEXT NOT NULL,
    object_kind TEXT NOT NULL,
    object_name TEXT NOT NULL,
    reason TEXT,
    message TEXT,
    event_time TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS workload_state (
    id SERIAL PRIMARY KEY,
    cluster_id TEXT NOT NULL,
    namespace TEXT NOT NULL,
    workload_name TEXT NOT NULL,
    workload_type TEXT NOT NULL,
    status TEXT,
    restart_count INT,
    observed_time TIMESTAMPTZ NOT NULL
);
