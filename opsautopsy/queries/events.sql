SELECT
    cluster_id,
    namespace,
    object_kind,
    object_name,
    reason,
    message,
    event_time
FROM events
WHERE
    cluster_id = ANY(%(clusters)s)
    AND event_time >= %(since)s
ORDER BY event_time ASC;
