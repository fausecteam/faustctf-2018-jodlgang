import numpy as np
import argparse
import requests
import random
import json
import os


def query_names(number, gender):
    # The received names may contain duplicates. Let's query more than necessary, remove the duplicates, and sample the desired number of identities
    num_queried = int(number * 1.5)
    resp = requests.get("http://uinames.com/api/?amount={}&gender={}&region=germany".format(num_queried, gender))
    random_identities = json.loads(resp.content.decode("utf-8"))
    random_names = [random_identity["name"] + " " + random_identity["surname"] for random_identity in random_identities]
    return random.sample(list(set(random_names)), number)


def create_class_label_mapping(data_dir, name_to_class_label_mapping_output_file):
    # Find all subdirectories of data_dir
    actors_dir = os.path.join(data_dir, "actors", "faces")
    actresses_dir = os.path.join(data_dir, "actresses", "faces")
    actors = [o for o in os.listdir(actors_dir) if os.path.isdir(os.path.join(actors_dir, o))]
    actresses = [o for o in os.listdir(actresses_dir ) if os.path.isdir(os.path.join(actresses_dir, o))]

    # Generate random for actors and actresses
    actor_names = query_names(len(actors), "male")
    actress_names = query_names(len(actresses), "female")

    actors_and_actresses = actors + actresses
    actor_and_actress_names = actor_names + actress_names

    # Shuffle classes
    permutation = list(range(len(actors_and_actresses)))
    random.seed(91058)
    random.shuffle(permutation)

    actors_and_actresses = list(np.array(actors_and_actresses)[permutation])
    actor_and_actress_names = list(np.array(actor_and_actress_names)[permutation])

    # List index is the class number
    with open(name_to_class_label_mapping_output_file, "w") as f:
        json.dump(actors_and_actresses, f, indent=4)

    with open(name_to_class_label_mapping_output_file.replace(".json", "_names.json"), "w") as f:
        json.dump(actor_and_actress_names, f, indent=4)

    print("Dumped {:d} class labels".format(len(actors_and_actresses)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("data_dir", type=str, help="Path to data directory, which contains the subdirectories `actors` and `actresses`")
    parser.add_argument("name_to_class_label_mapping_output_file", type=str, help="Path where to store class label mapping as json list")
    args = vars(parser.parse_args())

    create_class_label_mapping(args["data_dir"], args["name_to_class_label_mapping_output_file"])
