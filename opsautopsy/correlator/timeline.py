from datetime import timezone
from opsautopsy.db import get_connection



def build_timeline(clusters=None, namespace=None, start_time=None):
    """
    Build an incident timeline from persisted Kubernetes events.
    """

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT
            cluster_id,
            namespace,
            object_kind,
            object_name,
            reason,
            message,
            event_time
        FROM events
        WHERE 1=1
    """

    params = []

    if clusters:
        query += " AND cluster_id = ANY(%s)"
        params.append(clusters)

    if namespace:
        query += " AND namespace = %s"
        params.append(namespace)

    if start_time:
        query += " AND event_time >= %s"
        params.append(start_time.astimezone(timezone.utc))

    query += " ORDER BY event_time ASC"

    cur.execute(query, params)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    timeline = []

    for row in rows:
        timeline.append({
            "cluster": row[0],
            "namespace": row[1],
            "kind": row[2],
            "name": row[3],
            "reason": row[4],
            "message": row[5],
            "time": row[6],
        })

    return timeline
