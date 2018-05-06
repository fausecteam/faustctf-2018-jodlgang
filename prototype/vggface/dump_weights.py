from vggface.tf_vggface_v2 import VGGFace
import tensorflow as tf
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint_dir", type=str, help="Directory where to store checkpoint", default="checkpoint")
    parser.add_argument("hdf5_output_file", type=str, help="Where to store weights as HDF5 file")
    parser.add_argument("num_classes", type=int, help="Number of individuals")
    args = vars(parser.parse_args())

    with tf.Session() as sess:
        cnn = VGGFace(sess, args["num_classes"])
        cnn.load(args["checkpoint_dir"])
        cnn.dump_weights_to_hdf5(args["hdf5_output_file"])
