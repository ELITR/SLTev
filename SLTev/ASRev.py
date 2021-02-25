#!/usr/bin/env python
from jiwer import wer
import string 
import re
import subprocess as sp
from sacremoses import MosesTokenizer, MosesDetokenizer
import os
import uuid
import shutil
from utilities import *

######################################################################
# WER score functions
######################################################################


def text_preprocessing(text):
    """
    preprocessing input text, contains lowecaseing and removing punctuations
    
    :param text: the input text
    :retun text: the preprocessed text
    """
    
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    text = re.sub(' +', ' ', text)
    return text

def read_asr_for_wer(file_name):
    """
    Read asr file 
    Input: the path of the ASR file 
    Out_put: a list of sentences which each sentence split to many segments. 
    in OStt and ASR file only we want C segments. 
    
    :param file_name: the input ASR file path
    :return sentences: the ASR sentences without time-stamps (just compelet segments ) 
    """
    
    sentences = []
    tokenize = MosesTokenizer().tokenize
    with open(file_name, 'r', encoding="utf8") as in_file:
        line = in_file.readline()
        while line:
            line = tokenize(line.strip())
            if line == []:
                line = in_file.readline()
                continue
                
            if line[0] != 'P' and line[0] != 'C':
                sentences.append(line)
                
            elif 'C' == line[0]:
                l = line[4:]
                sentences.append(l)
            line = in_file.readline()
    sentences = list(filter(lambda a: a != [], sentences))
    return sentences

def read_ostt_for_wer(file_name):
    """
    Read OStt or tt file 
    Input: the path of OStt or tt or ASR file 
    Out_put: a list of sentences which each sentence split to many segments. 
    in OStt and ASR file only we want C segments. 
    
    :param file_name: the input OStt or OSt file path
    :return sentences: the OStt(OSt) sentences without time-stamps (just compelet segments ) 
    """
    
    sentences = []
    tokenize = MosesTokenizer().tokenize
    with open(file_name, 'r', encoding="utf8") as in_file:
        line = in_file.readline()
        while line:
            line = tokenize(line.strip())
            if line == []:
                line = in_file.readline()
                continue
            if line[0] != 'P' and line[0] != 'C':
                sentences.append(line)
            elif 'C' == line[0]:
                l = line[3:]
                sentences.append(l)
            line = in_file.readline()
    sentences = list(filter(lambda a: a != [], sentences))
    return sentences

def wer_evaluation (ostt, asr):
    """
    STEPS:
    1- conver ostt and asr to a string.  
    2- run preprocessing over them 
    3- run wer over them. 
    
    :param ostt: the list of OSt(OStt) sentences
    :param asr: the list of asr sentences
    :return: Return a WER score
    """
    
    #----------convert ostt to a string
    ostt_string = ''
    detokenize = MosesDetokenizer().detokenize
    for i in ostt:
        ostt_string += ' '
        ostt_string += detokenize(i) 
    #----------convert asr to a string
    asr_string = ''
    for i in asr:
        asr_string += ' '
        asr_string += detokenize(i)   
    #--------preprocessing 
    asr_string = text_preprocessing(asr_string)
    ostt_string = text_preprocessing(ostt_string)
    #-------run wer 
    return wer(ostt_string, asr_string)


def segmentation_by_mwersegmenter(ostt, asr, SLTev_home, temp_folder):
    """
    doing segmentation by mwersegmenter tool
    
    :param ostt: the list of OSt(OStt) sentences
    :param asr: the list of asr sentences
    :param SLTev_home: path oof the SLTev files (/path/to/mwerSegmenter)
    :param temp_folder: name of tem folder that created by UUID
    :return segments: a list of ASR sentences segmented by mwerSegmenter
    :return mWERQuality: the quality score of mwerSegmenter   
    """
    
    #---------save osst and asr sentences in temp_ref and temp_translate
    temp_folder_name = temp_folder
    os.mkdir(temp_folder_name)
    os.chdir(temp_folder_name)
    out = open('temp_ref', 'w')
    for i in ostt:
        sentence = ' '.join(i)
        out.write(sentence)
        out.write('\n')
    out.close()
    out = open('temp_translate', 'w')   
    for i in asr:
        sentence = ' '.join(i[:])
        out.write(sentence)
        out.write('\n')
    out.close()
    #--------------run mversegmnter and extract sentences in __segment file
    #-------------tokenize tt and MT
    cmd = SLTev_home + "/mwerSegmenter -mref " + "temp_ref" +" -hypfile "+ "temp_translate"
    mWERQuality = sp.getoutput(cmd)
    mWERQuality = mWERQuality.split(' ')[-1]
    mWERQuality = float(mWERQuality)    
    #-------------read segments 
    in_file = open('__segments', 'r', encoding="utf8")
    lines = in_file.readlines()
    segments = []
    for line in lines:
        segments.append(line.strip().split(' '))
    os.chdir('..')
    shutil.rmtree(temp_folder_name)
    return segments, mWERQuality

def WER_by_mwersegmenter(ostt, asr, SLTev_home, temp_folder):
    """ 
    Calculating WER score without Mosses-tokenizer and with preprocessing
    For each segment obtained from the mwersegmenter segmentation, the WER score is calculated and finally, the average is taken. 
    
    :param ostt: the list of OSt(OStt) sentences
    :param asr: the list of asr sentences
    :param SLTev_home: path oof the SLTev files (/path/to/mwerSegmenter)
    :param temp_folder: name of tem folder that created by UUID
    :return: Return a WER score
    """
    segments, mWERQuality = segmentation_by_mwersegmenter(ostt, asr, SLTev_home, temp_folder)
    detokenize = MosesDetokenizer().detokenize
    asr = segments[:]
    # ------------------convert to text and preprocessing and run wer
    wer_scores = list()
    for i in range(len(ostt)):
        ostt_text = detokenize(ostt[i])
        ostt_text = text_preprocessing(ostt_text)
        
        asr_text = detokenize(asr[i])
        asr_text = text_preprocessing(asr_text)
        score = wer(ostt_text, asr_text)
        wer_scores.append(score)
    return sum(wer_scores)/len(wer_scores)

def WER_by_moses_mwersegmenter(ostt, asr, SLTev_home, temp_folder):
    """  
    Calculating WER score with Mosses-tokenizer and without preprocessing
    For each segment obtained from the mwersegmenter segmentation, the WER score is calculated and finally, the average is taken.  
    
    :param ostt: the list of OSt(OStt) sentences
    :param asr: the list of asr sentences
    :param SLTev_home: path oof the SLTev files (/path/to/mwerSegmenter)
    :param temp_folder: name of tem folder that created by UUID
    :return: Return a WER score
    """
    
    segments, mWERQuality = segmentation_by_mwersegmenter(ostt, asr, SLTev_home, temp_folder)
    asr = segments[:]
    # ------------------convert to text and preprocessing and run wer
    wer_scores = list()
    for i in range(len(ostt)):
        ostt_text = ' '.join(ostt[i])
        asr_text = ' '.join(asr[i])
        score = wer(ostt_text, asr_text)
        wer_scores.append(score)
    return sum(wer_scores)/len(wer_scores)

def ASRev(ost="", asr="", SLTev_home=".", simple="False"):
    """
    This function receives two files OSt and ASR, and calculates the WER score.
    
    :param ost: path of the OSt(OStt) file
    :param asr: path of the ASR file
    :param simple: a binary value for types of representing the results ("False" or "True")
    :param SLTev_home: path oof the SLTev files (/path/to/mwerSegmenter)
    :print: the various types of WER scores
    """
    
    ostt_file = ost
    asr_file = asr
    ostt = read_ostt_for_wer(ostt_file)
    asr = read_asr_for_wer(asr_file)
    current_path = os.getcwd()
    if simple == 'False':
        eprint("-------------------------------------------------------------")
        eprint('L ... lowercasing')
        eprint('P ... removing punctuation')
        eprint('C ... concatenating all sentences')
        eprint('W ... using mwersegmemter')
        eprint('M ... using Moses tokenizer')
        eprint("-------------------------------------------------------------")
    #-----------
    if simple == 'False':
        score = wer_evaluation(ostt, asr)
        print('LPC   ', str("{0:.3f}".format(round(score, 3)))  )
    try:
        temp_folder = os.path.join(".", str(uuid.uuid4()))
        score = WER_by_mwersegmenter(ostt, asr, SLTev_home, temp_folder)
        print('LPW   ', str("{0:.3f}".format(round(score, 3)))  )
    except:
        os.chdir(current_path)
        shutil.rmtree(temp_folder, ignore_errors=True)
    try:
        if simple == 'False':
            temp_folder = os.path.join(".", str(uuid.uuid4()))
            score = WER_by_moses_mwersegmenter(ostt, asr, SLTev_home, temp_folder)
            print('WM    ', str("{0:.3f}".format(round(score, 3)))  )
    except:
        os.chdir(current_path)
        shutil.rmtree(temp_folder, ignore_errors=True)

