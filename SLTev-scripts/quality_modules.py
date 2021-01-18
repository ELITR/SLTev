#!/usr/bin/env python

import argparse
import sys
import nltk
import sacrebleu
import subprocess as sp
import os
from mosestokenizer import *
from files_modules import *


def calc_bleu_score_documnet(Ts, MT):
    """

    Calculating bleu score by using sacrebleu module. Input is the merge all of the sentences in MT and reference
    as a document.  
 
    """
    from nltk.translate.bleu_score import SmoothingFunction
    smoothie = SmoothingFunction().method4
    merge_mt_sentences = []

    for i in range(len(MT)):
        mt = MT[i][-1][3:-1]
        merge_mt_sentences += mt
    merge_references_sentences = []
    for i in Ts:
        l = []
        for j in i:
            for k,v in j.items():
                l.append(k)
        merge_references_sentences.append(' '.join(l))
    bleu_scores = []
    sacre_bleu_score = []
    

    refs= [[i]for i in merge_references_sentences]
    sys = [' '.join(merge_mt_sentences[:])]
    b_sacre = sacrebleu.corpus_bleu(sys, refs)
    nltk_score = nltk.translate.bleu_score.sentence_bleu([i[0].split() for i in refs], sys[0].split(), smoothing_function=smoothie)
    sacre_blue_score = b_sacre.score

    return nltk_score, sacre_blue_score


def calc_bleu_score_sentence_by_sentence(Ts, MT, language):
    """

    Calculating bleu score sentence by sentence with NLTK and sacrebleu modules.
    using Moses tokenizer befor using mwersegmenter
 
    """
    import nltk
    from nltk.translate.bleu_score import SmoothingFunction
    smoothie = SmoothingFunction().method4
   
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
        
    segmenter_sentence, mWERQuality = segmenter(MT, Ts, language)


    nltk_bleu = list()
    sacre_bleu = list()
    for i in range(len(references_sentences[0])):
        sys = [' '.join(segmenter_sentence[i])]
        refs = [ [' '.join(ref[i])] for ref in references_sentences]
#         print ('sys', sys)
#         print ('refs', refs)
        b_sacre = sacrebleu.corpus_bleu(sys, refs)
        nltk_score = nltk.translate.bleu_score.sentence_bleu([i[0].split() for i in refs], sys[0].split(), smoothing_function=smoothie)
        sacre_blue_score = b_sacre.score
        nltk_bleu.append(nltk_score)
        sacre_bleu.append(sacre_blue_score)
    
    
 

    return (sum(nltk_bleu)/len(nltk_bleu)), (sum(sacre_bleu)/len(sacre_bleu)), sum(nltk_bleu), sum(sacre_bleu)

def build_A_Time_Based_quality(sentence_segments):
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
    return uniq_words_estimate_time

def calc_bleu_score_sentence_by_time(Ts, MT, time_step):
    """

    Calculates blue score using the NLTK module with time slice strategy.

    """
    from nltk.translate.bleu_score import SmoothingFunction
    smoothie = SmoothingFunction().method4
    
    tail_number = float(MT[-1][-1][2])
    start = 0
    end = time_step
    mt_sentences = list()
    while start <= float(tail_number):
        l = []
        for i in range(len(MT)):
            estimat_word_times = build_A_Time_Based_quality(MT[i])
            for k,v in estimat_word_times.items():
                if v >= start and v <= end:
                    l.append(k)
        
        mt_sentences.append(l)
        start +=  time_step
        end += time_step
        
    references_sentences = list()
    start = 0
    end = time_step
    while start <=  float(tail_number):

        l = []
        for i in range(len(Ts)):
            s= []
            for sentence in Ts[i]:
                for k,v in sentence.items():
                    if v >= start and v <= end:
                        s.append(k)
            l.append(s)
        references_sentences.append(l)
        start +=  time_step
        end += time_step

#     print('references_sentences ', references_sentences)
#     print('mt_sentences', mt_sentences)
    blue_scores = []
    start = 0 
    end = time_step

    nltk_BLEU_list = []
    sacreBLEU_list = []
    
    for t in  range(len(mt_sentences)):
        
        sys = [' '.join(mt_sentences[t])]
        refs = [ [' '.join(ref)] for ref in references_sentences[t]]
#         print ('sys', sys)
#         print ('refs', refs)
        b_sacre = sacrebleu.corpus_bleu(sys, refs)
        nltk_score = nltk.translate.bleu_score.sentence_bleu([i[0].split() for i in refs], sys[0].split(), smoothing_function=smoothie)
        sacre_blue_score = b_sacre.score
   
        text = 'detailed BLEU          span-'+ format(start, '06') + '-' + format(end, '06') +  '     ' + str("{0:.3f}".format(nltk_score* 100) )
        nltk_BLEU_list.append( nltk_score*100  )
        text1 = 'detailed sacreBLEU     span-'+ format(start, '06') + '-' + format(end, '06') +  '     ' + str("{0:.3f}".format(sacre_blue_score))
        sacreBLEU_list.append(sacre_blue_score)
        start += time_step
        end += time_step
        blue_scores.append(text)
        blue_scores.append(text1)
    avg_BLEU = "avg      BLEU          span*                  " + str("{0:.3f}".format(round((sum(nltk_BLEU_list)/len(nltk_BLEU_list)), 3))) 
    avg_SacreBleu = "avg      sacreBLEU     span*                  " + str("{0:.3f}".format(round((sum(sacreBLEU_list)/len(sacreBLEU_list)), 3)))
    return blue_scores, avg_BLEU, avg_SacreBleu

