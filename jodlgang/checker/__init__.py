from os.path import join

import os
from jodlgang.path_utils import ExtraLoadPaths, SERVER_DIR

with ExtraLoadPaths(os.path.abspath(os.path.join(os.path.basename(__file__), '..', 'checker', 'jodlgang'))):
    import jodlgangchecker
    import jodlgangclient
    import constants
