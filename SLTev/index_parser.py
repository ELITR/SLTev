import os
import sys
import glob
import re
import json
import argparse

"""
Read an index file with meta-annotations (SRC, REF, ALIGNMENT...)

Meta-annotation format:
# NAME -> *.<EXTENSION>

Return an iterable of dicts containing paths to the specified files
If invoked on the command line, return a JSON of the list of dicts
Multiple directories can share the same meta-annotations, as long as there isn't a blank line between them
SRC line resets the meta-annotations 
SRC and REF are mandatory annotations

Example:

# SRC -> *.<EXTENSION>
# REF -> *.<EXTENSION>
PATH_TO_DIRECTORY
PATH_TO_ANOTHER_DIRECTORY_WITH_SAME_PREFIXES

# SRC -> *.<EXTENSION>
# REF -> *.<EXTENSION>
PATH_TO_DIRECTORY_WITH_DIFFERENT_PREFIXES
"""


def parseIndexFile(indexFilePath, testsetPath):
    fileExtensions = {} # Dict of file extensions
    with open(indexFilePath) as indexFile:
        for line in indexFile:
            line = line.rstrip()
            if line.startswith("#"):
                if "->" in line:
                    _, fileType, _, extension = line.split(" ")
                    if not extension.startswith("*"):
                        raise Exception(f"{line} -- extension must start with a *")
                    if fileType == "SRC":
                        fileExtensions = {}
                    fileExtensions[fileType] = extension 
            elif len(line) > 0:
                if "SRC" not in fileExtensions or "REF" not in fileExtensions:
                    raise Exception(f"{line} -- SRC or REF not specified") 

                evalEntry = {}
                for name, extension in fileExtensions.items():
                    files = glob.glob(f"{testsetPath}/{line}/{extension}")
                    matchingFiles = [file for file in files if file.endswith(extension[1:])]
                    if len(matchingFiles) == 0:
                        raise Exception(f"{name} {extension} does not have a matching file in directory {line}")
                    if len(matchingFiles) > 1:
                        raise Exception(f"{name} {extension} has more than one matching files in directory {line}: {matchingFiles}")
                    evalEntry[name] = os.path.realpath(matchingFiles[0])
                    yield evalEntry

def main():
    parser = argparse.ArgumentParser(
        description="Interpret index files of elitr-testset (https://github.com/ELITR/elitr-testset/tree/master/indices) and print them as simple file lists."
    )
    parser.add_argument("indexfile_path",
      help = "path to the index file",
      type = str,
    )
    parser.add_argument("dataset_path",
      help = "path to your clone of dataset",
      type = str,
    )
    args = parser.parse_args()

    paths = [path for path in parseIndexFile(args.indexfile_path, args.dataset_path)]
    print(json.dumps(paths))

if __name__ == "__main__":
    main()
