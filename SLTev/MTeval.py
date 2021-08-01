import sys
from utilities import eprint, split_gold_inputs_from_candidates, extract_gold_files_for_candidate
from utilities import check_empty_line, pipeline_input
from utilities import submission_argument, get_SLTev_home_path
from evaluator import normal_mt_evaluation, simple_mt_evaluation, print_headers
from files_modules import read_reference_file, read_candidate_file
from files_modules import read_ostt_file
from multi_docs_utils import get_ref_docs, get_candidate_docs
from multi_docs_evaluator import multi_docs_quality_evaluation, simple_multi_docs_quality_evaluation


def reference_checking(gold_files, split_token):
    check_all_gold_files_flag = 0
    for file in gold_files["ref"]:
        if check_empty_line(file, split_token) == 1:
            check_all_gold_files_flag = 1
            continue
    if check_all_gold_files_flag == 1:
        return 0
    return 1


def read_references(reference_files_paths):
    references = []
    for reference_path in reference_files_paths:
        references.append(read_reference_file(reference_path))
    return references


def multi_docs_mt_evaluation(candidate_file, gold_files, split_token, simple, sltev_home):
    references = read_references(gold_files["ref"])
    references_docs = get_ref_docs(references, split_token)
    candidate_lines = read_candidate_file(candidate_file[0])
    candidate_docs = get_candidate_docs(candidate_lines, split_token)
    evaluation_object = {
        'candidate_docs': candidate_docs,
        'references_docs': references_docs,
        'SLTev_home' : sltev_home
    }

    if simple == "False":
        print_headers()
        multi_docs_quality_evaluation(evaluation_object)
    else:
        simple_multi_docs_quality_evaluation(evaluation_object)


def main(inputs=[], file_formats=[], arguments={}):

    simple = arguments.get('simple', "False")
    docs = arguments.get('docs', "False")
    split_token = arguments.get('splitby', "###docSpliter###")

    sltev_home = get_SLTev_home_path()
    if len(inputs) % len(file_formats) != 0:
        eprint("inputs length and file_formats are not equal.")
        sys.exit(1)

    candidates, gold_inputs = split_gold_inputs_from_candidates(inputs, file_formats)

    for candidate_file, gold_input in zip(candidates, gold_inputs):
        gold_files, error = extract_gold_files_for_candidate(candidate_file, gold_input)
        if error == 1:
            continue

        if candidate_file[1] == "mt":
            
            if not reference_checking(gold_files, split_token): # reference checking
                continue

            print(
                "Evaluating the file ",
                candidate_file[0],
                " in terms of translation quality against ",
                " ".join(gold_files["ref"]),
            )

            if docs != "False":
                multi_docs_mt_evaluation(candidate_file, gold_files, split_token, simple, sltev_home)
                continue

            evaluation_object = {
                'references': read_references(gold_files["ref"]),
                'mt': read_candidate_file(candidate_file[0]), 
                'SLTev_home':  sltev_home,
            }

            if simple == "False":
                normal_mt_evaluation(evaluation_object)
            else:
                simple_mt_evaluation(evaluation_object)

        else:
            eprint("Evaulation for ", candidate_file[0], " failed, it is not an MT file")


def call_arguments():
    args = submission_argument()
    input_files = list()
    file_formats = list()
    if args.inputs is None:
        input_files = pipeline_input()
    else:
        for inp in args.inputs:
            input_files.append("".join(inp))

    for ords in args.file_formats:
        file_formats.append("".join(ords))
    return input_files, file_formats, args


def main_point():
    input_files, file_formats, args = call_arguments()
    arguments = {
        "docs": args.docs,
        'simple': args.simple,
        'splitby': args.splitby,
    }
    main(input_files, file_formats, arguments)

if __name__ == "__main__":
    input_files, file_formats, args = call_arguments()
    arguments = {
        "docs": args.docs,
        'simple': args.simple,
        'splitby': args.splitby,
    }
    main(input_files, file_formats, arguments)


