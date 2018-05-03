import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import argparse
import json
import os


def display(tfrecords_filename, name_to_class_label_mapping_file):
    assert os.path.exists(tfrecords_filename), "tfrecords file does not exist"

    # num_examples = 0
    # for record in tf.python_io.tf_record_iterator(tfrecords_filename):
    #     num_examples += 1
    # print("Number of examples: {:d}".format(num_examples))

    with open(name_to_class_label_mapping_file, "r") as f:
        directory_names = json.load(f)

    # Create look up table for class labels
    class_label_to_name_mapping = {i: directory_name for i, directory_name in enumerate(directory_names)}

    feature = {"train/image": tf.FixedLenFeature([], tf.string),
               "train/label": tf.FixedLenFeature([], tf.int64)}

    # Create list of file names and pass it to a queue
    # As long as we don't provide the num_epochs argument, this will cycle through the input infinitely many times
    filename_queue = tf.train.string_input_producer([tfrecords_filename])

    # Define a reader and read the next record
    reader = tf.TFRecordReader()
    _, serialized_example = reader.read(filename_queue)

    # Decode the record read by the reader
    features = tf.parse_single_example(serialized_example, features=feature)

    # Convert the image data from string back to numbers
    image = tf.decode_raw(features["train/image"], tf.uint8)
    # Reshape image data into the original shape
    image = tf.reshape(image, [224, 224, 3])

    # Cast label data into int32
    label = tf.cast(features["train/label"], tf.int32)

    # Any preprocessing here...

    # Create batches by randomly shuffling tensors
    images, labels = tf.train.shuffle_batch([image, label], batch_size=6, capacity=30, num_threads=1, min_after_dequeue=6)

    # Initialize all global and local variables
    init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())

    with tf.Session() as sess:
        sess.run(init_op)

        # Create a coordinator and run all QueueRunner objects
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)
        for batch_idx in range(5):
            image_batch, label_batch = sess.run([images, labels])
            image_batch = image_batch.astype(np.uint8)
            for j in range(6):
                plt.subplot(2, 3, j + 1)
                plt.imshow(image_batch[j, ...])
                plt.title(class_label_to_name_mapping[label_batch[j]])
            plt.show()

        # Stop the threads
        coord.request_stop()

        # Wait for threads to stop
        coord.join(threads)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="Path to tfrecords file of data set to display")
    parser.add_argument("name_to_class_label_mapping_output_file", type=str, help="Json file containing list of actor/actress folder names")
    args = vars(parser.parse_args())

    display(args["input_file"], args["name_to_class_label_mapping_output_file"])
