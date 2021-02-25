#!/usr/bin/env python

import sacrebleu
from files_modules import *

######################################################################
# quality functions 
######################################################################

def calc_bleu_score_document(references, MT):
    """
    Calculating bleu score by using sacrebleu module. In this method, all Complete segmented in MT is sys document and all Ts sentences is ref document. 
    
    :param references: a list of references
    :param MT: a list of MT senetnces 
    :return sacre_blue_score: the bleu score
    """

    merge_mt_sentences = []
    for i in range(len(MT)):
        mt = MT[i][-1][3:-1]
        merge_mt_sentences += mt
    merge_references_sentences = []
    for ref in references:
        l = []
        for sentence in ref:
            l.append(' '.join(sentence[:-1]))
        merge_references_sentences.append(l)
    refs= [' '.join(i) for i in merge_references_sentences]
    sys = ' '.join(merge_mt_sentences[:])
    b_sacre = sacrebleu.sentence_bleu(sys, refs)
    sacre_blue_score = b_sacre.score
    return sacre_blue_score

def calc_bleu_score_sentence_by_sentence(references, MT, language, SLTev_home, temp_folder):
    """
    Calculating bleu score sentence by sentence sacrebleu module.
    
    :param references: a list of references 
    :param MT: a list of MT senetnces 
    :param language: the submision language. 
    :param SLTev_home: path of the mwerSegmenter folder
    :param temp_folder: path of the temp folder that created by UUID
    :return sacre_blue_score: the bleu score
    """
   
    mt_sentences = []
    for i in range(len(MT)):
        mt = MT[i][-1][3:-1]
        mt_sentences.append(mt)        
    references_sentences = []
    merge_references_sentences = []
    for ref in references:
        l = []
        for sentence in ref:
            l.append(' '.join(sentence[:-1]))
        merge_references_sentences.append(l)     
    segmenter_sentence, mWERQuality = qualitySegmenter(MT, references, language, SLTev_home, temp_folder)
    sys = [' '.join(i) for i in segmenter_sentence]
    refs = merge_references_sentences[:]
    b_sacre = sacrebleu.corpus_bleu(sys, refs)
    sacre_blue_score = b_sacre.score
    return sacre_blue_score

def build_A_Time_Based_quality(sentence_segments):
    """
    Receiving segments of the mt sentences and calculates uniq_words_estimate_time dictionary
       
    :param sentence_segments: a list of a sentence segments
    :return uniq_words_estimate_time: a dictionary which key is one word of MT sentence and value is the display time of the
    word.
    """
    
    uniq_words_show_time = {}
    uniq_words_estimate_time = {}
    for word in sentence_segments[-1][3:-1]:
        uniq_words_estimate_time[word] = 0
        uniq_words_show_time[word] = 0
    for segment in sentence_segments:
        words = segment[3:-1] 
        step = (float(segment[2])-float(segment[1]))/len(words)
        for word in segment[3:-1]:
            try:
                if uniq_words_show_time[word] == 0:
                    uniq_words_show_time[word] = float(segment[0])
                    uniq_words_estimate_time[word] = float(float(segment[1]) + ((words.index(word)+1)*step))
            except:
                pass
    return uniq_words_estimate_time

def calc_bleu_score_sentence_by_time(Ts, MT, time_step):
    """
    Calculates blue score using the NLTK module with time slice strategy.
    
    :param Ts: a list of T tables 
    :param MT: a list of MT senetnces 
    :param time_step: size of time-step
    :return blue_scores: the average bleu score between time-step scores
    :return avg_SacreBleu: a list of time-step scores 
    """  
    
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
    start = 0 
    end = time_step
    sacreBLEU_list = []
    blue_scores = []
    for t in  range(len(mt_sentences)):
        try:
            sys = ' '.join(mt_sentences[t])
            refs = [ ' '.join(ref) for ref in references_sentences[t]]
            b_sacre = sacrebleu.sentence_bleu(sys, refs)
            sacre_blue_score = b_sacre.score
            text1 = 'detailed sacreBLEU     span-'+ format(start, '06') + '-' + format(end, '06') +  '     ' + str("{0:.3f}".format(sacre_blue_score))
            sacreBLEU_list.append(sacre_blue_score)
            start += time_step
            end += time_step
            blue_scores.append(text1)
        except:
            pass
    avg_SacreBleu = "avg      sacreBLEU     span*                  " + str("{0:.3f}".format(round((sum(sacreBLEU_list)/len(sacreBLEU_list)), 3)))
    return blue_scores, avg_SacreBleu



