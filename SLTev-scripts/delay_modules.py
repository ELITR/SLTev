#!/usr/bin/env python

import argparse
import sys
import nltk
import sacrebleu
import subprocess as sp
import os
from mosestokenizer import *
from files_modules import *


def get_Zero_T(ASR, reference):
    """
    Receiveing OStt (time-stamped transcript) sentences and reference sentences and calculate T matrix:
    which elements of T is a dictionary that key is one word of reference and value is the end time of the word.      
    To calculate the T matrix, first calculate the spent time of the Complete segment in the Ostt and this time is divided per number of equivalent sentence words in the reference.
    
    """
    Zero_T = []
    sentence_times = []
    start_times = []
    for sentence in ASR:

        sentence_time = float(sentence[-1][1]) - float(sentence[0][0])
        sentence_times.append(sentence_time)
        start_times.append(float(sentence[0][0]))
    
    for sentence in range(len(reference)):
        time_step = start_times[sentence] 
        step = sentence_times[sentence]/ len(reference[sentence][:-1])
        #l = {"##mean_delay##":(time_step/2)}
        l = dict()
        for word in reference[sentence][:-1]:
            time_step = time_step + step
            l[word] = time_step
            
        
        Zero_T.append(l)
    return Zero_T




def segemtWordsTimes(segment):
    """
    getting a segment and for each word calcuate word ending time 
    """
    out = {}
    duration = float(segment[1]) - float(segment[0])
    step = duration/len(segment[2:-1])
    count = 1
    for word in segment[2:-1]:
        if word not in out.keys():
            out[word] = float(segment[0]) + count*step
        count += 1
    return out
    
def makeAlignDict(align, ref):
    
    """
    making alignment between source and refernce by align file. in the output each word of reference (tt) match to the word
    of source (OStt)
    """
    out = {}
    for k,v in align.items():
        for i in v:
            out[ref[:-1][int(i)-1]] = k
            
    return out


def get_One_T(OStt, reference, aligns = None):
    """
    Receiving OStt (time-stamped transcript), tt sentences and the alignment (giza sentence orders) and
    finally calculated T matrix. Each row of T is a dictionary which key is one word of reference line and the value is the end time of that word. 
    To calculate T matrix, 
     
    """
    T = []
    for index in range(len(OStt)):
        sentence = OStt[index]
        s_time = {}
        just_times = [0]
        just_words = []
        for i in sentence:
            segment_words_time = segemtWordsTimes(i)
            for k,v in segment_words_time.items():
                if k in sentence[-1][2:-1] and k not in s_time.keys():
                    s_time[k] = v
                    just_times.append(v)
        just_times.append(0)
        #---------assign time in OStt words (source) to the tt words

        ref_T = {}
        count = 1
        for i in reference[index][:-1]:
            if i in ref_T.keys():
                continue
            p = float(len(just_times)-2)/len(set(reference[index][:-1])) * count

            t = just_times[int(p)] + ((just_times[int(p)+1] - just_times[int(p)])*(p-int(p)))
            ref_T[i] = t
            count += 1
            just_words.append(i)

        #---------------using align file
        if aligns != None:
            max_value = 0
            align_dict =  makeAlignDict(aligns[index], reference[index])
            for i in just_words:
                try:
                    ref_T[i] = max([ref_T[i], max_value, s_time[align_dict[i]]])
                except:
                    ref_T[i] = max([ref_T[i], max_value ])
                if max_value < ref_T[i]:
                    max_value = ref_T[i]
        T.append(ref_T)
    return T
            

    
def build_A_Time_Based(sentence_segments):
    """

    Receiving segments of the mt sentences and calculates A dictionary:
    A is a dictionary which key is one word of MT sentence and value is the show time of the
    word.

    """
    uniq_words_show_time = {}
    uniq_words_estimate_time = {} 
    for segment in sentence_segments:
        words = segment[3:-1] 
        step = (float(segment[2])-float(segment[1]))/len(words)
        for word in segment[3:-1]:
            if word not in uniq_words_show_time.keys() and word in sentence_segments[-1][3:-1]:
                uniq_words_show_time[word] = float(segment[0])
                uniq_words_estimate_time[word] = float(float(segment[1]) + ((words.index(word)+1)*step))
    start = sentence_segments[-1][1]
    end = sentence_segments[-1][2]
    return uniq_words_show_time, uniq_words_estimate_time


    
def extractMatchWords_basedOnTime(estimat_times, display_times, start, end):
    """
    extract all words in MT which have estimation time in range start and end (start and end extracted in OStt). 
    
    """
    out = {}
    min_v = 1000000000
    max_v = -1
    #--------extract words between start and end 
    for i in range(len(estimat_times)):
        for k,v in estimat_times[i].items():
            if v <= end and v >= start:
                out[k] = display_times[i][k]
                if v < min_v:
                    min_v = v
                if v > max_v:
                    max_v = v
    #------ add one extra words in two side
    min_list = []
    max_list = []
    for i in range(len(estimat_times)):
        for k,v in estimat_times[i].items():
            if v < min_v:
                min_list.append([v, k, display_times[i][k]])
            if v > max_v:
                max_list.append([v, k, display_times[i][k]])
    if min_list != []:
        min_list.sort()
        out[min_list[-1][1]] = min_list[-1][2]
    if max_list != []:
        max_list.sort()
        out[max_list[0][1]] = max_list[0][2]       
    return out

def get_delay (T, match_words):
    """
    calculating delay between T table and match words  
    """
    miss_word = 0
    delay = 0
    for k,v in T.items():
        try:
            d = float(match_words[k]) - v
            if d > 0:
                delay += d
        except:
            miss_word += 1
    return miss_word, delay
            
def evaluate(Ts, MT, OStt):
    """
    calcuting delay and mission words
    """
    sum_delay = 0
    sum_missing_words = 0
    mt_words= []
    display_times = []
    estimat_times = []
    for i in range(len(MT)):
        display_T, estimat_T = build_A_Time_Based(MT[i])
        display_times.append(display_T)
        estimat_times.append(estimat_T)
    
    for j in range(len(OStt)):
        start = float(OStt[j][-1][0])
        end = float(OStt[j][-1][1])
        match_words = extractMatchWords_basedOnTime (estimat_times, display_times, start, end)
        temp_list = []
        for T in Ts:
            miss, delay = get_delay(T[j], match_words)
            temp_list.append([delay, miss])
        temp_list.sort()
        sum_missing_words += temp_list[0][1]
        sum_delay += temp_list[0][0]
    return sum_delay, sum_missing_words



def build_segmenter_A(MT):
    """

    In this function, for each MT segment 'A' matrix has been built.
    The output is a big list as mt sentences words which each element of it is as [word, display_time[word]].
  
    """
    A_list = []
    for sentence_segments in MT:
        #------------------bulild A for each segment ----------
        uniq_words_start_time = {}
        for segment in sentence_segments:
            for word in segment[3:-1]:
                if word not in uniq_words_start_time.keys():
                    uniq_words_start_time[word] = int(segment[0])


        #----------------convert A to a list according to Complete segments----------
        out = []
        for word in sentence_segments[-1][3:-1]:
            out.append([word, uniq_words_start_time[word]])
        A_list.append(out)
        
    #--------------convert all element of A_list in a list (convert 2-D to 1-D array)
    out = []
    for i in A_list:
        out += i
    return out

def time_segmenter(segmenter_sentence, A_list, MovedWords):
    """

    This function indicates each segment in segmenter_sentence contains which segments in MT.
    This function get output of build_segmenter_A() and a list of sentences which is output of segmenter() function and a integer number as MovedWords (indicate move number to left and write (default is 1))
    
    """
    segment_times = list()
    start = 0 
    for i in range(len(segmenter_sentence)):
        
        segment = segmenter_sentence[i]
        
        end = start + len(segment)
    
        temp = A_list[start:end]
        try:
            write_moved = A_list[end:(end + MovedWords)]
        except:
            write_moved = []
        try:
            left_moved = A_list[(start-MovedWords):end]
        except:
            left_moved = []
        
        temp =  left_moved + temp + write_moved
        start = end
     
        #------convert each segment to dictionary-------
        temp1 = dict()
        for i in temp:
            temp1[i[0]] = i[1]
        segment_times.append(temp1)
      
    return segment_times

def evaluate_segmenter(Ts, MT, MovedWords, language, SLTev_home):
    """

    Receiving Ts and MT and calculates the delay time based on the mwersegmenter.
    First calculating segmenter_sentence, A_list by segmenter() and build_segmenter_A() functions and then build times table with time_segmenter() function, and calculate delay sentence by sentence in T and times. 

    """
    A_list = build_segmenter_A(MT)
    segmenter_sentence, mWERQuality = segmenter(MT, Ts, language, SLTev_home)
    segment_times = time_segmenter(segmenter_sentence, A_list, MovedWords)
   
    sum_delay = 0
    sum_missing_words = 0
    for i in range(len(Ts[0])):
        temp_list = []
        for T in Ts:
            miss, delay = get_delay(T[i], segment_times[i])
            temp_list.append([delay, miss])
        temp_list.sort()
        sum_missing_words += temp_list[0][1]
        sum_delay += temp_list[0][0]
            
    return sum_delay, sum_missing_words, mWERQuality
