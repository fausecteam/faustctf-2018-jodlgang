import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("partitions", type=int)
parser.add_argument('name_json')
args = parser.parse_args()

m = args.partitions
with open(args.name_json) as f:
    names = json.load(f)

    split = [[] for i in range(m)]
    for i, n in enumerate(names):
        split[i % m].append(n)

for ns in split:
    print(' '.join([json.dumps(n) if ('"' in n or "'" in n) else n for n in ns]))
    print()
