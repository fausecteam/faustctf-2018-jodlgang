import os
import random

from collections import defaultdict

import imageio
import numpy as np

def tree(): return defaultdict(tree)


class OurDataset(object):
    def __init__(self, directory, seed=None):
        old_np_random_state = np.random.get_state()
        old_random_state = random.getstate()

        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)


        self.dataset_directory = directory
        self.data = tree()

        self.data['dataset_directory'] = directory
        celebrities = set()

        all_train_data_points = []
        all_validation_data_points = []
        for data_type, data_points in [('training', all_train_data_points),
                                       ('validation', all_validation_data_points)]:

            data_type_dir = os.path.join(directory, data_type)

            for category in os.listdir(data_type_dir):
                faces_dir = os.path.join(data_type_dir, category, 'faces')

                for celeb in os.listdir(faces_dir):
                    celebrities.add(celeb)

                    celeb_dir = os.path.join(faces_dir, celeb)
                    images = os.listdir(celeb_dir)

                    data_points.extend([(celeb, os.path.abspath(os.path.join(celeb_dir, img))) for img in images])
                    self.data[data_type][category][celeb] = images

        self.celebrities = list(celebrities)
        self.label_to_celebrity = {}
        self.celebrity_to_label = {}
        for i, c in enumerate(self.celebrities):
            self.label_to_celebrity[i] = c
            self.celebrity_to_label[c] = i

        self.train_data_points_source = all_train_data_points
        self.valid_data_points_source = all_validation_data_points
        mapped_train_data_points = [(self.celebrity_to_label[celeb], img_path) for celeb, img_path in all_train_data_points]
        mapped_validation_data_points = [(self.celebrity_to_label[celeb], img_path) for celeb, img_path in all_validation_data_points]

        self.training_data = np.random.permutation(np.array(mapped_train_data_points, dtype=object))
        self.validation_data = np.random.permutation(np.array(mapped_validation_data_points, dtype=object))

        random.setstate(old_random_state)
        np.random.set_state(old_np_random_state)
