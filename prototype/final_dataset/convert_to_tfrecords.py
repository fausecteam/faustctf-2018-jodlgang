import tensorflow as tf
import argparse
import random
import json
import os
import re


def _int64_feature(value):
    """Wrapper for inserting int64 features into Example proto."""
    if not isinstance(value, list):
        value = [value]
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


def _bytes_feature(value):
    """
    Wrapper for inserting bytes features into Example proto.
    """
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def _convert_to_example(image_buffer, label):
    """
    Build an Example proto for an example.
    """

    example = tf.train.Example(features=tf.train.Features(feature={
        'label': _int64_feature(label),
        'image': _bytes_feature(tf.compat.as_bytes(image_buffer))}))
    return example


class ImageCoder(object):
    """Helper class that provides TensorFlow image coding utilities."""

    def __init__(self):
        # Create a single Session to run all image coding calls.
        self._sess = tf.Session()

        # Initializes function that converts PNG to JPEG data.
        self._png_data = tf.placeholder(dtype=tf.string)
        image = tf.image.decode_png(self._png_data, channels=3)
        self._png_to_jpeg = tf.image.encode_jpeg(image, format="rgb", quality=100)

        # Initializes function that decodes RGB JPEG data.
        self._decode_jpeg_data = tf.placeholder(dtype=tf.string)
        self._decode_jpeg = tf.image.decode_jpeg(self._decode_jpeg_data, channels=3)

    def png_to_jpeg(self, image_data):
        return self._sess.run(self._png_to_jpeg, feed_dict={self._png_data: image_data})

    def decode_jpeg(self, image_data):
        image = self._sess.run(self._decode_jpeg, feed_dict={self._decode_jpeg_data: image_data})
        assert len(image.shape) == 3
        assert image.shape[2] == 3
        return image


def _is_png(filename):
    """Determine if a file contains a PNG format image.

    Args:
      filename: string, path of the image file.

    Returns:
      boolean indicating if the image is a PNG.
    """
    return filename.endswith('.png')


def _process_image(filename, coder):
    """Process a single image file.

    Args:
      filename: string, path to an image file e.g., '/path/to/example.JPG'.
      coder: instance of ImageCoder to provide TensorFlow image coding utils.
    Returns:
      image_buffer: string, JPEG encoding of RGB image.
      height: integer, image height in pixels.
      width: integer, image width in pixels.
    """
    # Read the image file.
    with tf.gfile.FastGFile(filename, 'rb') as f:
        image_data = f.read()

    # Convert any PNG to JPEG's for consistency.
    if _is_png(filename):
        print('Converting PNG to JPEG for %s' % filename)
        image_data = coder.png_to_jpeg(image_data)

    # Decode the RGB JPEG.
    image = coder.decode_jpeg(image_data)

    # Check that image converted to RGB
    assert len(image.shape) == 3
    assert image.shape[2] == 3

    return image_data


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
    coder = ImageCoder()

    for i in range(num_images):
        if i % 1000 == 0:
            print("Progress: {:d}/{:d}".format(i + 1, num_images))

        img_file = img_files[i]
        label = name_to_class_label_mapping[os.path.basename(os.path.dirname(img_file))]
        image_buffer = _process_image(img_file, coder)

        # Create an example protocol buffer
        example = _convert_to_example(image_buffer, label)

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
