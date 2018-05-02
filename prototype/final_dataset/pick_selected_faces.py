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


parser = argparse.ArgumentParser()
parser.add_argument('dataset_directory')
parser.add_argument('out_dir')
parser.add_argument('-n', '--number_of_pictures_per', type=int, default=20)
parser.add_argument('-o', '--output_shape', default='250x250')
args = parser.parse_args()

output_shape = tuple(map(int, args.output_shape.split('x')))

shutil.rmtree(args.out_dir, ignore_errors=True)

for category in os.listdir(args.dataset_directory):
    faces_dir = os.path.join(args.dataset_directory, category, 'faces')

    for celeb in os.listdir(faces_dir):
        print("Processing celebrity {} ... ".format(celeb))
        celeb_dir = os.path.join(faces_dir, celeb)

        images = os.listdir(celeb_dir)

        selected_pics = np.random.permutation(images)[:args.number_of_pictures_per]

        for pic_path in selected_pics:
            pic_path = os.path.join(celeb_dir, pic_path)

            split_name = os.path.basename(pic_path).split('.')
            file_name, file_ext = '.'.join(split_name[:-1]), split_name[-1]

            img = imageio.imread(pic_path)

            #ipdb.set_trace()
            resized = resize(img, output_shape=output_shape)

            out_dir = os.path.join(args.out_dir, category, 'faces', celeb)

            #write_image(os.path.join(out_dir, '{}_resized.{}'.format(file_name, file_ext)), img)
            write_image(os.path.join(out_dir, '{}_noise0.{}'.format(file_name, file_ext)), add_white_noise(img))
            write_image(os.path.join(out_dir, '{}_noise1.{}'.format(file_name, file_ext)), add_white_noise(img))
            write_image(os.path.join(out_dir, '{}_noise2.{}'.format(file_name, file_ext)), add_white_noise(img))
            write_image(os.path.join(out_dir, '{}_noise3.{}'.format(file_name, file_ext)), add_white_noise(img))
