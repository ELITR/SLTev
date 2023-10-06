import pkg_resources
import os
import sys
from sacremoses import MosesTokenizer, MosesDetokenizer
from utilities import eprint, split_gold_inputs_from_candidates, extract_gold_files_for_candidate
from utilities import check_empty_line, osst_checking, pipeline_input, get_SLTev_home_path
from utilities import check_time_stamp_candiates_format, submission_argument, parity_checking_between_ostt_reference
from evaluator import normal_timestamp_evaluation, simple_timestamp_evaluation
from evaluator import normal_evaluation_without_parity, print_headers
from ASRev import simple_asr_evaluation, normal_asr_evaluation
from files_modules import read_reference_file, read_candidate_file
from files_modules import read_ostt_file
from multi_docs_utils import get_ref_docs, get_candidate_docs, get_ostt_docs
from multi_docs_utils import docs_count_checking, docs_ostt_ref_parity_checking
from multi_docs_evaluator import multi_docs_flicker_evaluation, simple_multi_docs_flicker_evaluation
from multi_docs_evaluator import multi_docs_quality_evaluation, simple_multi_docs_quality_evaluation
from multi_docs_evaluator import multi_docs_delay_evaluation, simple_multi_docs_delay_evaluation

def ost_checking(gold_files, split_token):
    check_all_gold_files_flag = 0
    for file in gold_files["ost"]:
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
    

def read_ost_asr_files(ost_file):
    """
    Read OStt or ost files

    :param ost_file: the input OStt or OSt file path
    :return sentences: the OSt sentences without time-stamps (just complete segments which tokenized by Moses tokenizer)
    """

    sentences = []
    tokenize = MosesTokenizer().tokenize
    with open(ost_file, "r", encoding="utf8") as in_file:
        line = in_file.readline()
        while line:
            line = tokenize(line.strip())
            if line == []:
                line = in_file.readline()
                continue
            if line[0] != "P" and line[0] != "C":
                sentences.append(line)
            elif "C" == line[0]:
                l = line[3:]
                sentences.append(l)
            line = in_file.readline()
    sentences = list(filter(lambda a: a != [], sentences))
    return sentences


def multi_docs_asr_evaluation(candidate_file, gold_files, split_token, simple, sltev_home):
    ost = read_ost_asr_files(gold_files["ost"][0])
    asr = read_ost_asr_files(candidate_file[0])
    ost_sentences = []
    for line in ost:
        if not ''.join(line).startswith(split_token):
            ost_sentences.append(line)
    asr_sentences = []
    for line in asr:
        if not ''.join(line).startswith(split_token):
            asr_sentences.append(line)
    inputs_object = {
        'ost': ost_sentences,
        'asr': asr_sentences, 
        'SLTev_home':  sltev_home,
        }
    if simple == "False":
        normal_asr_evaluation(inputs_object)
    else:
        simple_asr_evaluation(inputs_object)
    

def multi_docs_asrt_evaluation(candidate_file, gold_files, split_token, simple, sltev_home):
    ostt_lines = read_ostt_file(gold_files["ostt"][0])
    ostt_docs = get_ostt_docs(ostt_lines, split_token)
    references = read_references(gold_files["ost"])
    references_docs = get_ref_docs(references, split_token)
    candidate_lines = read_candidate_file(candidate_file[0])
    candidate_docs = get_candidate_docs(candidate_lines, split_token)

    evaluation_object = {
        'ostt_docs': ostt_docs,
        'candidate_docs': candidate_docs,
        'references_docs': references_docs,
        'SLTev_home' : sltev_home
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
    SLTev_home = get_SLTev_home_path()
    simple = arguments.get('simple', "False")
    docs = arguments.get('docs', "False")
    split_token = arguments.get('splitby', "###docSpliter###")

    if len(input_files) % len(file_formats) != 0:
        eprint("inputs length and file_formats are not equal.")
        sys.exit(1)

    candidates , gold_inputs = split_gold_inputs_from_candidates(input_files, file_formats)

    for candidate_file, gold_input in zip(candidates, gold_inputs):
        gold_files, error = extract_gold_files_for_candidate(candidate_file, gold_input)
        if error == 1:
            continue

        if candidate_file[1] == "asr":
            if not ost_checking(gold_files, split_token): # ost checking
                continue
            print(
                "Evaluating the file ",
                candidate_file[0],
                " in terms of  WER score against ",
                gold_files["ost"][0],
                )

            if docs != "False":
                multi_docs_asr_evaluation(candidate_file, gold_files, split_token, simple, SLTev_home)
                continue
            
            inputs_object = {
                'ost': read_ost_asr_files(gold_files["ost"][0]),
                'asr': read_ost_asr_files(candidate_file[0]), 
                'SLTev_home':  SLTev_home,
                }
            if simple == "False":
                normal_asr_evaluation(inputs_object)
            else:
                simple_asr_evaluation(inputs_object)

        elif candidate_file[1] == "asrt":
            if not ost_checking(gold_files, split_token): # ost checking
                continue
            if osst_checking(gold_files["ostt"][0], split_token) == 1: # OStt checking
                continue
            inputs_object = {
                'ostt': read_ostt_file(gold_files["ostt"][0]),
                'references': read_references(gold_files["ost"]),
                'SLTev_home': SLTev_home,
                'candidate': read_candidate_file(candidate_file[0]),
                'src': read_references(gold_files["ost"])
            }

            _ = check_time_stamp_candiates_format(candidate_file[0], split_token) # submission checking

            if docs != "False":
                multi_docs_asrt_evaluation(candidate_file, gold_files, split_token, simple, SLTev_home)
                continue  

            parity_state, error = parity_checking_between_ostt_reference(gold_files["ostt"][0], gold_files["ost"])
            if parity_state == 0:
                eprint(error)
                normal_evaluation_without_parity(inputs_object)
                continue            
            print(
                "Evaluating the file ",
                candidate_file[0],
                " in terms of translation quality against ",
                " ".join(gold_files["ost"]),
            )

            if simple == "False":
                normal_timestamp_evaluation(inputs_object)
            else:
                simple_timestamp_evaluation(inputs_object)
                
        else:
            eprint("Evaulation for ", candidate_file[0], " failed, it is not an ASR file")


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


