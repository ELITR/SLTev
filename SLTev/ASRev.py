#!/usr/bin/env python
from jiwer import wer
import string
import re
import subprocess as sp
from sacremoses import MosesTokenizer, MosesDetokenizer
import os
import uuid
import shutil
from utilities import eprint, mwerSegmenter_error_message


def print_headers():
    eprint("-------------------------------------------------------------")
    eprint("L ... lowercasing")
    eprint("P ... removing punctuation")
    eprint("C ... concatenating all sentences")
    eprint("W ... using mwersegmemter")
    eprint("M ... using Moses tokenizer")
    eprint("-------------------------------------------------------------")


def text_preprocessing(text):
    text = text.lower().translate(str.maketrans("", "", string.punctuation))
    text = re.sub(" +", " ", text)
    return text


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


def docs_as_whole_evaluation(ost_sentences, asr_sentences):
    # concatenate ost_sentences to a document
    ost_concatenate_string = ""
    detokenize = MosesDetokenizer().detokenize
    for i in ost_sentences:
        ost_concatenate_string += " "
        ost_concatenate_string += detokenize(i)
    # concatenate asr_sentences to a document
    asr_concatenate_string = ""
    for i in asr_sentences:
        asr_concatenate_string += " "
        asr_concatenate_string += detokenize(i)

    asr_concatenate_string = text_preprocessing(asr_concatenate_string)
    ost_concatenate_string = text_preprocessing(ost_concatenate_string)

    return wer(ost_concatenate_string, asr_concatenate_string)


def segmentation_by_mwersegmenter(evaluation_object, temp_folder):
    # save ost and asr sentences in temp_ref and temp_translate files
    os.mkdir(temp_folder)
    os.chdir(temp_folder)
    out = open("temp_ref", "w")
    for i in evaluation_object.get('ost_sentences'):
        sentence = " ".join(i)
        out.write(sentence)
        out.write("\n")
    out.close()

    out = open("temp_translate", "w")
    for i in evaluation_object.get('asr_sentences'):
        sentence = " ".join(i[:])
        out.write(sentence)
        out.write("\n")
    out.close()

    cmd = (
        evaluation_object.get('SLTev_home') 
        + "/mwerSegmenter -mref "
        + "temp_ref"
        + " -hypfile "
        + "temp_translate"
        )
    mWERQuality = sp.getoutput(cmd)
    mWERQuality = mWERQuality.split(" ")[-1]
    mWERQuality = float(mWERQuality)
    # read __segments (output of mwerSegmenter)
    in_file = open("__segments", "r", encoding="utf8")
    lines = in_file.readlines()

    segments = []
    for line in lines:
        segments.append(line.strip().split(" "))

    os.chdir("..")
    shutil.rmtree(temp_folder)
    return segments, mWERQuality


def WER_by_mwersegmenter_without_moses_tokenizer(evaluation_object, temp_folder):
    """
    Calculating WER score without Mosses tokenizer and with preprocessing
    For each segment obtained from the mwerSegmenter segmentation, the WER score is calculated and finally, the average is taken.

    :evaluation_object : an object of inputs 
    :param temp_folder: name of temp folder that created by UUID
    :return: Return a WER score
    """
    asr_segmented_sentences, _ = segmentation_by_mwersegmenter(evaluation_object, temp_folder)
    detokenize = MosesDetokenizer().detokenize

    wer_scores = list()
    ost_sentences = evaluation_object.get('ost_sentences')
    for i in range(len(ost_sentences)):
        ost_text = detokenize(ost_sentences[i])
        ost_text = text_preprocessing(ost_text)

        asr_text = detokenize(asr_segmented_sentences[i])
        asr_text = text_preprocessing(asr_text)

        score = wer(ost_text, asr_text)
        wer_scores.append(score)
    return sum(wer_scores) / len(wer_scores)


def WER_by_mwersegmenter_with_moses_tokenizer(evaluation_object, temp_folder):
    """
    Calculating WER score with Mosses-tokenizer and without preprocessing
    For each segment obtained from the mwersegmenter segmentation, the WER score is calculated and finally, the average is taken.

    :evaluation_object : an object of inputs 
    :param temp_folder: name of temp folder that created by UUID
    :return: Return a WER score
    """

    asr_segmented_sentences, _ = segmentation_by_mwersegmenter(evaluation_object, temp_folder)
    ost_sentences = evaluation_object.get('ost_sentences')
    wer_scores = list()
    for i in range(len(ost_sentences)):
        ostt_text = " ".join(ost_sentences[i])
        asr_text = " ".join(asr_segmented_sentences[i])
        score = wer(ostt_text, asr_text)
        wer_scores.append(score)
    return sum(wer_scores) / len(wer_scores)


def simple_asr_evaluation(inputs_object):
    ost_sentences = read_ost_asr_files(inputs_object.get('ost'))
    asr_sentences = read_ost_asr_files(inputs_object.get('asr'))

    evaluation_object = {
        'ost_sentences': ost_sentences,
        'asr_sentences': asr_sentences,
        'SLTev_home': inputs_object.get('SLTev_home')
        }
    current_path = os.getcwd()
    try:
        temp_folder = os.path.join(".", str(uuid.uuid4()))
        wer_score = WER_by_mwersegmenter_without_moses_tokenizer(evaluation_object, temp_folder)
        print("LPW   ", str("{0:.3f}".format(round(wer_score, 3))))
    except:
        os.chdir(current_path)
        shutil.rmtree(temp_folder, ignore_errors=True)
        mwerSegmenter_error_message()


def normal_asr_evaluation(inputs_object):
    print_headers()
    ost_sentences = read_ost_asr_files(inputs_object.get('ost'))
    asr_sentences = read_ost_asr_files(inputs_object.get('asr'))

    wer_score = docs_as_whole_evaluation(ost_sentences, asr_sentences)
    print("LPC   ", str("{0:.3f}".format(round(wer_score, 3))))

    evaluation_object = {
        'ost_sentences': ost_sentences,
        'asr_sentences': asr_sentences,
        'SLTev_home': inputs_object.get('SLTev_home')
        }
    current_path = os.getcwd()
    try:
        temp_folder = os.path.join(".", str(uuid.uuid4()))
        wer_score = WER_by_mwersegmenter_without_moses_tokenizer(evaluation_object, temp_folder)
        print("LPW   ", str("{0:.3f}".format(round(wer_score, 3))))
    except:
        os.chdir(current_path)
        shutil.rmtree(temp_folder, ignore_errors=True)
        mwerSegmenter_error_message()

    try:
        temp_folder = os.path.join(".", str(uuid.uuid4()))
        wer_score = WER_by_mwersegmenter_with_moses_tokenizer(evaluation_object, temp_folder)
        print("LPW   ", str("{0:.3f}".format(round(wer_score, 3))))
    except:
        os.chdir(current_path)
        shutil.rmtree(temp_folder, ignore_errors=True)
        mwerSegmenter_error_message()

