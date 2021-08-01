import os
import sys
from utilities import eprint, split_gold_inputs_from_candidates, extract_gold_files_for_candidate
from utilities import check_empty_line, osst_checking, pipeline_input, get_SLTev_home_path
from utilities import check_time_stamp_candiates_format, submission_argument, parity_checking_between_ostt_reference
from evaluator import normal_timestamp_evaluation, simple_timestamp_evaluation
from evaluator import normal_evaluation_without_parity, print_headers
from files_modules import read_reference_file, read_candidate_file
from files_modules import read_ostt_file
from multi_docs_evaluator import multi_docs_flicker_evaluation, multi_docs_quality_evaluation
from multi_docs_evaluator import multi_docs_delay_evaluation
from multi_docs_evaluator import simple_multi_docs_flicker_evaluation, simple_multi_docs_quality_evaluation
from multi_docs_evaluator import simple_multi_docs_delay_evaluation
from multi_docs_utils import get_ostt_docs, get_ref_docs, get_candidate_docs
from multi_docs_utils import docs_count_checking, docs_ostt_ref_parity_checking

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


def multi_docs_evaluation(candidate_file, gold_files, split_token, simple, SLTev_home):
    ostt_lines = read_ostt_file(gold_files["ostt"][0])
    ostt_docs = get_ostt_docs(ostt_lines, split_token)
    references = read_references(gold_files["ref"])
    references_docs = get_ref_docs(references, split_token)
    candidate_lines = read_candidate_file(candidate_file[0])
    candidate_docs = get_candidate_docs(candidate_lines, split_token)

    evaluation_object = {
        'ostt_docs': ostt_docs,
        'candidate_docs': candidate_docs,
        'references_docs': references_docs,
        'SLTev_home' : SLTev_home
    }
    if not docs_count_checking(evaluation_object):
        return
    if simple == "False":
        print_headers()
        if not docs_ostt_ref_parity_checking(evaluation_object):
            multi_docs_flicker_evaluation(evaluation_object)
            multi_docs_quality_evaluation(evaluation_object)
            return
        multi_docs_delay_evaluation(evaluation_object)
        multi_docs_flicker_evaluation(evaluation_object)
        multi_docs_quality_evaluation(evaluation_object)
    else:
        if not docs_ostt_ref_parity_checking(evaluation_object):
            simple_multi_docs_flicker_evaluation(evaluation_object)
            simple_multi_docs_quality_evaluation(evaluation_object)
            return
        simple_multi_docs_delay_evaluation(evaluation_object)
        simple_multi_docs_flicker_evaluation(evaluation_object)
        simple_multi_docs_quality_evaluation(evaluation_object)


def main(input_files=[], file_formats=[], arguments={}):
    
    simple = arguments.get('simple', "False")
    docs = arguments.get('docs', "False")
    split_token = arguments.get('splitby', "###docSpliter###")

    sltev_home = get_SLTev_home_path()
    if len(input_files) % len(file_formats) != 0:
        eprint("inputs length and file_formats are not equal.")
        sys.exit(1)

    candidates, gold_inputs = split_gold_inputs_from_candidates(input_files, file_formats)

    for candidate_file, gold_input in zip(candidates, gold_inputs):
        gold_files, error = extract_gold_files_for_candidate(candidate_file, gold_input)
        if error == 1:
            continue
        if candidate_file[1] == "slt":

            if not reference_checking(gold_files, split_token): # reference checking
                continue

            if osst_checking(gold_files["ostt"][0], split_token) == 1: # OStt checking
                continue

            evaluation_object = {
                'ostt': read_ostt_file(gold_files["ostt"][0]),
                'references': read_references(gold_files["ref"]),
                'candidate': read_candidate_file(candidate_file[0]),
                'align': gold_files["align"],
                'SLTev_home':  sltev_home,
            }

            state = check_time_stamp_candiates_format(candidate_file[0], split_token) # candidate checking
            if state:
                continue

            if docs != "False":
                multi_docs_evaluation(candidate_file, gold_files, split_token, simple, sltev_home)
                continue

            parity_state, error = parity_checking_between_ostt_reference(gold_files["ostt"][0], gold_files["ref"])
            if parity_state == 0:
                eprint(error)
                normal_evaluation_without_parity(evaluation_object)
                continue
            
            if (
                gold_files["align"] != [] and 
                len(gold_files["align"]) != len(gold_files["ref"])
                ):
                eprint(
                    "Evaluating the file ",
                    candidate_file[0],
                    " failed, the number of TT files and align files not equal",
                )
                continue

            print(
                "Evaluating the file ",
                candidate_file[0],
                " in terms of translation quality against ",
                " ".join(gold_files["ref"]),
            )

            if simple == "False":
                normal_timestamp_evaluation(evaluation_object)
            else:
                simple_timestamp_evaluation(evaluation_object)
        else:
            eprint("Evaulation for ", candidate_file[0], " failed, it is not an SLT file")


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



