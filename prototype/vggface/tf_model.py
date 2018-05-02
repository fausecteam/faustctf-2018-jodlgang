import tensorflow as tf
import numpy as np
import h5py
from vggface.ops import conv2d_relu, max_pool_2x2, weights_variable_truncated_normal, bias_variable
from scipy.misc import imread
from keras_vggface.utils import decode_predictions


class VGGFace(object):
    def __init__(self, sess, auto_setup_model=True):
        self._sess = sess
        self._images = tf.placeholder(tf.float32, [None, 224, 224, 3], name="images")
        self._drop_rate = tf.placeholder(tf.float32, name="drop_rate")

        if auto_setup_model:
            self._output, self._output_logits = self.model(self._images, self._drop_rate)

    @staticmethod
    def model(input, drop_rate):
        # Block 1
        # (224, 224, 3) -> (112, 112, 64)
        conv1_1 = conv2d_relu(input, 64, "conv1_1")
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
            fc8_weights = weights_variable_truncated_normal([4096, 2622], mean=0, stddev=1e-2, name="fc8_weights")
            fc8_bias = bias_variable([2622], value=0, name="fc8_bias")
            fc8_z = tf.matmul(fc7_dropout, fc8_weights) + fc8_bias
            fc8_a = tf.nn.softmax(fc8_z)

        return fc8_a, fc8_z

    @staticmethod
    def load(sess, weights_file):
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
        preprocessed_imgs = self.preprocess(imgs)

        predictions = self._sess.run(self._output, feed_dict={self._images: preprocessed_imgs, self._drop_rate: 0})
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


if __name__ == "__main__":
    weights_file = "/home/explicat/.keras/models/vggface/rcmalli_vggface_tf_vgg16.h5"
    with tf.Session() as sess:
        cnn = VGGFace(sess)
        cnn.load(sess, weights_file)

        img_filename = "../keras-vggface/image/ajb.jpg"
        img = imread(img_filename).astype(np.float)
        # img = tf.keras.preprocessing.image.load_img("../keras-vggface/image/ajb.jpg", target_size=(224, 224))
        # x = tf.keras.preprocessing.image.img_to_array(img)

        predictions = cnn.inference(img[None, :])
        print(decode_predictions(predictions))
