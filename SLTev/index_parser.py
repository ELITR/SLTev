import os
import sys
import glob
import re
import json

"""
Read an index file with meta-annotations (SRC, REF, ALIGNMENT...)

Meta-annotation format:
# NAME -> *.<EXTENSION>

Return an iterable of dicts containing paths to the specified files
If invoked on the command line, return a JSON of the list of dicts
Multiple directories can share the same meta-annotations, as long as there isn't a blank line between them
Blank line resets the meta-annotations 
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
                    fileExtensions[fileType] = extension 
            elif len(line) == 0:
                fileExtensions = {} 
            else:
                if "SRC" not in fileExtensions or "REF" not in fileExtensions:
                    raise Exception(f"{line} -- SRC or REF not specified") 
                sourceExtension = fileExtensions["SRC"]
                sources = glob.glob(f"{testsetPath}/{line}/{sourceExtension}")

                # Source file is guaranteed to exist, verify all other requested files exist
                for source in sources:
                    evalEntry = {}
                    for name, extension in fileExtensions.items():
                        matchingFileName = re.sub(sourceExtension[1:] + "$", "", source) + extension[1:]
                        if not os.path.exists(matchingFileName):
                            raise Exception(f"{name} {extension} -- {matchingFileName} does not exist")
                        evalEntry[name] = os.path.realpath(matchingFileName)
                    yield (evalEntry)

def main():
    paths = [path for path in parseIndexFile(sys.argv[1], sys.argv[2])]
    print(json.dumps(paths))

if __name__ == "__main__":
    main()