import tensorflow as tf
import numpy as np
import h5py
from vggface.ops import conv2d_relu, max_pool_2x2, weights_variable_truncated_normal, bias_variable
from scipy.misc import imread
import os


class VGGFace(object):
    def __init__(self, sess, num_classes, auto_setup_model=True):
        self._sess = sess
        self._images = tf.placeholder(tf.float32, [None, 224, 224, 3], name="images")
        self._drop_rate = tf.placeholder(tf.float32, name="drop_rate")

        if auto_setup_model:
            self._output, self._output_logits = self.model(self._images, self._drop_rate, num_classes)

    @staticmethod
    def model(input, drop_rate, num_classes):
        # Preprocessing:
        # Convert RGB to BGR
        bgr_input = tf.reverse(input, axis=[-1])

        # Subtract channel-wise mean
        b, g, r = tf.split(bgr_input, num_or_size_splits=3, axis=3)
        b_sub = tf.subtract(b, 93.5940)
        g_sub = tf.subtract(g, 104.7624)
        r_sub = tf.subtract(r, 129.1863)
        concat = tf.concat([b_sub, g_sub, r_sub], axis=3)

        # Block 1
        # (224, 224, 3) -> (112, 112, 64)
        conv1_1 = conv2d_relu(concat, 64, "conv1_1")
        conv1_2 = conv2d_relu(conv1_1, 64, "conv1_2")
        pool1 = max_pool_2x2(conv1_2)

        # Block 2
        # (112, 112, 64) -> (56, 56, 128)
        conv2_1 = conv2d_relu(pool1, 128, "conv2_1")
        conv2_2 = conv2d_relu(conv2_1, 128, "conv2_2")
        pool2 = max_pool_2x2(conv2_2)

        # Block 3
        # (56, 56, 128) -> (28, 28, 256)
        conv3_1 = conv2d_relu(pool2, 256, "conv3_1")
        conv3_2 = conv2d_relu(conv3_1, 256, "conv3_2")
        conv3_3 = conv2d_relu(conv3_2, 256, "conv3_3")
        pool3 = max_pool_2x2(conv3_3)

        # Block 4
        # (28, 28, 256) -> (14, 14, 512)
        conv4_1 = conv2d_relu(pool3, 512, "conv4_1")
        conv4_2 = conv2d_relu(conv4_1, 512, "conv4_2")
        conv4_3 = conv2d_relu(conv4_2, 512, "conv4_3")
        pool4 = max_pool_2x2(conv4_3)

        # Block 5
        # (14, 14, 512) -> (7, 7, 512)
        conv5_1 = conv2d_relu(pool4, 512, "conv5_1")
        conv5_2 = conv2d_relu(conv5_1, 512, "conv5_2")
        conv5_3 = conv2d_relu(conv5_2, 512, "conv5_3")
        pool5 = max_pool_2x2(conv5_3)

        flatten = tf.reshape(pool5, [-1, 7 * 7 * 512])

        with tf.variable_scope("fc6"):
            fc6_weights = weights_variable_truncated_normal([7 * 7 * 512, 4096], mean=0, stddev=1e-2, name="fc6_weights")
            fc6_bias = bias_variable([4096], value=0, name="fc6_bias")
            fc6_z = tf.matmul(flatten, fc6_weights) + fc6_bias
            fc6_a = tf.nn.relu(fc6_z)
            fc6_dropout = tf.layers.dropout(fc6_a, rate=drop_rate)

        with tf.variable_scope("fc7"):
            fc7_weights = weights_variable_truncated_normal([4096, 4096], mean=0, stddev=1e-2, name="fc7_weights")
            fc7_bias = bias_variable([4096], value=0, name="fc7_bias")
            fc7_z = tf.matmul(fc6_dropout, fc7_weights) + fc7_bias
            fc7_a = tf.nn.relu(fc7_z)
            fc7_dropout = tf.layers.dropout(fc7_a, rate=drop_rate)

        with tf.variable_scope("fc8"):
            fc8_weights = weights_variable_truncated_normal([4096, num_classes], mean=0, stddev=1e-2, name="fc8_weights")
            fc8_bias = bias_variable([num_classes], value=0, name="fc8_bias")
            fc8_z = tf.matmul(fc7_dropout, fc8_weights) + fc8_bias
            fc8_a = tf.nn.softmax(fc8_z)

        return fc8_a, fc8_z

    @staticmethod
    def restore_vggface_conv_weights(sess, weights_file):
        sess.run(tf.global_variables_initializer())

        with h5py.File(weights_file, "r") as f:
            layers = list(f.keys())
            for layer in layers:
                layer_layers = list(f[layer].keys())
                # Don't consider empty weights like for pooling or flatten operations
                if len(layer_layers) == 0:
                    continue

                layer_parameters = list(f[layer][layer_layers[0]].keys())
                for layer_parameter in layer_parameters:
                    trained_value = f[layer][layer_layers[0]][layer_parameter].value

                    parameter_name = layer_parameter
                    if parameter_name == "bias:0":
                        parameter_name = "bias"
                    elif parameter_name == "kernel:0":
                        parameter_name = "weights"

                    with tf.variable_scope(layer, reuse=True):
                        tf_variable = tf.get_variable("{}_{}".format(layer, parameter_name))
                        sess.run(tf.assign(tf_variable, trained_value))

    def inference(self, imgs):
        predictions = self._sess.run(self._output, feed_dict={self._images: imgs, self._drop_rate: 0})
        return predictions

    @staticmethod
    def preprocess(imgs):
        preprocessed_imgs = np.copy(imgs).astype(np.float)
        preprocessed_imgs = preprocessed_imgs[..., ::-1]
        preprocessed_imgs[..., 0] -= 93.5940
        preprocessed_imgs[..., 1] -= 104.7624
        preprocessed_imgs[..., 2] -= 129.1863
        return preprocessed_imgs

    @staticmethod
    def undo_preprocessing(imgs):
        original_imgs = np.copy(imgs)
        original_imgs[..., 0] += 93.5940
        original_imgs[..., 1] += 104.7624
        original_imgs[..., 2] += 129.1863
        original_imgs = original_imgs[..., ::-1]
        return original_imgs

    def finetune(self, training_tfrecords_file, validation_tfrecords_file, summary_dir):
        assert os.path.exists(training_tfrecords_file), "training set file does not exist"
        assert os.path.exists(validation_tfrecords_file), "validation set file does not exist"

        #
        # Set up input data queues
        #
        feature = {"train/image": tf.FixedLenFeature([], tf.string),
                   "train/label": tf.FixedLenFeature([], tf.int64)}

        # Create list of file names and pass it to a queue
        # As long as we don't provide the num_epochs argument, this will cycle through the input infinitely many times
        filename_queue = tf.train.string_input_producer([training_tfrecords_file])

        # Define a reader and read the next record
        reader = tf.TFRecordReader()
        _, serialized_example = reader.read(filename_queue)

        # Decode the record read by the reader
        features = tf.parse_single_example(serialized_example, features=feature)

        # Convert the image data from string back to numbers
        image = tf.decode_raw(features["train/image"], tf.uint8)
        # Reshape image data into the original shape
        image = tf.cast(tf.reshape(image, [224, 224, 3]), tf.float32)

        # Cast label data into int32
        label = tf.cast(features["train/label"], tf.int32)

        # Create batches by randomly shuffling tensors
        images, labels = tf.train.shuffle_batch([image, label], batch_size=64, capacity=512, num_threads=4, min_after_dequeue=128)

        #
        # Set up optimization
        #
        labels = tf.placeholder(tf.float32, [None,])

        with tf.name_scope("loss"):
            loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels=labels, logits=self._output_logits))

        with tf.name_scope("optimizer"):
            global_step = tf.Variable(0, name="global_step", trainable=False)
            optimizer = tf.train.AdamOptimizer(learning_rate=0.001)
            train_op = optimizer.minimize(loss, global_step=global_step)

        # Summary
        loss_summary = tf.summary.scalar("loss", loss)
        training_summary_writer = tf.summary.FileWriter(summary_dir, graph=self._sess.graph)

        # Initialize all global and local variables
        init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())

        self._sess.run(init_op)

        # Create a coordinator and run all QueueRunner objects
        coord = tf.train.Coordinator()
        threads = tf.train.start_queue_runners(coord=coord)

        patience = 50
        num_steps_to_eval_validation_set = 100

        try:
            while patience > 0:
                image_batch, label_batch = self._sess.run([images, labels])

                _, loss_val, global_step_val = self._sess.run([train_op, loss, global_step],
                                                              feed_dict={self._images: image_batch,
                                                                         labels: label_batch,
                                                                         self._drop_rate: 0.5})

                if global_step_val % num_steps_to_eval_validation_set == 0:
                    # TODO Eval

        finally:
            # Stop the threads
            coord.request_stop()

            # Wait for threads to stop
            coord.join(threads)
