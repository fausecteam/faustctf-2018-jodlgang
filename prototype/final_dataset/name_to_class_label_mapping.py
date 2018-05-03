import argparse
import random
import json
import os


def create_class_label_mapping(data_dir, name_to_class_label_mapping_output_file):
    # Find all subdirectories of data_dir
    actors_dir = os.path.join(data_dir, "actors", "faces")
    actresses_dir = os.path.join(data_dir, "actresses", "faces")
    actors = [o for o in os.listdir(actors_dir) if os.path.isdir(os.path.join(actors_dir, o))]
    actresses = [o for o in os.listdir(actresses_dir ) if os.path.isdir(os.path.join(actresses_dir , o))]
    actors_and_actresses = actors + actresses

    # Shuffle classes
    random.seed(91058)
    random.shuffle(actors_and_actresses)

    # List index is the class number
    with open(name_to_class_label_mapping_output_file, "w") as f:
        json.dump(actors_and_actresses, f, indent=4)

    print("Dumped {:d} class labels".format(len(actors_and_actresses)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=str, help="Path to data directory, which contains the subdirectories `actors` and `actresses`")
    parser.add_argument("name_to_class_label_mapping_output_file", type=str, help="Path where to store class label mapping as json list")
    args = vars(parser.parse_args())

    create_class_label_mapping(args["data_dir"], args["name_to_class_label_mapping_output_file"])
