import shutil

import imageio
from skimage import img_as_ubyte
from skimage.util import random_noise


def write_image(path, img):
    shutil._ensure_directory(path)
    imageio.imwrite(path, img)


def add_white_noise_ubyte(img):
    return img_as_ubyte(random_noise(img))

def add_white_noise(img):
    return random_noise(img)


def reflect_image(img):
    return img[:, ::-1]