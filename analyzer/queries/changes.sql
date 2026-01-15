SELECT
    cluster_id,
    namespace,
    object_name,
    message,
    event_time
FROM events
WHERE
    cluster_id = ANY(%(clusters)s)
    AND reason IN (
        'ScalingReplicaSet',
        'SuccessfulCreate',
        'SuccessfulDelete',
        'Pulling',
        'Pulled'
    )
    AND event_time >= %(since)s
ORDER BY event_time ASC;
