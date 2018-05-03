import matplotlib.pyplot as plt
import tensorflow as tf
import argparse


def _parse_function(proto):
    features = {
        "image": tf.FixedLenFeature([], tf.string),
        "label": tf.FixedLenFeature([], tf.int64)
    }

    parsed_features = tf.parse_single_example(proto, features)

    image_buffer = parsed_features["image"]
    label = tf.cast(parsed_features["label"], tf.int32)

    with tf.name_scope("decode_jpeg", [image_buffer], None):
        image = tf.image.decode_jpeg(image_buffer, channels=3)
        image = tf.image.convert_image_dtype(image, dtype=tf.float32)

    image = tf.reshape(image, [224, 224, 3])

    return image, label


def load_dataset(training_tfrecords_file, validation_tfrecords_file):
    # Training dataset
    train_dataset = tf.data.TFRecordDataset([training_tfrecords_file])
    # Parse the record into tensors
    train_dataset = train_dataset.map(_parse_function, num_parallel_calls=4)
    # Infinitely many iterations
    train_dataset = train_dataset.repeat(None)
    train_dataset = train_dataset.shuffle(buffer_size=1000)
    train_dataset = train_dataset.prefetch(buffer_size=1000)
    train_dataset = train_dataset.batch(6)

    # Validation dataset
    validation_dataset = tf.data.TFRecordDataset([validation_tfrecords_file])
    validation_dataset = validation_dataset.map(_parse_function, num_parallel_calls=4)
    validation_dataset = validation_dataset.prefetch(buffer_size=100)
    validation_dataset = validation_dataset.batch(6)

    handle = tf.placeholder(tf.string, shape=[])
    iterator = tf.contrib.data.Iterator.from_string_handle(handle, train_dataset.output_types, train_dataset.output_shapes)
    next_element = iterator.get_next()

    training_iterator = train_dataset.make_initializable_iterator()
    validation_iterator = validation_dataset.make_initializable_iterator()

    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        training_handle = sess.run(training_iterator.string_handle())
        validation_handle = sess.run(validation_iterator.string_handle())

        # Compute for 10 epochs.
        for _ in range(10):
            sess.run(training_iterator.initializer)
            while True:
                try:
                    image_batch, label_batch = sess.run(next_element, feed_dict={handle: training_handle})

                    for j in range(6):
                        plt.subplot(2, 3, j + 1)
                        plt.imshow(image_batch[j, ...])
                        plt.title(label_batch[j])
                    plt.show()

                    # sess.run(train_step, feed_dict={x: img, y_: lbl})
                except tf.errors.OutOfRangeError:
                    img, lbl = sess.run(next_element, feed_dict={handle: validation_handle})
                    # print sess.run(accuracy, feed_dict={x: img, y_: lbl})
                    break


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("training_tfrecords_file", type=str, help="Path to tfrecords file of data set to display")
    parser.add_argument("validation_tfrecords_file", type=str, help="Path to tfrecords file of data set to display")
    args = vars(parser.parse_args())

    load_dataset(args["training_tfrecords_file"], args["validation_tfrecords_file"])
