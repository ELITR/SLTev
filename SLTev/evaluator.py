#!/usr/bin/env python

import sys
import os
import shutil
import uuid
from delay_modules import *
from flicker_modules import *
from quality_modules import *
from files_modules import *
from utilities import *

def evaluator(ostt=None, asr=False, tt=[], align=[], mt=None, b_time=3000, SLTev_home="./", simple="False", ostt_state=0, time_stamp='True' ):
    """"
    This function receives three input files OStt, tt (OSt), MT (ASR/SLT), and align (optionally)
    and doing slt/asr/mt evaluation
    """   

    current_path = os.getcwd() 
    MovedWords = 1
    references =[]
    language = 'en'
    for path in tt:
        references.append(read_tt(path))
        
    #----------------------------------------
    if simple == 'False':
        eprint("P ... considering Partial segments in delay and quality calculation(in addition to Complete segments)")
        eprint("T ... considering source Timestamps supplied with MT output")
        eprint("W ... segmenting by mWER segmenter (i.e. not segmenting by MT source timestamps)")
        eprint("A ... considering word alignment (by GIZA) to relax word delay (i.e. relaxing more than just linear delay calculation)")
        eprint("------------------------------------------------------------------------------------------------------------")
    number_refs_words = []
    for ref in references:
        number_refs_words.append(get_number_words(ref))
        
    avergae_refs_words = sum(number_refs_words) / len(number_refs_words)
    ref_text = '--       TokenCount'
    count = 1
    for i in number_refs_words:
        text = '   reference'  + str(count) + '             ' + str(int(i))
        count += 1
        ref_text = ref_text + ' ' + text
        
    if simple == 'False':
        print(ref_text) #---- WordCount tt1 1699 tt2 1299 ...
    if simple == 'False':
        print("avg      TokenCount    reference*            ", int(avergae_refs_words)) #---- avg WordCount tt* 12345 
    count = 1
    sum_sentences = 0
    ref_text = '--       SentenceCount'
    for i in references:
        text = 'reference'  + str(count) + '             ' + str(len(i))
        count += 1
        ref_text = ref_text + ' ' + text
        sum_sentences += len(i)
        
    if simple == 'False':    
        print(ref_text) #---- SentenceCount tt1 1699 tt2 1299 ...
        print("avg      SentenceCount reference*            ", str(int(sum_sentences/len(references)))) #---- avg SentenceCount tt* 220 
    MT = read_MT(mt)
    if time_stamp == "True":
        if ostt_state == 0:
            OStt = read_ostt(ostt)
        else:
            OStt = read_ost_as_ostt(ostt)
        #-----------get duration of ASR
        start = OStt[0][0][0]
        end = OStt[-1][-1][1]
        duration = float(end) - float(start)
        duration =  str("{0:.3f}".format(round(duration, 3)))
        if simple == 'False':
            print("OStt     Duration      --                    ", duration) #---- OStt Duration -- 88816 
        Ts = []
        for reference in references: 
            T = get_Zero_T(OStt, reference)
            Ts.append(T)
        
    if simple == 'False' and time_stamp == "True":
        delay, missing_words = evaluate(Ts,MT, OStt)
        print("tot      Delay         T                     ", str("{0:.3f}".format(round(delay, 3))))
        print("avg      Delay         T                     ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
        print("tot      MissedTokens  T                     ", missing_words)
        try:
            temp_folder = "./" + str(uuid.uuid4())
            delay, missing_words, mWERQuality = evaluate_segmenter(Ts, MT, MovedWords, language, SLTev_home, temp_folder)
            print("tot      Delay         W                     ", str("{0:.3f}".format(round(delay, 3))))
            print("avg      Delay         W                     ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
            print("tot      MissedTokens  W                     ", missing_words)
            print("tot      mWERQuality   W                     ", mWERQuality)
        except:
            os.chdir(current_path)
            shutil.rmtree(temp_folder, ignore_errors=True)
            
    if time_stamp == "True":
        Ts = []
        for reference in references: 
            T = get_One_T(OStt, reference)
            Ts.append(T)

    if simple == 'False' and time_stamp == "True":
        delay, missing_words = evaluate(Ts,MT, OStt)
        print("tot      Delay         PT                    ", str("{0:.3f}".format(round(delay, 3))))
        print("avg      Delay         PT                    ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
        print("tot      MissedWords   PT                    ", missing_words)
    
    if time_stamp == "True":
        try:
            temp_folder = "./" + str(uuid.uuid4())
            delay, missing_words, mWERQuality = evaluate_segmenter(Ts, MT, MovedWords, language, SLTev_home, temp_folder)
            print("tot      Delay         PW                    ", str("{0:.3f}".format(round(delay, 3))))
            if simple == 'False':
                print("avg      Delay         PW                    ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
                print("tot      MissedTokens  PW                    ", missing_words)
        except:
            os.chdir(current_path)
            shutil.rmtree(temp_folder, ignore_errors=True)
            
    if asr == False and simple == 'False' and time_stamp == "True":
        aligns =[]
        for i in align:
            path = i
            aligns.append(read_alignment_file(path))
        Ts = []
        for index in range(len(references)): 
            reference = references[index]
            align = aligns[index]
            if len(align) != len(reference):
                print('len align(', len(align), ') is not equal to len tt (', len(reference), ') it maybe giza++ not good work'  )
                sys.exit(1)
            T = get_One_T(OStt, reference, align)
            Ts.append(T)
        delay, missing_words = evaluate(Ts,MT, OStt)
        print("tot      Delay         PTA                   ", str("{0:.3f}".format(round(delay, 3))))
        print("avg      Delay         PTA                   ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
        print("tot      MissedTokens  PTA                   ", missing_words)     
        try:
            temp_folder = "./" + str(uuid.uuid4())
            delay, missing_words, mWERQuality =  evaluate_segmenter(Ts, MT, MovedWords, language, SLTev_home, temp_folder)
            print("tot      Delay         PWA                   ", str("{0:.3f}".format(round(delay, 3))))
            print("avg      Delay         PWA                   ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
            print("tot      MissedTokens  PWA                   ", missing_words)
        except:
            os.chdir(current_path)
            shutil.rmtree(temp_folder, ignore_errors=True)
            
    if simple == 'False' and time_stamp == "True":    
        print("tot      Flicker       count_changed_Tokens  ", int(calc_revise(MT)))
    
    if  time_stamp == "True":
        print("tot      Flicker       count_changed_content ", int(calc_flicker(MT)))
    
    if simple == 'False' and time_stamp == "True":
        print("macroavg Flicker       count_changed_content ", str("{0:.3f}".format(round(calc_average_flickers_per_sentence(MT), 3)))  )
        print("microavg Flicker       count_changed_content ",  str("{0:.3f}".format(round(calc_average_flickers_per_document(MT), 3))))
        

    sacre_score = calc_bleu_score_document(references, MT)
    print("tot      sacreBLEU     docAsAWhole           ",  str("{0:.3f}".format(round(sacre_score, 3)))  )
    
    if simple == 'False':
        try:
            temp_folder = "./" + str(uuid.uuid4())
            sacre_score  = calc_bleu_score_sentence_by_sentence(references, MT, language, SLTev_home, temp_folder)
            print("avg      sacreBLEU     mwerSegmenter         ", str("{0:.3f}".format(round(sacre_score, 3))) )
        except:
            os.chdir(current_path)
            shutil.rmtree(temp_folder, ignore_errors=True)
            
    if simple == 'False' and time_stamp == "True":        
        try:
            c_b_s_s_by_time,  avg_SacreBleu = calc_bleu_score_sentence_by_time(Ts, MT, b_time)
            for x in c_b_s_s_by_time:
                print(x)
            print(avg_SacreBleu)
        except:
            pass





