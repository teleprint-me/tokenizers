#!/usr/bin/env python
"""
data2txt.py - convert parquet files to plaintext
"""
import os

from pathlib import Path
from datasets import load_dataset
from tqdm import tqdm

import argparse

parser = argparse.ArgumentParser(help="Convert parquet files to plaintext")
parser.add_argument(
    "-d",
    "--dir-path",
    default="data/wikitext-103-raw-v1",
    help="The directory to the dataset",
)
args = parser.parse_args()

path = Path(args.dir_path)
if not path.is_dir():
    raise FileNotFoundError(f"{path} does not exist!")

# Load the dataset
dataset = load_dataset(str(path))

# Convert parquet files into plaintext files
for index, subset in enumerate(dataset.items()):
    name, rows = subset
    print(f"Converting subset {name} to plaintext")

    # Concatenate all text features for a given subset
    text = ""
    for row in tqdm(rows, total=len(rows)):
        text += "\n".join(f"{row['text'].strip().split('\n')}")

    # Write the concatenated text to a plaintext file
    output_file_path = f"{path}/{name}-{index:05}-of-{len(dataset.keys()):05}.txt"

    print(f"Writing {output_file_path}")

    try:
        with open(output_file_path, "w") as f:
            f.write(text)
    except (OSError, IOError) as e:
        print(f"Error while writing to file '{output_file_path}': {e}")

raw_files = [ent for ent in os.scandir(str(path)) if Path(ent.path).suffix == ".txt"]
print(raw_files)
