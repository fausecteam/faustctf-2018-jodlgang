from vggface.ops import conv2d_relu, max_pool_2x2, weights_variable_truncated_normal, bias_variable
import tensorflow as tf
import numpy as np
import time
import h5py
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
        with h5py.File(weights_file, "r") as f:
            layers = list(f.keys())
            for layer in layers:
                # Only consider convolutional layers
                if not layer.startswith("conv"):
                    continue

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
        return True

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

    def load(self, checkpoint_dir, saver):
        print("Attempting to read checkpoint from {}".format(checkpoint_dir))

        checkpoint = tf.train.get_checkpoint_state(checkpoint_dir)
        if checkpoint and checkpoint.model_checkpoint_path:
            saver.restore(self._sess, checkpoint.model_checkpoint_path)
            print("Successfully restored checkpoint")
            return True

        print("Failed to restore checkpoint")
        return False

    def store(self, checkpoint_dir, saver, step):
        if not os.path.exists(checkpoint_dir):
            os.makedirs(checkpoint_dir)

        path = saver.save(self._sess, os.path.join(checkpoint_dir, os.path.basename(__file__)), global_step=step)
        print("Stored model at step {}".format(step))
        return path

    @staticmethod
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

    def train(self, training_tfrecords_file, validation_tfrecords_file, learning_rate, checkpoint_dir, summary_dir, vggface_trained_weights=None):
        assert os.path.exists(training_tfrecords_file), "training set file does not exist"
        assert os.path.exists(validation_tfrecords_file), "validation set file does not exist"

        # Some constants
        initial_patience = 50
        num_steps_to_check_validation_set = 1000
        num_steps_to_check_loss = 100

        # Set up dataset handling
        # Training dataset
        train_dataset = tf.data.TFRecordDataset([training_tfrecords_file])
        # Parse the record into tensors
        train_dataset = train_dataset.map(self._parse_function, num_parallel_calls=4)
        # Infinitely many iterations
        train_dataset = train_dataset.repeat(None)
        train_dataset = train_dataset.shuffle(buffer_size=1000)
        train_dataset = train_dataset.prefetch(buffer_size=1000)
        train_dataset = train_dataset.batch(32)

        # Validation dataset
        validation_dataset = tf.data.TFRecordDataset([validation_tfrecords_file])
        validation_dataset = validation_dataset.map(self._parse_function, num_parallel_calls=4)
        validation_dataset = validation_dataset.prefetch(buffer_size=100)
        validation_dataset = validation_dataset.batch(32)

        handle = tf.placeholder(tf.string, shape=[])
        iterator = tf.contrib.data.Iterator.from_string_handle(handle, train_dataset.output_types,
                                                               train_dataset.output_shapes)
        next_element = iterator.get_next()

        training_iterator = train_dataset.make_initializable_iterator()
        validation_iterator = validation_dataset.make_initializable_iterator()

        # Set up loss and optimization
        labels = tf.placeholder(tf.int64, [None,])

        with tf.name_scope("accuracy"):
            accuracy = tf.cast(tf.equal(tf.argmax(self._output, axis=1), labels), tf.float32)

        with tf.name_scope("loss"):
            loss = tf.reduce_mean(tf.nn.sparse_softmax_cross_entropy_with_logits(labels=labels, logits=self._output_logits))

        with tf.name_scope("optimizer"):
            global_step = tf.Variable(0, name="global_step", trainable=False)
            optimizer = tf.train.AdamOptimizer(learning_rate)
            train_op = optimizer.minimize(loss, global_step=global_step)

        # Checkpoint saver
        saver = tf.train.Saver(max_to_keep=1, save_relative_paths=True)

        # Summary
        loss_summary = tf.summary.scalar("loss", loss)
        accuracy_summary = tf.summary.scalar("accuracy", tf.reduce_mean(accuracy))
        summary_op = tf.summary.merge([loss_summary, accuracy_summary])

        # Prepare paths for summaries
        summary_dir_name = time.strftime("%Y_%m_%d_%H_%M_%S") + "-" + os.path.basename(__file__)
        training_summary_dir = os.path.join(summary_dir, summary_dir_name, "training")
        validation_summary_dir = os.path.join(summary_dir, summary_dir_name, "validation")
        # Create two different summary writers to give statistics on training and validation images
        training_summary_writer = tf.summary.FileWriter(training_summary_dir, graph=self._sess.graph)
        # Set up evaluation summary writer without graph to avoid overlap with training graph
        validation_summary_writer = tf.summary.FileWriter(validation_summary_dir)

        patience = initial_patience
        best_validation_accuracy = 0

        self._sess.run(tf.global_variables_initializer())

        # Attempt to restore checkpoint
        if self.load(checkpoint_dir, saver):
            print("Restored trained model")
        elif vggface_trained_weights and self.restore_vggface_conv_weights(self._sess, vggface_trained_weights):
            print("Restored VGGFace weights")
        else:
            print("Creating a new model")

        training_handle = self._sess.run(training_iterator.string_handle())
        validation_handle = self._sess.run(validation_iterator.string_handle())
        self._sess.run(training_iterator.initializer)

        while patience > 0:
            # Fetch batch
            image_batch, label_batch = self._sess.run(next_element, feed_dict={handle: training_handle})
            feed_dict = {self._images: image_batch, labels: label_batch, self._drop_rate: 0.5}
            _, loss_val, global_step_val = self._sess.run([train_op, loss, global_step], feed_dict=feed_dict)

            if global_step_val % num_steps_to_check_loss == 0:
                print("Step: {:d}, Loss: {:3.2f}, Patience: {:d}".format(global_step_val, loss_val, patience))
                feed_dict = {self._images: image_batch, labels: label_batch, self._drop_rate: 0}
                summary_val = self._sess.run(summary_op, feed_dict=feed_dict)
                # Write summary
                training_summary_writer.add_summary(summary_val, global_step=global_step_val)

            if global_step_val % num_steps_to_check_validation_set == 0:
                accuracy_batches = []
                self._sess.run(validation_iterator.initializer)
                validation_set_exhausted = False
                while not validation_set_exhausted:
                    try:
                        image_batch, label_batch = self._sess.run(next_element, feed_dict={handle: validation_handle})
                        accuracy_batch = self._sess.run(accuracy, feed_dict={self._images: image_batch, labels: label_batch, self._drop_rate: 0})
                        accuracy_batches.append(accuracy_batch)
                    except tf.errors.OutOfRangeError:
                        validation_set_exhausted = True

                # Average accuracies
                average_accuracy = np.mean(np.concatenate(accuracy_batches))

                summary = tf.Summary()
                summary.value.add(tag="accuracy", simple_value=average_accuracy)
                validation_summary_writer.add_summary(summary, global_step=global_step_val)

                if average_accuracy > best_validation_accuracy:
                    self.store(global_step_val)
                    patience = initial_patience
                    best_validation_accuracy = average_accuracy
