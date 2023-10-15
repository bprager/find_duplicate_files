#!/usr/bin/env python3
import os
import os.path
import hashlib
import logging
import time
import argparse

all_files = {}

logging.basicConfig(
    filename="test.log",
    level=logging.DEBUG,
    format="%(asctime)s.%(msecs)03d %(levelname)s %(name)s - %(funcName)s:%(lineno)d: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def progress_indicator(current, total=None, avrg=None):
    cursor = ["-", "\\", "|", "/"]
    progress_symbol = cursor[current % len(cursor)]

    if total is not None and avrg is not None:
        estimated_time = (total - current) * avrg
        print(
            f"\r{progress_symbol} {current:,}/{total:,} target files checked. Average time for single file: {(estimated_time):6,.2f} sec.",
            end="",
        )
    else:
        print(f"\r{progress_symbol} {current:,} files found.", end="")


def get_or_hash_file(d: dict, file: str) -> str:
    if d.get(file) is None:
        d[file] = hash_file(file)
    return d[file]


def find_duplicates(d: dict) -> None:
    files = list(d.keys())
    total_files = len(files)
    average = 0

    for idx1, file in enumerate(files):
        current_hash = get_or_hash_file(d, file)
        for idx2, target in enumerate(files[idx1 + 1 :]):
            progress_indicator(idx2 + 1, total_files - idx1, average)
            start = time.time()
            target_hash = get_or_hash_file(d, target)
            if current_hash == target_hash:
                logging.info(f"\n{file} is a duplicate of {target}")
            average = (average + time.time() - start) / (idx2 + 1)
    print(
        f"\n{idx1 + 1} file(s) checked. Estimated remaining time for {total_files - idx1} files still to be checked: {(average * (total_files - idx1)  * total_files ) / 60} min."
    )


# Calculates MD5 hash of file
# Returns HEX digest of file
def hash_file(path: str) -> str:
    # Opening file in afile
    afile = open(path, "rb")
    hasher = hashlib.md5()
    blocksize = 65536
    buf = afile.read(blocksize)

    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    afile.close()
    return hasher.hexdigest()


def main():
    parser = argparse.ArgumentParser(description="Find duplicate files.")
    # path
    parser.add_argument("path", help="path to search for duplicates")
    args = parser.parse_args()
    # Get all files in path
    idx = 0
    for dirpath, _, filenames in os.walk(args.path):
        idx = idx + 1
        for filename in filenames:
            progress_indicator(idx + 1)
            path = os.path.join(dirpath, filename)
            if os.path.isfile(path) and os.access(path, os.R_OK):
                all_files[os.path.join(path)] = None
    print(f"number of files: {len(all_files)}")

    # Look for duplicates
    find_duplicates(all_files)


if __name__ == "__main__":
    main()
