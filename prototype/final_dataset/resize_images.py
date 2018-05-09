import random

import imageio
import os

import shutil

import numpy as np
from jodlgang.image_utils import add_white_noise_ubyte, reflect_image, write_image
from skimage.transform import resize
import argparse



random.seed(0)
np.random.seed(0)


parser = argparse.ArgumentParser()
parser.add_argument('dataset_directory')
parser.add_argument('out_dir')
parser.add_argument('-o', '--output_shape', default='224x224')
args = parser.parse_args()

output_shape = tuple(map(int, args.output_shape.split('x')))

if os.path.abspath(args.out_dir) == os.path.abspath(args.dataset_directory):
    raise ValueError("I really don't think you wanna delete the input directory ... ")
shutil.rmtree(args.out_dir, ignore_errors=True)

for category in os.listdir(args.dataset_directory):
    faces_dir = os.path.join(args.dataset_directory, category, 'faces')

    for celeb in os.listdir(faces_dir):
        print("Processing celebrity {} ... ".format(celeb))
        celeb_dir = os.path.join(faces_dir, celeb)

        images = os.listdir(celeb_dir)

        for i, pic_path in enumerate(images):
            pic_path = os.path.join(celeb_dir, pic_path)

            fname = os.path.basename(pic_path)

            img = imageio.imread(pic_path)

            resized = resize(img, output_shape=output_shape)

            out_dir = os.path.join(args.out_dir, category, 'faces', celeb)

            write_image(os.path.join(out_dir, fname), resized)
