import json


def load_report_config(path):
    with open(path) as handle:
        return json.load(handle)
