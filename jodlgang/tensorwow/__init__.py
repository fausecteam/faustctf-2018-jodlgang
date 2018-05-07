from os.path import join

from jodlgang.path_utils import ExtraLoadPaths, SERVER_DIR
import ipdb; ipdb.set_trace()
with ExtraLoadPaths(SERVER_DIR):
    from tensorwow import model
    from tensorwow import layers
    from tensorwow import initializer
    from tensorwow import functions
    from tensorwow import im2col



