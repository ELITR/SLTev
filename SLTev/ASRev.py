#!/usr/bin/env python
from jiwer import wer
import string 
import re
import subprocess as sp
from mosestokenizer import *
import argparse
import sys
import os
import uuid
import shutil

def text_preprocessing(text):
    """
    
    preprocessing output text
    
    """
    
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    text = re.sub(' +', ' ', text)
    return text

def read_asr(file_name):
    """

    Read asr file 
    Input: the path of the ASR file 
    Out_put: a list of sentences which each sentence split to many segments. 
    in OStt and ASR file only we want C segments. 

    """
  
    sentences = []
    tokenize = MosesTokenizer()
    with open(file_name, 'r', encoding="utf8") as in_file:
        line = in_file.readline()
        while line:
            line = tokenize(line.strip())
            if line == []:
                continue
#             line = convert_to_asr_format(line) #--convert to asr format
            if line[0] != 'P' and line[0] != 'C':
                sentences.append(line)
                
            elif 'C' == line[0]:
                l = line[4:]
                sentences.append(l)


            line = in_file.readline()
    sentences = list(filter(lambda a: a != [], sentences))
    return sentences

def read_ostt(file_name):
    """

    Read OStt or tt file 
    Input: the path of OStt or tt or ASR file 
    Out_put: a list of sentences which each sentence split to many segments. 
    in OStt and ASR file only we want C segments. 

    """
  
    sentences = []
    tokenize = MosesTokenizer()
    with open(file_name, 'r', encoding="utf8") as in_file:
        line = in_file.readline()
        while line:
            line = tokenize(line.strip())
#             line = line.strip().split()
            if line[0] != 'P' and line[0] != 'C':
                sentences.append(line)
                
            elif 'C' == line[0]:
                l = line[3:]
                sentences.append(l)


            line = in_file.readline()
    sentences = list(filter(lambda a: a != [], sentences))
    return sentences


def wer_evaluate(ostt, asr):
    """
    STEPS:
    
    1- conver ostt and asr to a string.  
    2- run preprocessing over them 
    3- run wer over them. 
    
    """
    
    #----------convert ostt to a string
    ostt_string = ''
    detokenize = MosesDetokenizer()
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

def use_mversegmentor(ostt, asr, SLTev_home):
    """
    STEPS:
    
    1- save osst and asr sentences in temp_ref and temp_translate
    2- run mversegmnter and extract sentences in __segment file
    3- run preprocessing over ostt 
    4- run wer over them. 
    
    """
    
    #---------save osst and asr sentences in temp_ref and temp_translate
    temp_folder_name = "./" + str(uuid.uuid4())
    os.mkdir(temp_folder_name)
    os.chdir(temp_folder_name)
    out = open('temp_ref', 'w')
    for i in ostt:
        sentence = ' '.join(i)
        out.write(sentence)
        out.write('\n')
    out.close()
    
    out = open('temp_translate', 'w')
    
    #print('asr ', asr)    
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
    line = in_file.readline()
    segments = [] 
    detokenize = MosesDetokenizer()
    while line:
        segments.append(line.strip().split(' '))
        line = in_file.readline()
        
    asr = segments[:]
    os.chdir('../')
    shutil.rmtree(temp_folder_name)
    
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


def use_moses_mversegmentor(ostt, asr, SLTev_home):
    """
    STEPS:
    
    1- save osst and asr sentences in temp_ref and temp_translate
    2- run mversegmnter and extract sentences in __segment file
    3- run moses tokeniazer over ostt 
    4- run wer over them. 
    
    """
    
    #---------save osst and asr sentences in temp_ref and temp_translate
    temp_folder_name = "./" + str(uuid.uuid4())
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
    #------------run segmentation 
    #--------------run mversegmnter and extract sentences in __segment file
    #-------------tokenize tt and MT
    cmd = SLTev_home + "/mwerSegmenter -mref " + "temp_ref" +" -hypfile "+ "temp_translate"
    mWERQuality = sp.getoutput(cmd)
    
    mWERQuality = mWERQuality.split(' ')[-1]
    mWERQuality = float(mWERQuality)
    
    #-------------read segments 
    in_file = open('__segments', 'r', encoding="utf8")
    line = in_file.readline()
    segments = [] 
    while line:
        segments.append(line.strip().split(' '))
        line = in_file.readline()
        
    asr = segments[:]
    os.chdir('../')
    shutil.rmtree(temp_folder_name)
    # ------------------convert to text and preprocessing and run wer
    wer_scores = list()
    for i in range(len(ostt)):
        ostt_text = ' '.join(ostt[i])
#         ostt_text = tokenize(ostt_text)
#         ostt_text = ' '.join(ostt_text)
        
        asr_text = ' '.join(asr[i])
#         asr_text = tokenize(asr_text)
#         asr_text = ' '.join(asr_text)
        score = wer(ostt_text, asr_text)
        wer_scores.append(score)
    
    return sum(wer_scores)/len(wer_scores)



def ASRev(ost="", asr="", SLTev_home="./", simple="False"):

    """
    This function receives two files OSt and ASR, and calculates the WER score.
    
    """


    ostt_file = ost


    asr_file = asr

    ostt = read_ostt(ostt_file)
    asr = read_asr(asr_file)
    current_path = os.getcwd()

    #----------
    if simple == 'False':
        print("-------------------------------------------------------------")

        print('n ... not considering, not using')
        print('P ... preprocessing contains Lowercase, punctuation removing')
        print('C ... concatenating all sentences')
        print('W ... using mwersegmemter')
        print('M ... using Moses tokenizer')
        print("-------------------------------------------------------------")

    #-----------
    language = 'en'

    if simple == 'False':
        score = wer_evaluate(ostt, asr)
        print('PCnn ', str("{0:.3f}".format(round(score, 3)))  )

    try:
        score = use_mversegmentor(ostt, asr, SLTev_home)
        print('PnWn ', str("{0:.3f}".format(round(score, 3)))  )
    except:
        os.chdir(current_path)
    try:
        if simple == 'False':
            score = use_moses_mversegmentor(ostt, asr, SLTev_home)
            print('nnWM ', str("{0:.3f}".format(round(score, 3)))  )
    except:
        os.chdir(current_path)


