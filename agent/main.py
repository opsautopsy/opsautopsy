from kubernetes import config
from collectors.events import stream_events
from storage.postgres import get_connection, insert_events
from config import CLUSTER_ID, DATABASE_URL

def main():
    config.load_incluster_config()
    conn = get_connection(DATABASE_URL)

    buffer = []
    for event in stream_events(CLUSTER_ID):
        buffer.append(event)

        if len(buffer) >= 50:
            insert_events(conn, buffer)
            buffer.clear()

if __name__ == "__main__":
    main()
