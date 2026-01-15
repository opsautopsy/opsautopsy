SELECT DISTINCT ON (cluster_id, namespace, workload_name)
    cluster_id,
    namespace,
    workload_name,
    workload_type,
    status,
    restart_count,
    observed_time
FROM workload_state
WHERE
    cluster_id = ANY(%(clusters)s)
    AND observed_time >= %(since)s
ORDER BY
    cluster_id,
    namespace,
    workload_name,
    observed_time DESC;
