import argparse
import json
import re
import os
import shutil
from collections import defaultdict

import numpy as np
from PIL import Image
from skimage import img_as_ubyte
from skimage.transform import resize
from jodlgang.data_utils.celeb_labels import get_celeb_labels, get_new_name_labels
from jodlgang.data_utils.dataset import CelebDataset
from jodlgang.image_utils import add_white_noise, write_image
from jodlgang.tensorwow import get_face_recognition_cnn


def get_original_img_name(n):
    dots = n.split('.')
    fname, extension = '.'.join(dots[:-1]), dots[-1]

    split_underscore = fname.split('_')
    orig_name, reflected, noise = '_'.join(split_underscore[:-2]), split_underscore[-2], split_underscore[-1]
    assert reflected in {'original', 'reflected'}
    assert re.fullmatch('noise[0-9]+', noise)

    return orig_name + '.' + extension


def get_face_recognition_rate(cnn, target_class, face, num_checks_to_pass=4, num_checks_to_run=5):
    num_checks_passed = 0
    for i in range(num_checks_to_run):
        if num_checks_passed >= num_checks_to_pass:
            break

        noisy = add_white_noise(face)
        noisy_ubyte = img_as_ubyte(noisy).astype(np.float)
        class_probabilities = cnn.inference(noisy_ubyte[None, :])[0]
        predicted_class = np.argmax(class_probabilities)
        if predicted_class == target_class:
            num_checks_passed += 1

    return num_checks_passed >= num_checks_to_pass, num_checks_passed

NOISY_DIR = '/media/honululu/Data/facescrub_final_directory/'
NOISELESS_DIR = '/media/honululu/Data/facescrub_resized/'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('weights_file')
    parser.add_argument('checker_dataset_out_dir')
    parser.add_argument('--num-checks-to-run', default=1)
    parser.add_argument('--num-checks-to-pass', default=1)
    args = parser.parse_args()

    assert args.num_checks_to_pass <= args.num_checks_to_run, "The number of checks to pass can't exceed the number of checks to run."

    celebs = get_celeb_labels()
    celeb_to_class_label = {celeb: i for i, celeb in enumerate(celebs)}
    names = get_new_name_labels()

    cnn = get_face_recognition_cnn(args.weights_file)

    print ("Loading noisy dataset ... ")
    dataset_noisy = CelebDataset(NOISY_DIR)

    print("Locating noisefree images ... ")
    original_images = defaultdict(set)
    for d in {'training', 'validation'}:
        for type in {'actors', 'actresses'}:
            for celeb, pic_names in dataset_noisy.data[d][type].items():
                for pic_name in pic_names:
                    original_pic_name = get_original_img_name(pic_name)
                    original_pic = NOISELESS_DIR + '{t}/faces/{c}/{n}'.format(t=type, c=celeb, n=original_pic_name)
                    assert os.path.isfile(original_pic), "Could not find image {}".format(original_pic)
                    original_images[celeb].add(original_pic)

    import ipdb; ipdb.set_trace()
    print("Checking recognition rates of dataset images ... ")
    face_recognition = {}
    for celeb, images in original_images.items():
        print ("Checking images for {} ...".format(celeb))
        face_recognition[celeb] = list()
        for img in images:
            face = np.array(Image.open(img))
            passed, num_recognized = get_face_recognition_rate(cnn,
                                                       celeb_to_class_label[celeb],
                                                       face,
                                                       num_checks_to_pass=args.num_checks_to_pass,
                                                       num_checks_to_run=args.num_checks_to_run)
            print("... {}: Passed {}, {}/{}".format(img, passed, num_recognized, args.num_checks_to_run))
            if passed:
                out_path = os.path.join(args.checker_dataset_out_dir, celeb, os.path.basename(img))
                write_image(out_path, face)


            face_recognition[celeb].append(dict(img=img, success=num_recognized, total=args.num_checks_to_run, passed=passed))


    print(face_recognition)
    #for i in range(len(celebs)):
    #    if os.path.exists()
    #    for f in available_faces(f):

