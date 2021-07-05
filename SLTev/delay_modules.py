#!/usr/bin/env python

from files_modules import delay_segmenter


def get_timestamps_table_without_partials(ostt_sentences, reference):
    """
    Receiving OStt (time-stamped transcript) sentences and reference sentences and calculate T table just with using complete sentences:
    elements of T is a dictionary that key is one word of reference and value is the end time of the word.
    To calculate the T table, first, the spent time of the Complete segment in the Ostt is calculated and the time is divided per number of equivalent sentence words in the reference.

    :param ostt_sentences: a list of OStt sentences (each sentence contains multiple P and one C segments)
    :param reference: a list of OSt (tt) sentences
    :return timestamps_table: a list of dictionaries in which each dictionary contains keys in the corresponding sentence words in the reference.
    """

    timestamps_table = []
    sentence_lengths = []
    start_times = []
    for sentence in ostt_sentences:
        sentence_time = float(sentence[-1][1]) - float(sentence[0][0])
        sentence_lengths.append(sentence_time)
        start_times.append(float(sentence[0][0]))

    for sentence in range(len(reference)):
        time_step = start_times[sentence]
        step = sentence_lengths[sentence] / len(reference[sentence][:-1])
        l = dict()
        for word in reference[sentence][:-1]:
            time_step = time_step + step
            l[word] = time_step
        timestamps_table.append(l)
    return timestamps_table


def segment_tokens_times(segment):
    """
    getting a segment and for each token, the ending time is calculated.

    :param segment: a segment (Partial or Complete)
    :return time_tokens: a dictionary that contains unique tokens as keys and ending time as values
    """

    time_tokens = {}
    duration = float(segment[1]) - float(segment[0])
    step = duration / len(segment[2:-1])
    count = 1
    for token in segment[2:-1]:
        if token not in time_tokens.keys():
            time_tokens[token] = float(segment[0]) + count * step
        count += 1
    return time_tokens


def make_align_dict(align, ref):
    """
    making alignment between source and reference by aligning file. 
    in the output, each token of reference would be aligned with the token of the source (OStt)

    :param align: an align dictionary
    :param ref: a list of tokens in the sentence
    :return align_dict: a dictionary that each token of ref would be assigned to a place of a token in the OStt
    """

    align_dict = {}
    for k, v in align.items():
        for i in v:
            align_dict[ref[:-1][int(i) - 1]] = k
    return align_dict


def get_timestamps_table(ostt_sentences, reference_sentences, aligns=None):
    """
    Receiving OStt (time-stamped transcript), reference sentences, and the alignment (MGIZA sentence orders) and T matrix is calculated.
    Each row of T is a dictionary in which the keys are tokens of the reference sentences, and the values, are the end time of those tokens.

    :param ostt_sentences: a list of OStt sentences
    :param reference_sentences: a list of OSt (ref) sentences
    :param aligns: alist of align sentences
    :return T: the T matrix
    """

    timestamp_table = []
    for index in range(len(ostt_sentences)):
        sentence = ostt_sentences[index]
        seen_tokens = {}
        ostt_token_times = [0]
        for segment in sentence:
            segment_tokens_time = segment_tokens_times(segment)
            for token, time in segment_tokens_time.items():
                if token in sentence[-1][2:-1] and token not in seen_tokens.keys():
                    seen_tokens[token] = time
                    ostt_token_times.append(time)
        ostt_token_times.append(0)

        # assign time of OStt words (source) to the reference words
        ref_T = {}
        counter = 1
        ostt_tokens = []
        for token in reference_sentences[index][:-1]:
            if token in ref_T.keys():
                continue
            p = float(len(ostt_token_times) - 2) / len(set(reference_sentences[index][:-1])) * counter

            t = ostt_token_times[int(p)] + (
                (ostt_token_times[int(p) + 1] - ostt_token_times[int(p)]) * (p - int(p))
            )
            ref_T[token] = t
            counter += 1
            ostt_tokens.append(token)

        # Using align file
        if aligns != None:
            max_value = 0
            align_dict = make_align_dict(aligns[index], reference_sentences[index])
            for token in ostt_tokens:
                try:
                    ref_T[token] = max([ref_T[token], max_value, seen_tokens[align_dict[token]]])
                except:
                    ref_T[token] = max([ref_T[token], max_value])
                if max_value < ref_T[token]:
                    max_value = ref_T[token]
        timestamp_table.append(ref_T)
    return timestamp_table


def get_candidate_timestamp_table(sentence_segments):
    """
    Receiving segments of the candidate sentences and calculates candiate timestamps table:
    candiate timestamps table is a dictionary that keys are words of MT/SLT/ASR sentence, and value is the display time of the words.

    :param sentence_segments: a sentence of candidates (SLT/ASR/MT)
    :return uniq_tokens_show_time: a dictionary that unique tokens are the keys and display times are the values
    :return uniq_tokens_estimate_time: a dictionary that unique tokens are the keys and estimated times are the values
    """

    uniq_tokens_show_time = {}
    uniq_tokens_estimate_time = {}
    for segment in sentence_segments:
        tokens = segment[3:-1]
        step = (float(segment[2]) - float(segment[1])) / len(tokens)
        for token in segment[3:-1]:
            if (
                token not in uniq_tokens_show_time.keys()
                and token in sentence_segments[-1][3:-1]
            ):
                uniq_tokens_show_time[token] = float(segment[0])
                uniq_tokens_estimate_time[token] = float(
                    float(segment[1]) + ((tokens.index(token) + 1) * step)
                )
    return uniq_tokens_show_time, uniq_tokens_estimate_time


def extract_match_tokens_based_on_time(estimat_times, display_times, start, end):
    """
    extracting all words in candidate which have estimation time in range start and end (start and end extracted in OStt).

    :param estimat_times: an estimation dictionary that obtained by get_candidate_timestamp_table
    :param display_times: an display dictionary that obtained by get_candidate_timestamp_table
    :param start,end: the start and end times of a sentence based on the OStt.
    :return out: a dictionary that contains words between start and end
    """

    match_tokens = {}
    min_value = 1000000000
    max_value = -1
    # extract tokens between start and end times
    for i in range(len(estimat_times)):
        for k, v in estimat_times[i].items():
            if v <= end and v >= start:
                match_tokens[k] = display_times[i][k]
                if v < min_value:
                    min_value = v
                if v > max_value:
                    max_value = v
    # add an extra token in two sides
    leftside_list = []
    rightside_list = []
    for i in range(len(estimat_times)):
        for k, v in estimat_times[i].items():
            if v < min_value:
                leftside_list.append([v, k, display_times[i][k]])
            if v > max_value:
                rightside_list.append([v, k, display_times[i][k]])

    if leftside_list != []:
        leftside_list.sort()
        match_tokens[leftside_list[-1][1]] = leftside_list[-1][2]
    if rightside_list != []:
        rightside_list.sort()
        match_tokens[rightside_list[0][1]] = rightside_list[0][2]
    return match_tokens


def get_delay(timestamp_table, match_tokens):
    """
    the calculating delay between timestamp table and match tokens

    :param timestamp_table: the timestamp table
    :param match_words: Common words between T matrix (OSt words) and submission file based on the two different types of segmentation
    :return miss_tokens: words that just are in the T
    :return delay: difference between tokens time in the timestamp table and display time in the match tokesn
    """

    miss_tokens = 0
    delay = 0
    for token, time in timestamp_table.items():
        try:
            d = float(match_tokens[token]) - time
            if d > 0:
                delay += d
        except:
            miss_tokens += 1
    return miss_tokens, delay


def time_based_evaluation(Ts, candidate_sentences, OStt_sentences):
    """
    the calculating delay between submission and reference 

    :param Ts: a list of timestamps tables
    :param candidate_sentences: a list of candidate_sentences senetnces
    :param OStt_sentences: a list of OStt sentences
    :return sum_delay: sum of delays between between submission and OSts
    :return sum_missing_tokens: sum of missing tokens between between submission and OSts
    """

    sum_delay = 0
    sum_missing_tokens = 0
    display_times = []
    estimat_times = []

    for i in range(len(candidate_sentences)):
        display_T, estimat_T = get_candidate_timestamp_table(candidate_sentences[i])
        display_times.append(display_T)
        estimat_times.append(estimat_T)

    for j in range(len(OStt_sentences)):
        start = float(OStt_sentences[j][-1][0])
        end = float(OStt_sentences[j][-1][1])
        match_words = extract_match_tokens_based_on_time(
            estimat_times, display_times, start, end
        )
        temp_list = []
        for T in Ts:
            miss, delay = get_delay(T[j], match_words)
            temp_list.append([delay, miss])
        temp_list.sort()
        sum_missing_tokens += temp_list[0][1]
        sum_delay += temp_list[0][0]
    return sum_delay, sum_missing_tokens


def get_wordbased_candidate_table(candidate_sentences):
    """
    In this function, for each slt segment, the candidate time table will be created

    :param candidate_sentences: a list of candidate sentences
    :return flat_candidate_table: a list of dictionary that unique words in the C segments are the keys, and display times are the values
    """

    candidate_table = []
    for sentence_segments in candidate_sentences:
        # bulild candidate time table for each segment 
        uniq_tokens_start_time = {}
        for segment in sentence_segments:
            for token in segment[3:-1]:
                if token not in uniq_tokens_start_time.keys():
                    uniq_tokens_start_time[token] = float(segment[0])
        # convert candidate timetable to a list according to Complete segments
        token_segment = []
        for token in sentence_segments[-1][3:-1]:
            token_segment.append([token, uniq_tokens_start_time[token]])
        candidate_table.append(token_segment)

    # flatten 2D candidate_table 
    flat_candidate_table = []
    for i in candidate_table:
        flat_candidate_table += i
    return flat_candidate_table


def time_based_segmenter(segmenter_sentence, flat_candidate_table, MovedWords):
    """
    this function indicates each segment in segmenter_sentence contains which segments in candidate by mwerSegmenter.

    :param segmenter_sentence: list of sentences based on the mwerSegmenter
    :param flat_candidate_table: the output of the get_wordbased_candidate_table functions (display times of submission words)
    :param MovedWords: indicate move number to left and write (default is 1)
    :return segment_times: a list of correspond words in the  flat_candidate_table
    """

    segment_times = list()
    start = 0
    for i in range(len(segmenter_sentence)):
        segment = segmenter_sentence[i]
        end = start + len(segment)
        temp = flat_candidate_table[start:end]
        try:
            right_moved = flat_candidate_table[end : (end + MovedWords)]
        except:
            right_moved = []
        try:
            left_moved = flat_candidate_table[(start - MovedWords) : end]
        except:
            left_moved = []
        temp = left_moved + temp + right_moved
        start = end
        # convert each segment to a dictionary
        temp_dict = dict()
        for item in temp:
            temp_dict[item[0]] = item[1]
        segment_times.append(temp_dict)
    return segment_times


def word_based_evaluation(evaluation_object, temp_folder):
    flat_candidate_table = get_wordbased_candidate_table(evaluation_object.get('candidate_sentences'))

    segmenter_sentence, mWERQuality = delay_segmenter(
        evaluation_object, temp_folder
        )
    segment_times = time_based_segmenter(segmenter_sentence, flat_candidate_table, evaluation_object.get('MovedWords'))
    sum_delay = 0
    sum_missing_words = 0
    for i in range(len(evaluation_object.get('Ts')[0])):
        temp_list = []
        for T in evaluation_object.get('Ts'):
            miss, delay = get_delay(T[i], segment_times[i])
            temp_list.append([delay, miss])
        temp_list.sort()
        sum_missing_words += temp_list[0][1]
        sum_delay += temp_list[0][0]
    return sum_delay, sum_missing_words, mWERQuality

