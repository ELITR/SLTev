#!/usr/bin/env python

import subprocess as sp
import os
from sacremoses import MosesTokenizer
import shutil


def read_reference_file(file_name):
    """
    Reading the input reference file

    :param file_name: path of the reference file
    :return  reference_lines: a list of sentences that tokenized by Moses tokenizer. For example [['i', 'am', '.'], ['you', 'are', '.'] ]
    """

    tokenize = MosesTokenizer().tokenize
    reference_lines = list()
    with open(file_name, "r", encoding="utf8") as in_file:
        line = in_file.readline()
        while line:
            token_line = tokenize(line.strip())
            if token_line == []:
                line = in_file.readline()
                continue
            token_line.append(".")
            reference_lines.append(token_line)
            line = in_file.readline()
    reference_lines = list(filter(lambda a: a != ["."], reference_lines))
    return reference_lines


def read_ostt_file(file_name):
    """
    Reading OStt (time-stamped transcript) file

    :param file_name: the path of ostt file
    :return ostt_sentences: a list of sentences which each sentence split to many segments (a complete segment and multiple partial segments).
    Note: in each line in the input file, only we have "end" and "start" times (P/C start-time end-time). (e.g. P 1448 1599 How)
    """

    ostt_sentences = list()
    tokenize = MosesTokenizer().tokenize
    with open(file_name, "r", encoding="utf8") as in_file:
        line = in_file.readline()
        sentence = []
        while line:
            if tokenize(line.strip()) == []:
                line = in_file.readline()
                continue
            if "P " in line[:3]:
                l = tokenize(line.strip())[1:]
                l.append(".")
                sentence.append(l)
            else:
                l = tokenize(line.strip())[1:]
                l.append(".")
                sentence.append(l)
                ostt_sentences.append(sentence)
                sentence = []
            line = in_file.readline()
    ostt_sentences = list(filter(lambda a: a != [["."]], ostt_sentences))
    return ostt_sentences


def read_candidate_file(file_name):
    """
    Reading ASRT and SLT files and saving sentences in a list (each sentence contains many segments that tokenized by Moses tokenizer)

    :param file_name: the path of MT/SLT files
    :return candidate_sentences: a list of sentences which each sentence splits to some segments.
    """

    candidate_sentences = list()
    sentence = []
    tokenize = MosesTokenizer().tokenize
    with open(file_name, "r", encoding="utf8") as in_file:
        line = in_file.readline()
        while line:
            line = tokenize(line.strip())
            if line == []:
                line = in_file.readline()
                continue
            if "P" == line[0]:
                l = line[1:]
                l.append(".")
                sentence.append(l)
            elif "C" == line[0]:
                l = line[1:]
                l.append(".")
                sentence.append(l)
                candidate_sentences.append(sentence)
                sentence = []
            else:
                l = [0, 0, 0]
                l += line[:]
                l.append(".")
                sentence.append(l)
                candidate_sentences.append(sentence)
                sentence = []
            line = in_file.readline()
    candidate_sentences = list(filter(lambda a: a != [["."]], candidate_sentences))
    return candidate_sentences


def read_alignment_file(align_file_path):
    """ "
    Receiving alignment file path as the input and a dictionary that indicates matched token in ostt (time-stamped transcript) and reference has been returned per each sentence.

    :param align_file_path: path of the align file
    :return align_table: a list of dictionary, e.g of output ([..., {'NULL': [], 'middle': ['1', '2', '4'], 'shelf': ['3', '5', '6', '7']}, ...])
    """
    sentences = []
    with  open(align_file_path, "r", encoding="utf8") as in_file:
        line = in_file.readline()
        sentence = []
        while line:
            line = line.strip().split(" ")
            if line == []:
                line = in_file.readline()
                continue
            if "#" in line:
                sentences.append(sentence)
                sentence = []
            else:
                sentence.append(line)
            line = in_file.readline()
        sentences.append(sentence)
        sentences = sentences[1:]
    
    order_numbers = []
    for item in sentences:
        sentence = item[1]
        d = []
        l = []
        for j in sentence:
            if j == "})":
                l.remove("({")
                d.append(l)
                l = []
            else:
                l.append(j)

        order_numbers.append(d)
    
    align_table = []
    for i in order_numbers:
        l = {}
        for j in i:
            try:
                l[j[0]] = j[1:]
            except:
                l[j[0]] = int(-1)
        align_table.append(l)
    return align_table


def delay_segmenter(evaluation_object, temp_folder):
    """
    slt complete segments have been joined and saved in the temp_translate file.
    and temp_translate file has been segmented by mwerSegmenter.

    :param evaluation_object: a dictionary of evaluation key, values
    :param temp_folder: path of the temp folder that created by UUID
    :return mwer_candidate_sentences: a list of slt sentecess which segmented by the mwerSegmenter
    :return mWERQuality: the quality score of mwerSegmenter
    """

    complete_candidate_sentences = []
    for i in range(len(evaluation_object.get('candidate_sentences'))):
        mt = evaluation_object.get('candidate_sentences')[i][-1][3:-1]
        complete_candidate_sentences.append(mt)

    references_sentences = []
    for ref in evaluation_object.get('Ts'):
        l = []
        for sentennce in ref:
            s = []
            for k, v in sentennce.items():
                s.append(k)
            l.append(s)
        references_sentences.append(l)
    # write complete_candidate_sentences in temp_translate file and reference in temp_ref
    temp_folder_name = temp_folder
    os.mkdir(temp_folder_name)
    os.chdir(temp_folder_name)
    out = open("temp_ref", "w")
    for i in references_sentences[0]:
        sentence = " ".join(i)
        out.write(sentence)
        out.write("\n")
    out.close()
    out = open("temp_translate", "w")
    for complete_sentence in complete_candidate_sentences:
        sentence = " ".join(complete_sentence)
        out.write(sentence)
        out.write("\n")
    out.close()
    # tokenize candidate and reference
    cmd = evaluation_object.get('SLTev_home') + "/mwerSegmenter -mref temp_ref -hypfile temp_translate"
    mWERQuality = sp.getoutput(cmd)
    mWERQuality = mWERQuality.split(" ")[-1]
    mWERQuality = float(mWERQuality)
    # read __segments file
    in_file = open("__segments", "r", encoding="utf8")
    line = in_file.readline()
    segments = []
    while line:
        segments.append(line.strip().split(" "))
        line = in_file.readline()

    mwer_candidate_sentences = segments[:]
    os.chdir("..")
    shutil.rmtree(temp_folder_name)
    return mwer_candidate_sentences, mWERQuality


def quality_segmenter(evaluation_object, temp_folder):
    """
    candidate complete segments have been joined and saved in a temp_translate file.
    and temp_translate file has been segmented by mwerSegmenter.

    :param evaluation_object: a dictionary of evaluation key, values
    :param temp_folder: path of the temp folder that created by UUID
    :return mt_sentences: a list of MT sentecess which segmented by the mwerSegmenter
    :return mWERQuality: the quality score of mwerSegmenter
    """

    candidate_sentences = []
    for i in range(len(evaluation_object.get('candidate_sentences'))):
        candidate = evaluation_object.get('candidate_sentences')[i][-1][3:-1]
        candidate_sentences.append(candidate)

    reference_sentences = []
    for ref in evaluation_object.get('references')[0]:
        reference_sentences.append(ref[:-1])
    # write candaiate in temp_translate file and reference in temp_ref
    os.mkdir(temp_folder)
    os.chdir(temp_folder)
    out = open("temp_ref", "w")
    for i in reference_sentences:
        sentence = " ".join(i)
        out.write(sentence)
        out.write("\n")
    out.close()
    out = open("temp_translate", "w")
    for i in candidate_sentences:
        sentence = " ".join(i)
        out.write(sentence)
        out.write("\n")
    out.close()
    # tokenize reference and candidate
    cmd = evaluation_object.get('SLTev_home') + "/mwerSegmenter -mref temp_ref -hypfile temp_translate"
    mWERQuality = sp.getoutput(cmd)
    mWERQuality = mWERQuality.split(" ")[-1]
    mWERQuality = float(mWERQuality)
    # read segments for __segments file (output of mwerSegmenter)
    in_file = open("__segments", "r", encoding="utf8")
    line = in_file.readline()
    candidate_segments = []
    while line:
        candidate_segments.append(line.strip().split(" "))
        line = in_file.readline()

    os.chdir("..")
    shutil.rmtree(temp_folder)
    return candidate_segments, mWERQuality

