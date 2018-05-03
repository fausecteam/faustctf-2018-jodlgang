from scipy.misc import imread
import tensorflow as tf
import argparse
import random
import json
import os
import re


def collect(data_dir, name_to_class_label_mapping_file, output_file):
    assert os.path.exists(data_dir), "Given data dir does not exist"
    assert os.path.exists(name_to_class_label_mapping_file), "Class label mapping file does not exist"

    with open(name_to_class_label_mapping_file, "r") as f:
        directory_names = json.load(f)

    # Create look up table for class labels
    name_to_class_label_mapping = {directory_name: i for i, directory_name in enumerate(directory_names)}

    # Recursively find all jpg, jpeg, and png files in data directory
    img_files = [os.path.join(dp, f) for dp, dn, filenames in os.walk(data_dir) for f in filenames if re.search(".(jpg|jpeg|png)$", f.lower()) is not None]
    num_images = len(img_files)
    random.shuffle(img_files)

    # Open TFRecords file
    writer = tf.python_io.TFRecordWriter(output_file)

    for i in range(num_images):
        if i % 1000 == 0:
            print("Progress: {:d}/{:d}".format(i + 1, num_images))

        img_file = img_files[i]
        img = imread(img_file)
        label = name_to_class_label_mapping[os.path.basename(os.path.dirname(img_file))]

        # Create a feature
        feature = {"train/label": tf.train.Feature(int64_list=tf.train.Int64List(value=[label])),
                   "train/image": tf.train.Feature(bytes_list=tf.train.BytesList(value=[tf.compat.as_bytes(img.tostring())]))}

        # Create an example protocol buffer
        example = tf.train.Example(features=tf.train.Features(feature=feature))

        # Serialize to string and write on the file
        writer.write(example.SerializeToString())

    writer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=str, help="Path to data root directory")
    parser.add_argument("name_to_class_label_mapping_output_file", type=str, help="Json file containing list of actor/actress folder names")
    parser.add_argument("output_file", type=str, help="Path to output file")
    args = vars(parser.parse_args())

    collect(args["data_dir"], args["name_to_class_label_mapping_output_file"], args["output_file"])
