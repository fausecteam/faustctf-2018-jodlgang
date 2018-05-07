import json
from os.path import dirname, join


def get_celeb_labels():
    with open(join(dirname(__file__), 'class_label_mapping.json')) as f:
        return json.load(f)

def get_renamed_labels():
    with open(join(dirname(__file__), 'class_label_mapping_names.json')) as f:
        return json.load(f)
