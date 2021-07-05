#!/usr/bin/env python

import os
import sys
import argparse
from os import getcwd
import shutil
import git
import pkg_resources
from filelock import FileLock
from sacremoses import MosesTokenizer

from utilities import eprint, population, generate_index_files
from utilities import split_submissions_gold_inputs, split_gold_inputs_submission_in_working_directory
from utilities import remove_digits
import ASReval
import MTeval
import SLTeval


def SLTev_argument_parser():
    parser = argparse.ArgumentParser(
        description="Evaluate outputs of SLT/MT/ASR systems in a reproducible way. Use custom inputs and references, or use inputs and references from https://github.com/ELITR/elitr-testset"
    )
    parser.add_argument(
        "-g",
        metavar="INDEX",
        help="generate an 'evaluation directory' with inputs for your system based on elitr-testset index called INDEX",
        type=str,
    )
    parser.add_argument(
        "--simple",
        help="report a simplified set of scores",
        action="store_true",
        default="False",
    )
    parser.add_argument(
        "--aggregate",
        help="aggregate all scores and shows them in the standard output instead of produce score files",
        action="store_true",
        default="False",
    )
    parser.add_argument(
        "--outdir",
        "-O",
        help="put outputs (input files for -g, results for -e) in OUTDIR",
        type=str,
    )
    parser.add_argument(
        "-T",
        "--elitr-testset",
        metavar="DIR",
        help="use DIR as git clone of elitr-testset instead of elitr-testset",
        default="elitr-testset",
        type=str,
    )
    parser.add_argument(
        "-e", metavar="EVALDIR", help="evaluate evaluation directory EVALDIR", type=str
    )
    parser.add_argument(
        "--commitid",
        help="use elitr-testset at commit COMMITID",
        default="HEAD",
        type=str,
    )
    parser.add_argument(
        "--version",
        help="report the SLTev version",
        action="store_true",
        default="False",
    )
    args = parser.parse_args()
    return args, parser


def print_SLTev_version(args, SLTev_home):
    if args.version != "False":
        try:
            __version__ = pkg_resources.get_distribution("SLTev").version
            eprint(__version__)
        except:
            try:
                repo = git.Repo(os.path.split(SLTev_home)[0])
                commit_id = repo.head.commit
                eprint("The commit id is: ", commit_id)
            except:
                eprint(
                    "SLTev is not installed, you can use the following command for installation:\n pip install SLTev"
                )
        sys.exit(1)


def moses_tokenizer_checking():
    try:
        tokenize = MosesTokenizer().tokenize
        tokens = tokenize("Hello World!")
        assert tokens == [
            "Hello",
            "World",
            "!",
        ], "sacremoses is badly installed, run as follow for fix: pip install --upgrade sacremoses"
    except:
        eprint(
            "sacremoses is badly installed, run as follow for fix:\n pip install --upgrade sacremoses"
        )
        sys.exit(1)


def checking_correct_arguments(args, parser):
    if args.e is None and args.g is None:
        parser.print_help()
        sys.exit(1)


def make_output_directory(args):
    output_dir = ""
    if args.outdir is None:
        if args.e is not None:
            output_dir = args.e
        else:
            output_dir = "outdir"
    else:
        output_dir = args.outdir

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    return output_dir


def get_SLTev_commit_id(SLTev_home):
    SLTev_commit_id = ""
    try:
        repo = git.Repo(os.path.split(SLTev_home)[0])
        sha = repo.head.object.hexsha
        SLTev_commit_id = "SLTev_" + repo.git.rev_parse(sha, short=True) + "-"
    except:
        try:
            SLTev_commit_id = (
                "SLTev_version_" + pkg_resources.get_distribution("SLTev").version + "-"
            )
        except:
            SLTev_commit_id = "SLTev_NONE" + "-"
    return SLTev_commit_id


def get_elitr_commit_id(elitr_path):
    try:
        repo = git.Repo(elitr_path)
        elitr_commit_id = repo.head.commit
    except:
        elitr_commit_id = ""
    return elitr_commit_id


def do_population(elitr_path):
    try:
        population(
            elitr_path, os.environ.copy()["ELITR_CONFIDENTIAL_PASSWORD"]
        )  # link population
    except:
        eprint("ELITR_CONFIDENTIAL_PASSWORD=... was not used") 


def pull_and_populate(elitr_path):
    try:
        repo = git.Repo(elitr_path)
        repo.remotes.origin.pull()
        do_population(elitr_path)
        sha = repo.head.object.hexsha
        elitr_commit_id = "elitrtestset_" + repo.git.rev_parse(sha, short=True)
        eprint("elitr-testset pulled")
        return elitr_commit_id
    except:
        eprint(
            "Pull from elitr-testset at " + elitr_path + " failed.\n"
            + "Is it a valid git clone? Do I have the git keys/password?\n"
            + "Test manually:\n  cd " + elitr_path + "; git pull"
        )
        sys.exit(1)


def clone_and_populate(git_path, elitr_path):
    try:
        eprint("cloning elitr-testset repo to dir: ", elitr_path)
        eprint("...this does take a while and needs a lot of disk space")
        git.Repo.clone_from(git_path, elitr_path)
        do_population(elitr_path)
        repo = git.Repo(elitr_path)
        sha = repo.head.object.hexsha
        elitr_commit_id = "elitrtestset_" + repo.git.rev_parse(sha, short=True)
        return elitr_commit_id
    except:
        eprint(
            "cloning from elitr-testset failed, please check your internet conection"
        )
        sys.exit(1)


def check_out(args, elitr_path):
    try:
        repo = git.Repo(elitr_path)
        repo.git.checkout(args.commitid)
        eprint("checkout to ", args.commitid, " done.")
    except:
        eprint(args.commitid, " is not valid")


def extract_index_files(args, elitr_commit_id, elitr_path, output_dir):
    try:
        eprint("elitr-testset commit id is: ", elitr_commit_id)
        with FileLock(os.path.join(elitr_path, "SLTev.lock")):
            generate_index_files(elitr_path, args.g, output_dir)
    except:
        eprint(
            "Generating index ",
            args.g,
            " failed. Check ",
            args.g,
            " index, it does not seem to exist, also check ",
            output_dir,
            " for write permision",
        )


def generate_files_from_index(args, elitr_path, output_dir):
    git_path = "https://github.com/ELITR/elitr-testset.git"
    elitr_commit_id = ""
    if os.path.isdir(elitr_path): # if cloned 
        elitr_commit_id = pull_and_populate(elitr_path)
    else:
        elitr_commit_id = clone_and_populate(git_path, elitr_path)
    if args.commitid != "HEAD":
        check_out(args, elitr_path)

    extract_index_files(args, elitr_commit_id, elitr_path, output_dir) # extract index files


def check_working_directory(working_dir):
    if os.path.isdir(working_dir):
        eprint("working directory is ", working_dir)
    else:
        eprint(working_dir, " does not exist.")
        sys.exit(1)


def make_signature(SLTev_commit_id, elitr_path):
    signature = SLTev_commit_id
    if os.path.isdir(elitr_path):
        try:
            repo = git.Repo(elitr_path)
            sha = repo.head.object.hexsha
            elitr_commit_id = "elitrtestset_" + repo.git.rev_parse(sha, short=True)
            signature = signature + elitr_commit_id
        except:
            signature = signature + "elitrtestset_NONE"
    else:
        signature = signature + "elitrtestset_NONE"
    
    return signature


def asr_submission_evaluation(args, inputs_object):
    if args.aggregate != "False":
        print("Signature: ", inputs_object.get('signature'))
        ASReval.main(inputs_object.get('input_files'), inputs_object.get('file_formats'), args.simple)
    else:
        out_name = (
            os.path.join(
                inputs_object.get('output_dir'),
                os.path.split(inputs_object.get('submission_file'))[1]
                )
            + ".WER.out"
            )
        with open(out_name, "w") as f:
            sys.stdout = f
            print("Signature: ", inputs_object.get('signature'))
            ASReval.main(inputs_object.get('input_files'), inputs_object.get('file_formats'), args.simple)
            sys.stdout = inputs_object.get('original_stdout')
        eprint("Results saved in ", out_name)


def asrt_submission_evaluation(args, inputs_object):
    if args.aggregate != "False":
        print("Signature: ", inputs_object.get('signature'))
        ASReval.main(inputs_object.get('input_files'), inputs_object.get('file_formats'), args.simple)
    else:
        out_name = (
            os.path.join(inputs_object.get('output_dir'), os.path.split(inputs_object.get('submission_file'))[1])
            + ".BLEU.out"
        )
        with open(out_name, "w") as f:
            sys.stdout = f
            print("Signature: ", inputs_object.get('signature'))
            ASReval.main(inputs_object.get('input_files'), inputs_object.get('file_formats'), args.simple)
            sys.stdout = inputs_object.get('original_stdout')
        eprint("Results saved in ", out_name)


def mt_submission_evaluation(args, inputs_object):
    if args.aggregate != "False":
        print("Signature: ", inputs_object.get('signature'))
        MTeval.main(inputs_object.get('input_files'), inputs_object.get('file_formats'), args.simple)
    else:
        out_name = (
            os.path.join(inputs_object.get('output_dir'), os.path.split(inputs_object.get('submission_file'))[1])
            + ".BLEU.out"
        )
        with open(out_name, "w") as f:
            sys.stdout = f
            print("Signature: ", inputs_object.get('signature'))
            MTeval.main(inputs_object.get('input_files'), inputs_object.get('file_formats'), args.simple)
            sys.stdout = inputs_object.get('original_stdout')
        eprint("Results saved in ", out_name)


def slt_submission_evaluation(args, inputs_object):
    if args.aggregate != "False":
        print("Signature: ", inputs_object.get('signature'))
        SLTeval.main(inputs_object.get('input_files'), inputs_object.get('file_formats'), args.simple)
    else:
        out_name = (
            os.path.join(inputs_object.get('output_dir'), os.path.split(inputs_object.get('submission_file'))[1])
            + ".BLEU.out"
        )
        with open(out_name, "w") as f:
            sys.stdout = f
            print("Signature: ", inputs_object.get('signature'))
            SLTeval.main(inputs_object.get('input_files'), inputs_object.get('file_formats'), args.simple)
            sys.stdout = inputs_object.get('original_stdout')
        eprint("Results saved in ", out_name)


def build_input_fils_and_file_formats(submission_file, gold_input_files):
    status, references, ostt, aligns = split_gold_inputs_submission_in_working_directory(submission_file, gold_input_files)

    input_files = [submission_file]
    file_formats = [remove_digits(status)]

    for reference_file in references:
        input_files.append(reference_file)
        if remove_digits(status) == "asr" or remove_digits(status) == "asrt":
            file_formats.append("ost")
        elif remove_digits(status) == "mt" or remove_digits(status) == "slt":
            file_formats.append("ref")
    if ostt != "":
        input_files.append(ostt)
        file_formats.append("ostt")

    for align_file in aligns:
        input_files.append(align_file)
        file_formats.append("align")

    return input_files, file_formats, status


def generation(args, parser, output_dir):
    # ----get commit id
    elitr_path = args.elitr_testset
    elitr_commit_id = get_elitr_commit_id(elitr_path)
    if args.g :
        generate_files_from_index(args, elitr_path, output_dir)
        sys.exit(1)


def submissions_evaluation(args, submission_object):
    if submission_object.get('submissions') == []:
        eprint(
            "No SLT/ASR/MT files in working directory ", submission_object.get('working_dir'), " for evaluatin"
        )
    for submission_file in submission_object.get('submissions'):
        input_files, file_formats, status =  build_input_fils_and_file_formats(
            submission_file, submission_object.get('gold_input_files')
            )
        inputs_object = {
            'input_files': input_files,
            'file_formats': file_formats,
            'signature':submission_object.get('signature'),
            'output_dir': submission_object.get('output_dir'),
            'submission_file': submission_file,
            'original_stdout': submission_object.get('original_stdout') 
        }
        if remove_digits(status) == "asr":
            asr_submission_evaluation(args, inputs_object)
            continue

        elif remove_digits(status) == "asrt":
            asrt_submission_evaluation(args, inputs_object)
            continue

        elif remove_digits(status) == "mt":
            mt_submission_evaluation(args, inputs_object)
            continue

        elif remove_digits(status) == "slt":
            slt_submission_evaluation(args, inputs_object)
            continue

def main():
    args, parser = SLTev_argument_parser()
    # add SLTev home to the path
    try:
        SLTev_home = pkg_resources.resource_filename("SLTev", "")
    except:
        SLTev_home = os.path.dirname(os.path.realpath(sys.argv[0]))
    sys.path.insert(1, SLTev_home)

    # print SLTev version
    print_SLTev_version(args, SLTev_home)

    # sacremoses checking
    moses_tokenizer_checking()

    SLTev_commit_id = get_SLTev_commit_id(SLTev_home)
    checking_correct_arguments(args, parser)
    output_dir = make_output_directory(args) 

    generation(args, parser, output_dir) # generation part

    # evaluation part
    elitr_path = args.elitr_testset
    working_dir = args.e
    check_working_directory(working_dir)
    signature = make_signature(SLTev_commit_id, elitr_path)

    submissions, gold_input_files = split_submissions_gold_inputs(working_dir)
    original_stdout = sys.stdout

    submission_object = {
        'submissions': submissions,
        'signature': signature,
        'gold_input_files': gold_input_files,
        'working_dir': working_dir,
        'output_dir': output_dir,
        'original_stdout': original_stdout
        }
    submissions_evaluation(args, submission_object)


if __name__ == "__main__":
    main()

