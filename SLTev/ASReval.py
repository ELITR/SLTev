import pkg_resources
import os
import sys
import argparse
from utilities import *
from ASRev import *
from evaluator import *


def main(inputs=[], file_formats=[], simple="False"):
    # -----------add SLTev home to the path
    try:
        sltev_home = pkg_resources.resource_filename("SLTev", "")
    except:
        sltev_home = os.path.dirname(os.path.realpath(sys.argv[0]))

    # checking arguments
    if len(inputs) % len(file_formats) != 0:
        eprint("inputs length and file_formats are not equal.")
        sys.exit(1)

    hypos, gold_inputs = split_inputs_hypos(inputs, file_formats)

    for hypo_file, gold_input in zip(hypos, gold_inputs):
        gold_files, error = extract_hypo_gold_files(hypo_file, gold_input)
        if error == 1:
            continue

        if hypo_file[1] == "asr":
            # ost checking
            temp_flag = 0
            for file in gold_files["ost"]:
                if check_empty_line(file) == 1:
                    temp_flag = 1
                    continue
            if temp_flag == 1:
                continue
            print(
                "Evaluating the file ",
                hypo_file[0],
                " in terms of  WER score against ",
                gold_files["ost"][0],
            )
            ASRev(
                ost=gold_files["ost"][0],
                asr=hypo_file[0],
                SLTev_home=sltev_home,
                simple=simple,
            )

        elif hypo_file[1] == "asrt":
            # ost checking
            temp_flag = 0
            for file in gold_files["ost"]:
                if check_empty_line(file) == 1:
                    temp_flag = 1
                    continue
            if temp_flag == 1:
                continue
            # OStt checking
            if check_empty_ostt_line(gold_files["ostt"][0]) == 1:
                continue
            parity_state, error = partity_test(gold_files["ostt"][0], gold_files["ost"])
            if parity_state == 0:
                eprint(
                    "Evaulation for ",
                    hypo_file[0],
                    " failed, the number of Complete lines (C) in ",
                    gold_files["ostt"][0],
                    " and ",
                    " ".join(gold_files["ost"]),
                    " are not equal",
                )
                eprint(error)
                continue
            # submission checking
            state = check_input(hypo_file[0])
            print(
                "Evaluating the file ",
                hypo_file[0],
                " in terms of translation quality against ",
                " ".join(gold_files["ost"]),
            )
            evaluator(
                ostt=gold_files["ostt"][0],
                asr=True,
                tt=gold_files["ost"],
                align=[],
                mt=hypo_file[0],
                SLTev_home=sltev_home,
                simple=simple,
            )
        else:
            eprint("Evaulation for ", hypo_file[0], " failed, it is not an ASR file")


def main_point():
    args = submission_argument()
    inputs = list()
    file_formats = list()
    if args.inputs is None:
        inputs = pipeline_input()
    else:
        for inp in args.inputs:
            inputs.append("".join(inp))

    for ords in args.file_formats:
        file_formats.append("".join(ords))

    main(inputs, file_formats, args.simple)


if __name__ == "__main__":
    args = submission_argument()
    inputs = list()
    file_formats = list()
    if args.inputs is None:
        inputs = pipeline_input()
    else:
        for inp in args.inputs:
            inputs.append("".join(inp))

    for ords in args.file_formats:
        file_formats.append("".join(ords))

    main(inputs, file_formats, args.simple)
