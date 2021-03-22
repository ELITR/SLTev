import os
import sys
import glob
import re

"""
Read an index file with meta-annotations and return tuples of (SOURCE, REFERENCE) absolute paths to file.
Annotations specify the source and target file prefixes and apply to a specified directory.
An index file can contain multiple annotations.
Index file format:

# SRC *.<PREFIX>
# TRG *.<PREFIX>
PATH_TO_DIRECTORY
"""

def parseIndexFile(indexFilePath, testsetPath):
    SRC = None
    REF = None
    with open(indexFilePath) as indexFile:
        for line in indexFile:
            line = line.rstrip()
            # Line format:  # SRC: *.en.OSt
            if line.startswith("#"):
                if line.startswith("# SRC "):
                    SRC = line.split(" ")[2]
                elif line.startswith("# REF "):
                    REF = line.split(" ")[2]
            elif len(line) > 0:
                if not SRC or not REF:
                    raise Exception("SRC or REF file suffix not specified")
                sources = glob.glob(f"{testsetPath}/{line}/{SRC}")
                references = glob.glob(f"{testsetPath}/{line}/{REF}")

                sourceSuffix = SRC[1:]
                referenceSuffix = REF[1:]
                for source in sources:
                   reference = next(filter(lambda ref: re.sub(referenceSuffix + "$", sourceSuffix, ref) == source, references))
                   if reference:
                       yield (os.path.realpath(source), os.path.realpath(reference))

def main():
    pairs = parseIndexFile(sys.argv[1], sys.argv[2])
    for pair in pairs:
        print(f"{pair[0]}\t{pair[1]}")

if __name__ == "__main__":
    main()