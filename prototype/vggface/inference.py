from vggface.tf_vggface_v2 import VGGFace
import tensorflow as tf
from scipy.misc import imread
import numpy as np
from keras_vggface.utils import decode_predictions


if __name__ == "__main__":
    weights_file = "/home/explicat/.keras/models/vggface/rcmalli_vggface_tf_vgg16.h5"
    with tf.Session() as sess:
        cnn = VGGFace(sess, 2622)
        cnn.restore_vggface_conv_weights(sess, weights_file)

        img_filename = "../keras-vggface/image/ajb.jpg"
        img = imread(img_filename).astype(np.float)

        predictions = cnn.inference(img[None, :])
        print(decode_predictions(predictions))
