import json

def export_json(report):
    return json.dumps(report, indent=2)
