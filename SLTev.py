#===========================================================
#  Title:  SLTev
#  Author: Ebrahim Ansari, Ondrej Bojar, Mohammad Mahmoudi
#  Date:   02 Feb 2022
#  This Project is a part of the framework which is written 
# to evaluate simoltanius translation systems.
#  https://github.com/ELITR/
#===========================================================

#!/usr/bin/env python

import argparse
import sys
import nltk

def read_reference(file_name):
    """

    Read the input reference file and save sentences in a list (each sentence splits by space) 
    Input: path of the reference file like as 'sample/reference'
    Out_put : a list of sentences that split by space like as [['i', 'am', '.'], ['you', 'are', '.'] ]

    """
    reference = list()
    with open(file_name, 'r') as in_file:
        line = in_file.readline()
        while line: 
            reference.append(line.strip().split(' '))
            line = in_file.readline()
    reference = list(filter(lambda a: a != [], reference))
    return reference

def read_ASR(file_name):
    """

    Read ASR (time-stamped transcript) file and save sentences in a list (each sentence contains many segments that split by space)
    Input: the path of reference file like as 'sample/ASR'
    Out_put: a list of sentences which each sentence split to many segments. 

    """
    ASR = list()
    sentence = []
    with open(file_name, 'r') as in_file:
        line = in_file.readline()
        while line:
            if 'P ' in line[:3]:
                l = line.strip().split()[1:]
                l.append('.')
                sentence.append(l)

            else:
                l = line.strip().split()[1:]
                l.append('.')
                sentence.append(l)
                ASR.append(sentence)
                sentence = []

            line = in_file.readline()
    ASR = list(filter(lambda a: a != [['.']], ASR))
    for i in range(len(ASR)):
        sentence = ASR[i]
        temp = sentence[0][1]
        for j in range(1,len(sentence)):
            ASR[i][j][0] = temp 
            temp = ASR[i][j][1]
        
    return ASR

def read_MT(file_name):
    """

    Read MT file and save sentences in a list (each sentence contains many segments that split by space)
    Input: the path of reference file like as 'sample/OUT_MT'
    Out_put: a list of sentences which each sentence split to many segments. 

    """
    MT = list()
    sentence = []
    with open(file_name, 'r') as in_file:
        line = in_file.readline()
        while line:
            if 'P ' in line[:3]:
                l = line.strip().split()[1:]
                l.append('.')
                sentence.append(l)

            else:
                l = line.strip().split()[1:]
                l.append('.')
                sentence.append(l)
                MT.append(sentence)
                sentence = []

            line = in_file.readline()
    MT = list(filter(lambda a: a != [['.']], MT))
    return MT


def get_Zero_T(ASR, reference):
    """

    Receives ASR (time-stamped transcript) sentences and reference sentences and calculate T matrix:
    which elements of T is a dictionary that key is one word of reference and value is the end time of the word.      

    """
    Zero_T = []
    sentence_times = []
    start_times = []
    for sentence in ASR:

        sentence_time = int(sentence[-1][1]) - int(sentence[0][0])
        sentence_times.append(sentence_time)
        start_times.append(int(sentence[0][0]))
    
    for sentence in range(len(reference)):
        time_step = start_times[sentence] 
        step = sentence_times[sentence]/ len(reference[sentence])
        #l = {"##mean_delay##":(time_step/2)}
        l = dict()
        for word in reference[sentence][:-1]:
            time_step = time_step + step
            l[word] = time_step
            
        
        Zero_T.append(l)
    return Zero_T



def remove_listElement_onOther_list(list1, list2):
    """

    Receives two arrays and removes the common elements in the first array (list1).  

    """
    for i in list2:
        try:
            list1.remove(i)
        except:
            pass
    return list1

def calc_change_words(segment1, segment2):
    """

    Receives two segments and calculates the number of times the first segment words have been changed.

    """
    count =0 
    for word in segment1:
        if word not in segment2:
            count += 1
    return count

def calc_flicker(MT):
    """

    Calculates the sum of the flickers in all MT sentences (by calculating the count of changed words).

    """
    flicker_size = 0
    for sentence in MT:
        first_segment = sentence[0][3:-1]
        for segment in sentence[1:]:
            flicker_size += calc_change_words(first_segment, segment[3:-1])
            first_segment = segment[3:-1]
    return flicker_size




def get_One_T(ASR, reference, aligns = None):
    """

    Receives ASR (time-stamped transcript) and reference sentence and makes the alignment (giza sentence orders) and finally calculates T matrix. Each line of T is a dictionary which key is one word of reference line and the value is the end time of that word. 
 
    """
    
    one_T = []
 
    for index in range(len(ASR)):
        sentence = ASR[index]
        #---------set ASR table
        ASR_T = []
        for i in range(len(sentence[-1][2:-1])):
            ASR_T.append(0)
        old_segment = []
        ASR_T_INDEX = 0
        for segment in sentence:
            
            new_words = remove_listElement_onOther_list(segment[2:-1], old_segment)
            old_segment = segment[2:-1]
            segment_start = int(segment[0])
            for i in range(len(new_words)):
                ASR_T[ASR_T_INDEX] = segment_start + (((int(segment[1])-int(segment[0]))/len(new_words))*(i+1))
                ASR_T_INDEX += 1
        #------------------------- set reference table
        ref_T = []
     
        T = dict()
        sentence = reference[index]
        for i in sentence[:-1]:
            ref_T.append(0)
    
        for i in range(len(ref_T)):
   
            index_in_ASR = i*(len(ASR_T)/len(ref_T))
            try:
                temp = ((index_in_ASR - int(index_in_ASR)) * (ASR_T[int(index_in_ASR)+1] -  ASR_T[int(index_in_ASR)]))
            except:
                temp = ((index_in_ASR - int(index_in_ASR)) * (ASR_T[int(index_in_ASR)] -  ASR_T[int(index_in_ASR)]))
            ref_T[i] = ASR_T[int(index_in_ASR)] + temp
        for i in range(len(ref_T)):
            T[sentence[i]] = ref_T[i]
        #--------------------------- use align dictioary
        if aligns == None:
            one_T.append(T)
        else:
           
            align = aligns[index]
           
            for k,v in align.items():
                if k in T.keys() and v != -1:
                    temp = round(v*(len(ref_T)/len(ASR_T)))
                    try:
                        T[k] = max([ref_T[temp], T[k]])
                    except:
                        pass
            one_T.append(T)
    return one_T






def build_A(sentence_segments):
    """

    Receives segments of the sentences and calculates A dictionary:
    A is a dictionary which key is one word of MT sentence and value is the start time of the
    word.

    """
    uniq_words_start_time = {}
    for segment in sentence_segments:
        for word in segment[3:-1]:
            if word not in uniq_words_start_time.keys():
                uniq_words_start_time[word] = int(segment[0])
    start = sentence_segments[-1][1]
    end = sentence_segments[-1][2]
    return uniq_words_start_time, int(start), int(end)



def build_times(A, Ts, A_start, A_end):
    """

    Receives A and T dictionaries and calculates times list:
    each element of times is a list which its elements are like this [word_in_T, start_time_in_T]  
	  
    """
    A_keys = list(A.keys())
    count_T = []
    for T in Ts: 
        count = 0
        excit_flag = 0
        for sentence in T:
                
            for k,v in sentence.items():
                if v >= A_start and v <= A_end:
                    count += 1 

                if v > A_end:
                    excit_flag = 1
                    break
            if excit_flag == 1:
                break
    
        count_T.append(count)
    mean_ref= int(sum(count_T)/len(count_T))
    
    
    times = []
    times_dict = dict()
    #--- build times as add each word and start times from T (create as ASR) which has start value between 
    #--- start and time for each complete segment. 
    for T in Ts: 
        excit_flag = 0
        for sentence in T:

            for k,v in sentence.items():
                if v >= A_start and v <= A_end:
                    try:
                        times_dict[k] = max([v, times_dict[k]])
                    except:
                        times_dict[k] = v
                    
                if v > A_end:
                    excit_flag = 1
                    break
            if excit_flag == 1:
                break
    
    
    
    #--------calculate min_value and max_value from upper times_dict 
    min_value = min_value_in_dict(times_dict)
    max_value = max_value_in_dict(times_dict)
    #------if min_vlue not start of the complete sgment, one lower word from T was added. 
    out = min_value_is_started(min_value, Ts)
    if out != -1:
        times_dict[out[1]] = out[0]
    #------if min_vlue not end of the complete sgment, one higher word from T was added. 
    out = max_value_is_started(max_value, Ts)
    if out != -1:
        times_dict[out[1]] = out[0]
        
    for k,v in times_dict.items():
        times.append([k,v])
    return times, mean_ref
    


def min_value_in_dict(times_dict):
    value = 100000000000
    for k,v in times_dict.items():
        if v < value:
            value = v
            
    return value
def max_value_in_dict(times_dict):
    value = -1
    for k,v in times_dict.items():
        if v > value:
            value = v
         
    return value

def min_value_is_started(min_value, Ts):
    """
   
    If "min_value" was the start of the one segment, so -1 has been returned, otherwise, the minimum nearest start time has been returned.    

 
    """
    lower = []
    is_start = 0
    for T in Ts: 
        excit_flag = 0
        for sentence in T:
            if sentence[list(sentence.keys())[0]] == min_value:
                excit_flag = 1
                is_start = 1
                break
            for k,v in sentence.items():
                if v < min_value :
                    lower.append([v,k])
                     
            if excit_flag == 1:
                break
    if is_start == 0 and lower != []:
        lower.sort()
        return lower[-1]
    else:
        return -1

def max_value_is_started(max_value, Ts):
    """
    
    If "min_value" was the end of the one segment, so -1 has been returned, otherwise, the minimum nearest end time has been returned.  
    
    """
    higher = []
    is_start = 0
    for T in Ts: 
        excit_flag = 0
        for sentence in T:
            if sentence[list(sentence.keys())[-1]] == max_value:
                excit_flag = 1
                is_start = 1
                break
            for k,v in sentence.items():
                if v > max_value :
                    higher.append([v,k])
                     
            if excit_flag == 1:
                break
    if is_start == 0 and higher != []:
        
        higher.sort()
        return higher[0]
    else:
        return -1
    
    
def evaluate(Ts,MT):
    """

    Receives MT sentences and T matrix and calculates the sum of delays.
   
    """
    sum_delay = 0
    for i in range(len(MT)):
        A,start, end = build_A(MT[i])
        times, mean_ref = build_times(A,Ts,start, end)
        #print(times)
        #print(mean_ref)       
        delays = [] 
        for time in times:
            if time[0] in A.keys():
                delay = A[time[0]] - time[1] 
                if delay > 0:
                    delays.append(delay)

        try:
            not_in_refer = max(delays)
        except:
            not_in_refer = 0
        for k in range((len(times)-len(delays))):
            delays.append(not_in_refer)
        delays.sort()    
        sentence_delay = sum(delays[:mean_ref])
        sum_delay += sentence_delay
    return sum_delay

def calc_blue_score_documnet(Ts, MT):
    """

    Calculates blue score by using the NLTK module. Input is the merge all of the sentences in MT and reference
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
        merge_references_sentences.append(l)
    blue_scores = []
    for i in range(len(merge_references_sentences)):
        BLEUscore = nltk.translate.bleu_score.sentence_bleu([merge_references_sentences[i]], merge_mt_sentences, smoothing_function=smoothie)
        blue_scores.append(BLEUscore)
    return max(blue_scores)

def calc_blue_score_sentence_by_sentence(Ts, MT):
    """

    Calculates blue score sentence by sentence with NLTK module.
 
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
        
    #------------------write MT in temp_translate file and reference in temp_ref
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
    #------------run segmentation 
    import os
    text = "./mwerSegmenter -mref temp_ref -hypfile temp_translate &> /dev/null"
    os.system(text)


    os.system('rm temp_ref')
    os.system('rm temp_translate')
    
    #-------------read segments 
    in_file = open('__segments', 'r')
    line = in_file.readline()
    segments = [] 
    while line:
        segments.append(line.strip().split(' '))
        line = in_file.readline()
        
    mt_sentences = segments[:]
    os.system('rm __segments')  
    blue_scores = []
    for j in range(len(references_sentences[0])):
        l = []
        for i in range(len(references_sentences)):
            BLEUscore = nltk.translate.bleu_score.sentence_bleu([references_sentences[i][j]], mt_sentences[j], smoothing_function=smoothie)
            l.append(BLEUscore)
        blue_scores.append(max(l))
    return sum(blue_scores)/len(blue_scores)


def calc_blue_score_sentence_by_time(Ts, MT, time_step):
    """

    Calculates blue score using the NLTK module with time slice strategy.

    """
    from nltk.translate.bleu_score import SmoothingFunction
    smoothie = SmoothingFunction().method4
    start = 0
    end = time_step
    mt_sentences = []
    while end <=  float(MT[-1][-1][2]):
        l = []
        for i in range(len(MT)):
            for j in range(len(MT[i])):
                if float(MT[i][j][1]) >= start and float(MT[i][j][2]) <= end :
                    l += MT[i][j][3:-1]
        mt_sentences.append(list(dict.fromkeys(l)))
        start +=  time_step
        end += time_step
    references_sentences = []
    start = 0
    end = time_step
    while end <=  float(MT[-1][-1][2]):
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

    blue_scores = []
    start = 0 
    end = time_step
    for t in  range(len(mt_sentences)):
        
        b = []
        for i in range(len(references_sentences[t])):
            l = []
            for j in range(len(references_sentences[t][i])):
                BLEUscore = nltk.translate.bleu_score.sentence_bleu([references_sentences[t][i][j]], mt_sentences[t][i], smoothing_function=smoothie)
                l.append(BLEUscore)
            try:
                b.append(max(l))
            except:
                b.append(0)
        text = 'from '+ str(start) + ' to ' + str(end) +  ' is ' + str((sum(b)/len(b)))
        start += time_step
        end += time_step
        blue_scores.append(text)
    return blue_scores



def build_times_simple(A, Ts):
    """

   Receives A and T dictionaries and calculates times list:
    each element of times is a list which its elements are like this [word_in_T, start_time_in_T]
  
    """
    A_keys = list(A.keys())
    
    A_start = A[A_keys[0]]
    A_end = A[A_keys[-1]]
    
    
    times_all = []
    
    for T in Ts: 
        times = []
        excit_flag = 0
        for sentence in T:

            for k,v in sentence.items():
                if v >= A_start and v <= A_end:
                    times.append([k,v])
                    
                if v > A_end:
                    excit_flag = 1
                    break
            if excit_flag == 1:
                break
        times_all.append(times)
    return times_all
    

def evaluate_simple(Ts,MT):
    """

    Receives MT sentences and T matrix and the sum of delays has been calculated.
   
    """
    sum_delay_all = list()
    for i in range(len(MT)):
        A = build_A(MT[i])
        times_all = build_times_simple(A,Ts)
        
        sum_delay = []
        for k in times_all:
            sum_delay.append(0)
        
        for j in range(len(times_all)):
            times = times_all[j]
	    
            delays = [] 
            for time in times:
                if time[0] in A.keys():
                    delay = A[time[0]] - time[1] 
                    if delay > 0:
                        delays.append(delay)

            try:
                not_in_refer = max(delays)
            except:
                not_in_refer = 0
            for k in range((len(times)-len(delays))):
                delays.append(not_in_refer)
            delays.sort()    
            
            sentence_delay = sum(delays)
            sum_delay[j] += sentence_delay
        sum_delay_all.append(sum_delay)
        
    delays = []
    #print('sum_delay_all', sum_delay_all)
    for i in sum_delay_all[0]:
        delays.append(0)
    for i in sum_delay_all:
        for j in range(len(i)):
            delays[j] += i[j]
    #print('delays ',  delays)
    return min(delays)


def read_alignment_file(in_file):
    """"

    Receives alignment file path as the input and a dictionary that indicates matched word in ASR (time-stamped transcript) and reference has been returned. 

    """

    in_file = open(in_file)
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
        d =[]
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
                l[j[0]] = int(j[1])
            except:
                l[j[0]] = int(-1)
        out.append(l)

        
    return out
            
def calc_change_words1(segment1, segment2):
    """

    Receives two segments and calculates times that words have been changed. 

    """
    words = [] 
    for word in segment1:
        if word not in segment2:
            words.append(word) 
    return words
def calc_flicker1(MT):
    """

    Calculates sum of flickers in all MT sentences.  
 
    """
    flicker_size = 0
    for sentence in MT:
        first_segment = sentence[0][3:-1]
        for segment in sentence[1:]:
            words = calc_change_words1(first_segment, segment[3:-1])
            for word in words:
                word_index = first_segment.index(word)
                temp = len(segment[3:-1]) - word_index -1
                flicker_size += temp
            first_segment = segment[3:-1]
    return flicker_size

def segmenter(MT, Ts):
    """

    MT complete segments have been joined and saved in a temp_translate file.
    and temp_translate file has been segmented by mwerSegmenter.  

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
    #------------run segmentation 
    import os
    text = "./mwerSegmenter -mref temp_ref -hypfile temp_translate"
    os.system(text)


    os.system('rm temp_ref')
    os.system('rm temp_translate')

    #-------------read segments 
    in_file = open('__segments', 'r')
    line = in_file.readline()
    segments = [] 
    while line:
        segments.append(line.strip().split(' '))
        line = in_file.readline()

    mt_sentences = segments[:]
    os.system('rm __segments')
    return mt_sentences

def build_segmenter_A(MT):
    """

    In this function, for each MT segment 'A' matrix has been built.
  
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
        strat = end
        #------convert each segment to dictionary-------
        temp1 = dict()
        for i in temp:
            temp1[i[0]] = i[1]
        segment_times.append(temp1)
      
    return segment_times

def evaluate_segmenter(Ts, MT, MovedWords):
    """

    Receives Ts and MT and calculates the delay time.

    """
    A_list = build_segmenter_A(MT)
    segmenter_sentence = segmenter(MT, Ts)
    segment_times = time_segmenter(segmenter_sentence, A_list, MovedWords)
   
    sum_delay = list()
    for T in Ts:
        ref_delay = 0
        for i in range(len(segment_times)):
            
            delays = [] 
            
            for k,v in T[i].items():
                if k in segment_times[i].keys():
                    delay = segment_times[i][k] - v
                    if delay > 0:
                        delays.append(delay)
            try:
                not_in_refer = max(delays)
            except:
                not_in_refer = 0
            for k in range((len(list(T[i].keys()))-len(delays))):
                delays.append(not_in_refer)  
            sentence_delay = sum(delays)
            ref_delay += sentence_delay
            
        sum_delay.append(ref_delay)
    return min(sum_delay)


def calc_average_flickers_per_sentence(MT):
    """

    Calculates the average of flicker per sentence. 
  
    """
    
    sentence_flickers = []
    for sentence in MT:
        sentence_flicker_size = 0
        first_segment = sentence[0][3:-1]
        for segment in sentence[1:]:
            words = calc_change_words1(first_segment, segment[3:-1])
            for word in words:
                word_index = first_segment.index(word)
                temp = len(segment[3:-1]) - word_index -1
                sentence_flicker_size += temp
            first_segment = segment[3:-1]
        average = sentence_flicker_size / float(len(sentence[-1][3:-1]))
        sentence_flickers.append(average)
    return sum(sentence_flickers)/float(len(sentence_flickers))


def calc_average_flickers_per_document(MT):
    """

    Calculates the average of flicker per all sentence (document).   

    """
    flicker_size = 0
    complet_word_count = 0
    for sentence in MT:
        first_segment = sentence[0][3:-1]
        for segment in sentence[1:]:
            words = calc_change_words1(first_segment, segment[3:-1])
            for word in words:
                word_index = first_segment.index(word)
                temp = len(segment[3:-1]) - word_index -1
                flicker_size += temp
            first_segment = segment[3:-1]
        complet_word_count += float(len(sentence[-1][3:-1]))
    return float(flicker_size) / complet_word_count


# initiate the parser
parser = argparse.ArgumentParser(description="This module receives three files  --asr or -a that receives path of ASR file (time-stamped transcript)  --ref or -r that is the path of Reference file   --mt or -m that is the path of MT output file and  -d or --delay that refers to type of delay -t or --ref_d that type of delay calculation by reference 0/1")
parser.add_argument("-a", "--asr", help="path of the ASR file", type=str)
parser.add_argument("-r", "--ref", help="path of the references file", type=list, nargs='+' )
parser.add_argument("-al", "--align", help="path of the aligments file", type=list, nargs='+' )
parser.add_argument("-m", "--mt", help="path of the MT file", type=str )
parser.add_argument("-b", "--b_time", help="slot time of blue score calculation", type=int, default = 200 )
# read arguments from the command line
args = parser.parse_args()

if args.asr == None:
    print('please insert ASR (time-stamped transcript) file path')
    sys.exit(1)
if args.ref == None :
    print('please insert References file path in list')
    sys.exit(1)
if args.mt == None :
    print('please insert MT file path')
    sys.exit(1)



if __name__== "__main__":
    MovedWords = 1
    references =[]
    b_time = args.b_time
    for i in args.ref:
        path = ''.join(i)
        references.append(read_reference(path))
 
    ASR = read_ASR(args.asr)
    MT = read_MT(args.mt)
 
    Ts = []
    for reference in references: 
        T = get_Zero_T(ASR, reference)
        Ts.append(T)
    print('delay with Zero_T (only Complete segments have been used) and times (use Guess times) is:  ', evaluate(Ts,MT))
    print('delay with Zero_T (only Complete segments have been used) and mwerSegmenter is:  ', evaluate_segmenter(Ts, MT, MovedWords))
    Ts = []
    for reference in references: 
        T = get_One_T(ASR, reference)
        Ts.append(T)
    print('delay with one_T (Complete and Partial segments have been used) and times(use Guess times) and without align is:  ', evaluate(Ts,MT))
    print('delay with one_T (Complete and Partial segments have been used) and without align and  use mwerSegmenter is:  ', evaluate_segmenter(Ts, MT, MovedWords))
    aligns =[]
    for i in args.align:
        path = ''.join(i)
        aligns.append(read_alignment_file(path))
    Ts = []

    for index in range(len(references)): 
        reference = references[index]
        align = aligns[index]
        T = get_One_T(ASR, reference, align)
        Ts.append(T)
    print('delay with one_T (Complete and Partial segments have been used) and times(use Guess times) with align is:  ', evaluate(Ts,MT))  
    print('delay with one_T (Complete and Partial segments have been used) and use mwerSegmenter and with align is:  ', evaluate_segmenter(Ts, MT, MovedWords))

 
    print("flicker with method 'count_changed_words ' is equel to:  ", calc_flicker(MT))
    print("flicker with method 'count_changed_content' is equel to:  ", calc_flicker1(MT))
    print("average of divide flicker per length of each sentence:  ", calc_average_flickers_per_sentence(MT))
    print("divive sum sentence flickers per sum of sentence length:", calc_average_flickers_per_document(MT))
    print('bleu score for all sentences is equel to:  ', calc_blue_score_documnet(Ts, MT))
    print('bleu score for sentence-by-sentence is equel to:  ', calc_blue_score_sentence_by_sentence(Ts, MT))
    print('bleu score for document_divided_by_time is equel to:  ', calc_blue_score_sentence_by_time(Ts, MT, b_time))

