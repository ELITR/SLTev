import os
import sys
from os import getcwd
import shutil
import argparse
import pkg_resources


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def remove_extra_spaces(text):
    """
    remove free spaces in the input string

    :param text: input string
    :return text: preprocessed output string
    """

    text = text.replace("\t", "")
    text = text.replace(" ", "")
    return text


def get_SLTev_home_path():
    try:
        sltev_home = pkg_resources.resource_filename("SLTev", "")
    except:
        sltev_home = os.path.dirname(os.path.realpath(sys.argv[0]))
    
    if not sltev_home:
        sltev_home = os.path.dirname(os.path.realpath(sys.argv[0]))
    return sltev_home


def population(elitr_path, password):
    """
    populate link files using elitr-testset/populate.sh

    :param elitr_path: path of the cloning elitr-testset repo
    :param password: an string like as ELITR_CONFIDENTIAL_PASSWORD=...
    """

    current_path = os.getcwd()
    os.chdir(elitr_path)

    cmd = (
        "ELITR_CONFIDENTIAL_PASSWORD="
        + remove_extra_spaces(password)
        + " ./populate.sh"
    )
    os.system(cmd)
    eprint("population done.")
    os.chdir(current_path)


def copy_index_file_to_output(index_file_path, target_path):
    """
    copy files from the index to the target path.

    :param index_file_path: a list of index files
    :param target_path: path of the target directory
    """

    if index_file_path.endswith(".link") or index_file_path.endswith(".url"):
        index = remove_extra_spaces(index_file_path)
        with open(index) as link_f:
            link_files = link_f.readlines()
            for file in link_files:
                shutil.copy2(file, target_path)
    else:
        indice = remove_extra_spaces(index_file_path)
        shutil.copy2(indice, target_path)


def chop_elitr_testset_prefix(path):
    path_split = path.split("/")
    if path_split[0] == "elitr-testset":
        return "/".join(path_split[1:])
    else:
        return path


def check_empty_line(file):
    """
    check for empty lines

    :param file: path of the file
    :return : status of error
    """
    with open(file, "r", encoding="utf8") as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if not lines[i].strip():
                eprint("The file ", file, ", line ", i, " is empty. please remove it.")
                return 1
    return 0


def osst_checking(file):
    """
    check OStt file for correct format and empty lines

    :param file: path of the file
    :return : status of error
    """
    with open(file, "r", encoding="utf8") as f:
        lines = f.readlines()
        for i in range(len(lines)):
            if not lines[i].strip():
                eprint("The file ", file, ", line ", i, " is empty. please remove it.")
                return 1
            line = lines[i].strip().split()
            try:
                if (
                    line[0] not in ["P", "C"]
                    or int(line[1]) < -1
                    or int(line[2]) < -1
                    or line[3:] == []
                    or line[3:] == [""]
                ):
                    eprint(
                        "The file ",
                        file,
                        ", line ",
                        i,
                        " does not have true format (C/P 0 0 ) or it is empty line",
                    )
                    return 1
            except:
                pass

    return 0


def generate_index_files(elitr_testset_path, indexname, target_path):
    """
    populate and copy index files from elitr-testset to the target directory

    :param elitr_testset_path: path of elitr-testset repo
    :param indexname: index name
    :param target_path: path of the target directory
    """
    index_file_path = os.path.join(elitr_testset_path, "indices", indexname)
    indices = [index_file_path]
    indices_lines = []
    while indices != []:
        index_file_path = indices.pop()
        with open(index_file_path) as f:
            lines = f.readlines()
            lines = [i.strip() for i in lines if i.strip() != ""]
        for line in lines:
            if line.startswith("#include "):
                indice = remove_extra_spaces(line[9:])
                indice_path = os.path.join(
                    elitr_testset_path, "indices", chop_elitr_testset_prefix(indice)
                )
                indices.append(indice_path)
            elif line == "" or line[0] == "#":
                continue
            else:
                indices_lines.append(
                    os.path.join(elitr_testset_path, chop_elitr_testset_prefix(line))
                )

    for line in indices_lines: # copy files
        if line[0] == "#":
            pass
        else:
            try:
                copy_index_file_to_output(line, target_path)
                eprint(line + " copied to " + target_path)
            except:
                eprint("copying file", line, "failed. please check this file in index")


def remove_digits(string):
    """
    remove digits from the input string

    :param string: input string
    :return result: preprocessed input string (removing digits from the path)
    """

    result = "".join([i for i in string if not i.isdigit()])
    return result


def check_time_stamp_candiates_format(in_file):
    """
    check timestamp candidate files

    :param in_file: input MT/SLT/ASR file path
    """

    lines = open(in_file, "r").readlines()
    state = 0
    for i in range(len(lines)):
        line = lines[i].strip().split(" ")
        if line == []:
            continue
        if line[0] != "C" and line[0] != "P":
            text = (
                "File "
                + in_file
                + " and line "
                + str(i)
                + " is not in the proper format  please correct this line as C/P 0 0 0 <text line>"
            )
            state = 1
            eprint(text)
            break

        try:
            if float(line[1]) > -1 and float(line[2]) > -1 and float(line[3]) > -1:
                if line[4:] != [] and line[4:] != [""]:
                    pass
                else:
                    eprint(
                        "The file ",
                        in_file,
                        ", line ",
                        i,
                        " does not have true format (C/P 0 0 0 ) or it is empty line",
                    )
                    state = 1
                    break
        except:
            print("line is ", line)
            print("int(line[1])", float(line[1]))
            text = (
                "File "
                + in_file
                + " and line "
                + str(i)
                + " is not in the proper format  please correct this line as C/P 0 0 0 <text line> or it is empty"
            )
            state = 1
            eprint(text)
            break

    return state


def split_submissions_gold_inputs(working_dir):
    """
    split submmisions and inputs files for SLTev evaluation from working directory (a folder which contains inputs (OStt/OSt/...) and submmisions (SLT/ASR/MT))

    :param working_dir: path of working directory (args.e avalue).
    :return submissions: a list of submmisione files
    :return inputs: a list of input files
    """

    submissions = []
    gold_inputs = []
    for _, _, files in os.walk(working_dir):
        for f in files:
            file_path = os.path.join(working_dir, f)
            file_format = remove_digits(f.split(".")[-1])
            if file_format == "slt" or file_format == "asr" or file_format == "mt" or file_format == "asrt":
                submissions.append(file_path)
            elif file_format == "OSt" or file_format == "OStt" or file_format == "align":
                gold_inputs.append(file_path)
    return submissions, gold_inputs


def split_gold_inputs_submission_in_working_directory(submission_file, gold_inputs):
    """
    extract OSt , align and OStt from the input files.

    :param submission_file: path of the submission file
    :param inputs: a list of input files (OSt/OStt/align)
    :return status: state of the submission, a value among (asr, slt, mt)
    :return tt, ostt, align: OSt, OStt, align files  according to the submission file
    """

    status, ostt = "", ""
    references, aligns = list(), list()

    submission_file_name = os.path.split(submission_file)[1]
    submission_file_name_without_prefix = ".".join(submission_file_name.split(".")[:-3])

    source_lang = submission_file_name.split(".")[-3]
    target_lang = submission_file_name.split(".")[-2]

    status = submission_file_name.split(".")[-1]

    for file in gold_inputs:
        input_name = os.path.split(file)[1]
        input_name = input_name.split(".")
        if (
            ".".join(input_name[:-1]) + "." + remove_digits(input_name[-1])
            == submission_file_name_without_prefix + "." + target_lang + ".OSt"
        ):
            references.append(file)
        elif (
            ".".join(input_name[:-1]) + "." + remove_digits(input_name[-1])
            == submission_file_name_without_prefix + "." + source_lang + ".OStt"
        ):
            ostt = file
        elif (
            ".".join(input_name[:-1]) + "." + remove_digits(input_name[-1])
            == submission_file_name_without_prefix + "." + source_lang + "." + target_lang + ".align"
        ):
            aligns.append(file)
    return status, references, ostt, aligns


def mwerSegmenter_error_message():
    eprint(
            " Running mwerSegmenter faild, please check SLTev installed correctly (pip install --upgrade SLTev).\n",
            "mwerSegmenter just run in the Linux and it will be failed in the other operating systems."
        )

def count_complete_segments(segments):
    counter = 0
    for segment in segments:
        if segment.strip().split() == []:
            continue
        if segment.strip().split()[0] == "C":
            counter += 1
    return counter


def parity_checking_between_ostt_reference(ostt, references):
    """
    checks equalness of the number of C (complete) lines in OStt and reference

    :param ostt: the path of ostt file
    :param tt_list: a list of tt (OSt) file pthes
    :return status: error checking state (if safe it equal to 1 and otherwise is 0)
    :return error: error string (if safe it equal with '')
    """

    status = 1
    error = ""
    with open(ostt) as f:
        ostt_complete_segment_count = count_complete_segments(f.readlines())
    for ref in references:
        with open(ref) as f:
            ref_length = len(f.readlines())
        if ostt_complete_segment_count != ref_length:
            status = 0
            error = (
                "The number of C segment (complete) in "
                + ostt
                + " is "
                + str(ostt_complete_segment_count)
                + " and number of lines in "
                + ref
                + " is "
                + str(ref_length)
            )
            break
    return status, error


def MT_checking(file):
    """
    check MT that contain at least one C(Complete) segment

    :param file: path of the MT/ASR/SLT file.
    :return status: error checking state (if safe it equal to 1 and otherwise is 0)
    """

    status = 0
    with open(file) as f:
        mt_sentence = count_complete_segments(f.readlines())
        if mt_sentence > 0:
            status = 1
    return status

    
def split_gold_inputs_from_candidates(input_files, file_formats):
    """
    splitting inputs and hypothesis

    :param input_files: a list of the input file paths
    :param file_formats: a list of input file formats in order
    :return hypos: a list of the hypothesis files [[hypo_path, format], []]
    :return gold_inputs: a list of the gold input files [{format:[file1, ...], ...}, {format:[file1, ...], ...},]
    """

    # making file_formats length as inputs length
    if len(input_files) != len(file_formats):
        formats = file_formats[:]
        for i in range(1, int(len(input_files) / len(formats))):
            file_formats += formats
    # calling error checking
    # There is two correct format:
    # First, candiates are before inputs
    # Second, candidats are after inputs
    if (file_formats[0] in ["asrt", "asr", "slt", "mt"] or
        file_formats[-1] in ["asrt", "asr", "slt", "mt"]):
        pass
    else:
        eprint("the calling format is not correct,\n\
candidates (such as slt) must be before or after its inputs")
        sys.exit(1)

    candidates = list()
    gold_inputs = list()
    input_candidates = {}
    for input, format in zip(input_files, file_formats):
        if format in ["asrt", "asr", "slt", "mt"]:
            candidates.append([input, format])
            if input_candidates != {}:
                gold_inputs.append(input_candidates)
                input_candidates = {}
        else:
            try:
                input_candidates[format].append(input)
            except:
                input_candidates[format] = [input]
    if input_candidates != {}:
        gold_inputs.append(input_candidates)
    return candidates, gold_inputs


def extract_asr_gold_files_for_candidate(candidate_file, gold_inputs):
    error = 0
    gold_files = {}
    try:
        gold_files["ost"] = gold_inputs["ost"]
    except:
        eprint("evaluation failed, the source file does not exist for ", candidate_file[0])
        error = 1
    return gold_files, error


def extract_asrt_gold_files_for_candidate(candidate_file, gold_inputs):
    error = 0
    gold_files = {}
    try:
        gold_files["ost"] = gold_inputs["ost"]
    except:
        eprint("evaluation failed, the source file does not exist for ", candidate_file[0])
        error = 1
    try:
        gold_files["ostt"] = gold_inputs["ostt"]
    except:
        eprint("evaluation failed, the OStt file does not exist for ", candidate_file[0])
        error = 1
    return gold_files, error 


def extract_mt_gold_files_for_candidate(candidate_file, gold_inputs):
    error = 0
    gold_files = {}
    try:
        gold_files["ref"] = gold_inputs["ref"]
    except:
        eprint( "evaluation failed, the reference file does not exist for ", candidate_file[0])
        error = 1
    return gold_files, error 


def extract_slt_gold_files_for_candidate(candidate_file, gold_inputs):
    error = 0
    gold_files = {"ref": "", "ostt": "", "align": ""}
    try:
        gold_files["ref"] = gold_inputs["ref"]
    except:
        eprint("evaluation failed, the reference file does not exist for ", candidate_file[0])
        error = 1
    try:
        gold_files["ostt"] = gold_inputs["ostt"]
    except:
        eprint("evaluation failed, the OStt file does not exist for ", candidate_file[0])
        error = 1
    try:
        gold_files["align"] = gold_inputs["align"]
    except:
        gold_files["align"] = []
    return gold_files, error 


def extract_gold_files_for_candidate(candidate_file, gold_inputs):
    """
    extracting gold files for the candidate

    :param candidate_file: path of the hypo file [hypo_path, format]
    :param gold_inputs: a dictionary of gold files {format:gold_path, ...} 
    :return error: if an error occurred it will be 1 and otherwise it will be 0
    :return out: a dict of gold files for the hypo {format:file_path}
    """

    error = 0
    gold_files = {}
    if candidate_file[1] == "asr":
        gold_files, error = extract_asr_gold_files_for_candidate(candidate_file, gold_inputs)

    elif candidate_file[1] == "asrt":
        gold_files, error = extract_asrt_gold_files_for_candidate(candidate_file, gold_inputs)

    elif candidate_file[1] == "mt":
        gold_files, error = extract_mt_gold_files_for_candidate(candidate_file, gold_inputs)

    elif candidate_file[1] == "slt":
        gold_files, error = extract_slt_gold_files_for_candidate(candidate_file, gold_inputs)
    return gold_files, error


def submission_argument():
    """
    making argument for SLTeval, ASReval and Mteval

    :return args: a parser
    """
    parser = argparse.ArgumentParser(
        description="Evaluate outputs of SLT/MT/ASR systems in a reproducible way. Use custom inputs and references, or use inputs and references from https://github.com/ELITR/elitr-testset"
    )
    parser.add_argument(
        "-i", "--inputs", help="path of the input files", type=list, nargs="+"
    )
    parser.add_argument(
        "-f",
        "--file-formats",
        help="format of the input files in order, the format can be chosen from the following dictionary keys \n {source: source files, ref: reference, ostt: timestamped gold transcript, align: align files, \
                        slt: timestamped online MT hypothesis, mt: finalized MT hypothesis, asrt:timestamped ASR hypothesis \
                        asr:finalized ASR transcript} ",
        type=list,
        nargs="+",
    )
    parser.add_argument(
        "--simple",
        help="report a simplified set of scores",
        action="store_true",
        default="False",
    )
    args = parser.parse_args()
    return args


def pipeline_input():
    """
    receive inpute files from pipeline.
    for example: echo "A.mt A.ref \n B.mt B.ref \n C.mt C.ref " | MTeval -i -f mt ref
    The output will be [A.mt, A.ref, B.mt, B.ref, C.mt, C.ref]
    """

    lines = ""
    for line in sys.stdin:
        lines += line
    inputs = lines.split()
    inputs = list(filter(lambda i: i != "\n", inputs))
    inputs = list(filter(lambda i: i != "\\n", inputs))
    inputs = list(filter(lambda i: i != "", inputs))
    inputs = list(filter(lambda i: i != " ", inputs))
    return inputs



