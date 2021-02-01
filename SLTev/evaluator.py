#!/usr/bin/env python

import argparse
import sys
import sacrebleu
import subprocess as sp
import os
from mosestokenizer import *
from delay_modules import *
from flicker_modules import *
from quality_modules import *
from files_modules import *





def evaluator(ostt=None, asr=False, tt=[], align=[], mt=None, b_time=3000, SLTev_home="./", simple="False" ):

    """"
    This function receives three input files OStt, tt (OSt), MT (ASR/SLT), and align (optionally)
    and doing slt/asr/mt evaluation
    """
    
    current_path = os.getcwd() 
    
    MovedWords = 1
    references =[]
    language = 'en'
    for i in tt:
        path = i
        #------------check exist file
        if os.path.isfile(path):
            if '.de.OSt' in path:
                language = 'de'
            elif '.cs.OSt' in path:
                language = 'cs'

        else:
            print (path, " not exist")
            sys.exit(1)
        #-------------add to refernec list
        references.append(read_tt(path))

    #---------- Calculte number of words

    #----------------------------------------
    if simple == 'False':
        print("n ... not considering, not using")
        print("P ... considering Partial segments in delay and quality calculation(in addition to Complete segments)")
        print("T ... considering source Timestamps supplied with MT output")
        print("W ... segmenting by mWER segmenter (i.e. not segmenting by MT source timestamps)")
        print("A ... considering word alignment (by GIZA) to relax word delay (i.e. relaxing more than just linear delay calculation)")
        print("------------------------------------------------------------------------------------------------------------")

    #-----------------------------------------
    number_refs_words = []
    for ref in references:
        number_refs_words.append(get_number_words(ref))

    avergae_refs_words = sum(number_refs_words) / len(number_refs_words)

    ref_text = '--       WordCount'
    count = 1
    for i in number_refs_words:
        text = '    tt'  + str(count) + '                    ' + str(int(i))
        count += 1
        ref_text = ref_text + ' ' + text
    if simple == 'False':
        print(ref_text) #---- WordCount tt1 1699 tt2 1299 ...

    if simple == 'False':
        print("avg      wordCount     tt*                   ", int(avergae_refs_words)) #---- avg WordCount tt* 12345 
    #print("Number of tt words: ", avergae_refs_words)

    count = 1
    sum_sentences = 0
    ref_text = '--       SentenceCount'
    for i in references:
        text = 'tt'  + str(count) + '                    ' + str(len(i))
        count += 1
        ref_text = ref_text + ' ' + text
        sum_sentences += len(i)
    if simple == 'False':    
        print(ref_text) #---- SentenceCount tt1 1699 tt2 1299 ...
        print("avg      SentenceCount tt*                   ", str(int(sum_sentences/len(references)))) #---- avg SentenceCount tt* 220 





    OStt = read_ostt(ostt)
    MT = read_MT(mt, asr)


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


    if simple == 'False':
        delay, missing_words = evaluate(Ts,MT, OStt)
        print("tot      Delay         nTnn                  ", str("{0:.3f}".format(round(delay, 3))))
        print("avg      Delay         nTnn                  ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
        print("tot      MissedWords   nTnn                  ", missing_words)
        try:
            delay, missing_words, mWERQuality = evaluate_segmenter(Ts, MT, MovedWords, language, SLTev_home)


            print("tot      Delay         nnWn                  ", str("{0:.3f}".format(round(delay, 3))))
            print("avg      Delay         nnWn                  ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
            print("tot      MissedWords   nnWn                  ", missing_words)
            print("tot      mWERQuality   nnWn                  ", mWERQuality)
        except:
            os.chdir(current_path)


    Ts = []
    for reference in references: 
        T = get_One_T(OStt, reference)
        Ts.append(T)

    if simple == 'False':
        delay, missing_words = evaluate(Ts,MT, OStt)

        print("tot      Delay         PTnn                  ", str("{0:.3f}".format(round(delay, 3))))
        print("avg      Delay         PTnn                  ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
        print("tot      MissedWords   PTnn                  ", missing_words)

    try:
        delay, missing_words, mWERQuality = evaluate_segmenter(Ts, MT, MovedWords, language, SLTev_home)

        print("tot      Delay         PnWn                  ", str("{0:.3f}".format(round(delay, 3))))
        print("avg      Delay         PnWn                  ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
        print("tot      MissedWords   PnWn                  ", missing_words)
        print("tot      mWERQuality   PnWn                  ", mWERQuality)
    except:
        os.chdir(current_path)

    if asr == False and simple == 'False':

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

        print("tot      Delay         PTnA                  ", str("{0:.3f}".format(round(delay, 3))))
        print("avg      Delay         PTnA                  ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
        print("tot      MissedWords   PTnA                  ", missing_words)
        
        try:
            delay, missing_words, mWERQuality =  evaluate_segmenter(Ts, MT, MovedWords, language, SLTev_home)

            print("tot      Delay         PnWA                  ", str("{0:.3f}".format(round(delay, 3))))
            print("avg      Delay         PnWA                  ", str("{0:.3f}".format(round((delay/avergae_refs_words), 3))))
            print("tot      MissedWords   PnWA                  ", missing_words)
            print("tot      mWERQuality   PnWA                  ", mWERQuality)
        except:
            os.chdir(current_path)

    if simple == 'False':    
        print("tot      Flicker       count_changed_words   ", int(calc_revise(MT)))

    print("tot      Flicker       count_changed_content ", int(calc_flicker(MT)))

    if simple == 'False':
        print("macroavg Flicker       count_changed_content ", int(calc_average_flickers_per_sentence(MT)) )

        print("microavg Flicker       count_changed_content ", int(calc_average_flickers_per_document(MT))  )

    sacre_score = calc_bleu_score_documnet(Ts, MT)

    print("tot      sacreBLEU     docAsAWhole           ",  str("{0:.3f}".format(round(sacre_score, 3)))  )

    if simple == 'False':
        try:
            sacre_score, tot_bleu_sacre  = calc_bleu_score_sentence_by_sentence(Ts, MT, language, SLTev_home)

            print("avg      sacreBLEU     --                    ", str("{0:.3f}".format(round(sacre_score, 3))) )

            print('tot      sacreBLEU     mWER-segmented        ', str("{0:.3f}".format(round(tot_bleu_sacre, 3))) )
        except:
            os.chdir(current_path)
            
        c_b_s_s_by_time,  avg_SacreBleu = calc_bleu_score_sentence_by_time(Ts, MT, b_time)
        for x in c_b_s_s_by_time:
            print(x)
        print(avg_SacreBleu)





