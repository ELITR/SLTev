#!/usr/bin/env python

import argparse
import sys
import sacrebleu
import subprocess as sp
import os
from mosestokenizer import *
import uuid
import shutil
    
######################################################################
# file manipulation functions
######################################################################

def get_number_words(tt_list):
    """
    Recived a tt sentences and calculate number of words.
    
    :param tt_list: a list of tt (OSt) sentences
    :return count: the count of all words 
    """
    count = 0
    for i in tt_list:
        count += (len(i)-1)

    return count
 
def read_tt(file_name):
    """
    Reading the input tt file  
    
    :param file_name: path of the tt file 
    :return  reference: a list of sentences that split by space like as [['i', 'am', '.'], ['you', 'are', '.'] ]
    """
    
    tokenize = MosesTokenizer()
    reference = list()
    with open(file_name, 'r', encoding="utf8") as in_file:
        line = in_file.readline()
        while line:
            l = tokenize(line.strip())
            l.append('.')
            reference.append(l)
            line = in_file.readline()
    reference = list(filter(lambda a: a != [], reference))
    return reference

def read_ostt(file_name):
    """
    Reading *.OStt (time-stamped transcript) file 
    
    :param file_name: the path of ostt file 
    :return ASR: a list of sentences which each sentence split to many segments. 
    Note: in each line in the input file, only we have end and start times (P/C start-time end-time). (e.g. P 1448 1599 How) 
    """
    
    ASR = list()
    sentence = []
    tokenize = MosesTokenizer()
    with open(file_name, 'r', encoding="utf8") as in_file:
        line = in_file.readline()
        while line:
            if 'P ' in line[:3]:
                l = tokenize(line.strip())[1:]
                l.append('.')
                sentence.append(l)
            else:
                l = tokenize(line.strip())[1:]
                l.append('.')
                sentence.append(l)
                ASR.append(sentence)
                sentence = []
            line = in_file.readline()
    ASR = list(filter(lambda a: a != [['.']], ASR))       
    return ASR

def read_ost_as_ostt(file_name):
    """
    Reading *.OSt file as OStt file
    
    :param file_name: the path of ost file 
    :return ASR: a list of sentences which each sentence split to many segments. 
    Note: in each line in the input file, only we have end and start times (P/C start-time end-time). (e.g. P 1448 1599 How) 
    """
    
    ASR = list()
    sentence = []
    tokenize = MosesTokenizer()
    with open(file_name, 'r', encoding="utf8") as in_file:
        line = in_file.readline()        
        while line:
            l = [0,0]
            l += tokenize(line.strip())
            l.append('.')
            ASR.append([l])
            line = in_file.readline()
    ASR = list(filter(lambda a: a != [['.']], ASR))       
    return ASR

def read_MT(file_name, asr_status=False):
    """
    Reading MT file and saving sentences in a list (each sentence contains many segments that split by space)
    
    :param file_name: the path of MT/SLT files
    :return MT: a list of sentences which each sentence splits to some segments. 
    """
    
    MT = list()
    sentence = []
    tokenize = MosesTokenizer()
    with open(file_name, 'r', encoding="utf8") as in_file:
        line = in_file.readline()
        while line:
            line = tokenize(line.strip())               
            if 'P' == line[0]:
                l = line[1:]
                l.append('.')
                sentence.append(l)
            else:
                l = line[1:]
                l.append('.')
                sentence.append(l)
                MT.append(sentence)
                sentence = []
            line = in_file.readline()
    MT = list(filter(lambda a: a != [['.']], MT))
    return MT



def read_alignment_file(in_file):
    """"
    Receiving alignment file path as the input and a dictionary that indicates matched word in ASR (time-stamped transcript) and reference has been returned per each sentence.
    
    :param in_file: path of the align file
    :return out: a list of dictionary, e.g of output ([..., {'NULL': [], 'middle': ['1', '2', '4'], 'shelf': ['3', '5', '6', '7']}, ...])    
    """

    in_file = open(in_file,  'r', encoding="utf8")
    sentences = []
    line = in_file.readline()
    sentence = []
    while line:
        line = line.strip().split(' ')
        if '#' in line:
            sentences.append(sentence)
            sentence = []
        else:
            sentence.append(line)
        line = in_file.readline()
    sentences.append(sentence)
    sentences = sentences[1:]
    orders = []
    for i in sentences:
        sentence = i[1]
        d = []
        l = []
        for j in sentence:
            if j == '})':
                l.remove('({')
                d.append(l)
                l = []
            else:
                l.append(j)
       
        orders.append(d)       
    out = []
    for i in orders:
        l = {}
        for j in i:
            try:
                l[j[0]] = j[1:]
            except:
                l[j[0]] = int(-1)
        out.append(l)       
    return out


def segmenter(MT, Ts, language, SLTev_home, temp_folder):
    """
    MT complete segments have been joined and saved in a temp_translate file.
    and temp_translate file has been segmented by mwerSegmenter. 
    
    :param Ts: a list of T tables 
    :param MT: a list of MT senetnces 
    :param language: the submision language. 
    :param SLTev_home: path of the mwerSegmenter folder
    :param temp_folder: path of the temp folder that created by UUID
    :return mt_sentences: a list of MT sentecess which segmented by the mwerSegmenter
    :return mWERQuality: the quality score of mwerSegmenter
    """
    
    mt_sentences = []
    for i in range(len(MT)):
        mt = MT[i][-1][3:-1]
        mt_sentences.append(mt)

    references_sentences = []

    for ref in Ts:
        l = []
        for sentennce in ref:
            s = []
            for k,v in sentennce.items():
                s.append(k)
            l.append(s)
        references_sentences.append(l)
    #------------------write MT in temp_translate file and reference in temp_ref
    temp_folder_name = temp_folder
    os.mkdir(temp_folder_name)
    os.chdir(temp_folder_name)
    out = open('temp_ref', 'w')
    for i in references_sentences[0]:
        sentence = ' '.join(i)
        out.write(sentence)
        out.write('\n')
    out.close()    
    out = open('temp_translate', 'w')   
    for i in mt_sentences:
        sentence = ' '.join(i)
        out.write(sentence)
        out.write('\n')
    out.close()
    #-------------tokenize tt and MT
    cmd = SLTev_home + "/mwerSegmenter -mref temp_ref -hypfile temp_translate"
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
    mt_sentences = segments[:]
    os.chdir('../')
    shutil.rmtree(temp_folder_name)
    return mt_sentences, mWERQuality
