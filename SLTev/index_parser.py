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

## --no-* args
class ActionNoYes(argparse.Action):
    def __init__(self, option_strings, dest, default=None, required=False, help=None):

        if default is None:
            raise ValueError('You must provide a default with Yes/No action')
        if len(option_strings)!=1:
            raise ValueError('Only single argument is allowed with YesNo action')
        opt = option_strings[0]
        if not opt.startswith('--'):
            raise ValueError('Yes/No arguments must be prefixed with --')

        opt = opt[2:]
        opts = ['--' + opt, '--no-' + opt]
        super(ActionNoYes, self).__init__(opts, dest, nargs=0, const=None, 
                                          default=default, required=required, help=help)
    def __call__(self, parser, namespace, values, option_strings=None):
        if option_strings.startswith('--no-'):
            setattr(namespace, self.dest, False)
        else:
            setattr(namespace, self.dest, True)
## end of --no-* args


def main():
    parser = argparse.ArgumentParser(
        description="Interpret index files of elitr-testset (https://github.com/ELITR/elitr-testset/tree/master/indices) and print them as simple file lists."
    )
    parser.add_argument("indexfile_path",
      help = "path to the index file",
      type = str,
    )
    parser.add_argument("elitr_testset_path",
      help = "path to your clone of elitr-testset",
      type = str,
    )
    parser.add_argument('--relative', action=ActionNoYes, default=True,
      help = "treat indexfile_path relative to indices/ in elitr_testset_path",
    )
    parser.add_argument("--format", "-f",
      help = "print output as tsv or json",
      type = str,
      default = "tsv",
    )
    args = parser.parse_args()

    indexfile_path = args.elitr_testset_path+"/indices/"+args.indexfile_path if args.relative else args.indexfile_path
    print(args.indexfile_path)
    print(indexfile_path)
    paths = [path for path in parseIndexFile(indexfile_path, args.elitr_testset_path)]
    if args.format == "json":
      print(json.dumps(paths))
    else:
      # collect used colnames
      colnames = list(set([colname for d in paths for colname in d.keys()]))
      print("\t".join(colnames))
      for d in paths:
        colvals = [ d[c] if d[c] is not None else "" for c in colnames ]
        print("\t".join(colvals))

if __name__ == "__main__":
    main()
