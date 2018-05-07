import json

import os

DIR_FORMAT_STR = '/media/honululu/Data/facescrub_final_directory/{step}/{type}/faces/{name}/'
CLASS_MAP_PATH = '../src/jodlgang/class_label_mapping.json'


def load_class_map(class_map_path=None):
    if class_map_path is None:
        class_map_path = CLASS_MAP_PATH

    with open(class_map_path) as f:
        return json.load(f)


def available_faces(name, dir_fmt_str=None):
    if dir_fmt_str is None:
        dir_fmt_str = DIR_FORMAT_STR

    to_try = [dir_fmt_str.format(step=s, type=t, name=name) for s in {'training', 'validation'} for t in {'actors', 'actresses'}]
    for d in to_try:
        if os.path.isdir(d):
            return [os.path.join(d, f) for f in os.listdir(d)]

    raise RuntimeError("Could not find any faces for {}".format(name))


