import random

import imageio
import os

import shutil

import ipdb
import numpy as np
from skimage import img_as_ubyte
from skimage.transform import resize
from skimage.io import imread
import argparse

from skimage.util import random_noise

random.seed(0)
np.random.seed(0)


def write_image(path, img):
    shutil._ensure_directory(path)
    imageio.imwrite(path, img)

def add_white_noise(img):
    return img_as_ubyte(random_noise(img))

def reflect_image(img):
    return img[:, ::-1]


parser = argparse.ArgumentParser()
parser.add_argument('dataset_directory')
args = parser.parse_args()


for category in os.listdir(args.dataset_directory):
    faces_dir = os.path.join(args.dataset_directory, category, 'faces')

    for celeb in os.listdir(faces_dir):
        print("Processing celebrity {} ... ".format(celeb))
        celeb_dir = os.path.join(faces_dir, celeb)

        images = os.listdir(celeb_dir)

        for i, pic_path in enumerate(images):
            pic_path = os.path.join(celeb_dir, pic_path)

            img = imageio.imread(pic_path)
            if len(img.shape) == 2 or img.shape[2] == 1:
                os.unlink(pic_path)

