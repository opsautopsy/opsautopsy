import psycopg2
from psycopg2.extras import execute_values

def get_connection(db_url):
    return psycopg2.connect(db_url)

def insert_events(conn, rows):
    query = """
    INSERT INTO events
    (cluster_id, namespace, object_kind, object_name, reason, message, event_time)
    VALUES %s
    """
    with conn.cursor() as cur:
        execute_values(cur, query, rows)
    conn.commit()
