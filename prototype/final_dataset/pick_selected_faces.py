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
parser.add_argument('out_dir')
parser.add_argument('-n', '--number_of_pictures_per', type=int, default=20)
parser.add_argument('-o', '--output_shape', default='224x224')
parser.add_argument('-v', '--validation-split', default=0.2)
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
        training_pic_length = int(len(selected_pics) * args.validation_split)

        for i, pic_path in enumerate(selected_pics):
            pic_path = os.path.join(celeb_dir, pic_path)

            split_name = os.path.basename(pic_path).split('.')
            file_name, file_ext = '.'.join(split_name[:-1]), split_name[-1]

            img = imageio.imread(pic_path)

            #ipdb.set_trace()
            resized = resize(img, output_shape=output_shape)
            reflected = reflect_image(resized)

            if i < training_pic_length:
                out_dir = os.path.join(args.out_dir, 'validation', category, 'faces', celeb)
            else:
                out_dir = os.path.join(args.out_dir, 'training', category, 'faces', celeb)

            write_image(os.path.join(out_dir, '{}_original_noise0.{}'.format(file_name, file_ext)), add_white_noise(resized))
            write_image(os.path.join(out_dir, '{}_original_noise1.{}'.format(file_name, file_ext)), add_white_noise(resized))
            write_image(os.path.join(out_dir, '{}_reflected_noise0.{}'.format(file_name, file_ext)), add_white_noise(reflected))
            write_image(os.path.join(out_dir, '{}_reflected_noise1.{}'.format(file_name, file_ext)), add_white_noise(reflected))
            #write_image(os.path.join(out_dir, '{}_original_noise2.{}'.format(file_name, file_ext)), add_white_noise(resized))
            #write_image(os.path.join(out_dir, '{}_original_noise3.{}'.format(file_name, file_ext)), add_white_noise(resized))
