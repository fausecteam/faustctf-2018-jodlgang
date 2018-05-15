import sys
from os.path import join, dirname, abspath


class ExtraLoadPaths:
    def __init__(self, *paths_to_add):
        self.paths_to_add = [abspath(p) for p in paths_to_add]
        self.preserved_sys_path = None

    def __enter__(self):
        self.preserved_sys_path = list(sys.path)
        sys.path.extend(self.paths_to_add)
        return None

    def __exit__(self, *args):
        #import ipdb; ipdb.set_trace()
        sys.path = list(self.preserved_sys_path)

SERVER_DIR = join(dirname(abspath(__file__)), '..', 'src', 'jodlgang')
PROTOTYPE_DIR = join(abspath(dirname(__file__)), '..', 'prototype')