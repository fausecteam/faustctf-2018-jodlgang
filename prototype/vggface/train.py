from vggface.tf_vggface_v2 import VGGFace
import tensorflow as tf
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("training_tfrecords_file", type=str, help="Path to training data")
    parser.add_argument("validation_tfrecords_file", type=str, help="Path to validation data")
    parser.add_argument("num_classes", type=int, help="Number of individuals")
    parser.add_argument("--checkpoint_dir", type=str, help="Directory where to store checkpoint", default="checkpoint")
    parser.add_argument("--summary_dir", type=str, help="Directory where to store summary", default="summary")
    parser.add_argument("--vggface_trained_weights", type=str, help="Restore conv weights from this file is no checkpoint to load is available")
    args = vars(parser.parse_args())

    with tf.Session() as sess:
        cnn = VGGFace(sess, args["num_classes"])
        cnn.train(training_tfrecords_file=args["training_tfrecords_file"],
                  validation_tfrecords_file=args["validation_tfrecords_file"],
                  learning_rate=args["learning_rate"],
                  checkpoint_dir=args["checkpoint_dir"],
                  summary_dir=args["summary_dir"],
                  vggface_trained_weights=args["vggface_trained_weights"])
