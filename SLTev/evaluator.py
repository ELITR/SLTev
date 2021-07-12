#!/usr/bin/env python

import sys
import os
import shutil
import uuid
from delay_modules import get_timestamps_table_without_partials, time_based_evaluation
from delay_modules import word_based_evaluation, get_timestamps_table
from flicker_modules import calc_revise_count, calc_flicker_score
from flicker_modules import calc_average_flickers_per_sentence, calc_average_flickers_per_tokens
from quality_modules import calc_bleu_score_documentlevel, calc_bleu_score_segmenterlevel
from quality_modules import calc_bleu_score_timespanlevel
from files_modules import read_reference_file, read_candidate_file
from files_modules import read_ostt_file, read_alignment_file
from utilities import mwerSegmenter_error_message, eprint


def print_headers():
    eprint(
        "P ... considering Partial segments in delay and quality calculation(in addition to Complete segments)"
    )
    eprint("T ... considering source Timestamps supplied with MT output")
    eprint(
        "W ... segmenting by mWER segmenter (i.e. not segmenting by MT source timestamps)"
    )
    eprint(
        "A ... considering word alignment (by GIZA) to relax word delay (i.e. relaxing more than just linear delay calculation)"
    )
    eprint(
        "docAsWhole ... concatenating all reference segments and candidate complete segments as two documents"
    )
    eprint(
        "mwerSegmenter ... using mWER to resegment complete candidate segments according to reference segments"
    )
    eprint(
        "span-START-END  ... the time span between START and END times (just tokens in the time-span considered)"
    )
    eprint(
        "span* ... average of all time-spans"
    )    
    eprint(
        "------------------------------------------------------------------------------------------------------------"
    )


def read_references(reference_files_paths):
    references = []
    for reference_path in reference_files_paths:
        references.append(read_reference_file(reference_path))
    return references


def get_average_references_token_count(references):
    references_token_count = []
    for ref in references:
        reference_token_count = sum([len(sentence)-1 for sentence in ref])
        references_token_count.append(reference_token_count)
    average_refernces_token_count = sum(references_token_count) / len(references)
    return average_refernces_token_count


def print_references_token_info(references):
    references_token_count = []
    for ref in references:
        reference_token_count = sum([len(sentence)-1 for sentence in ref])
        references_token_count.append(reference_token_count)
    average_refernces_token_count = sum(references_token_count) / len(references)

    token_info = "--       TokenCount"
    counter = 1
    for token_count in references_token_count:
        text = "   reference" + str(counter) + "             " + str(int(token_count))
        counter += 1
        token_info = token_info + " " + text
    print(token_info)
    print(
            "avg      TokenCount    reference*            ", int(average_refernces_token_count)
        )

    
def print_references_sentence_info(references):
    counter = 1
    sentence_info =  "--       SentenceCount"
    references_sentences_count = 0
    for ref in references:
        text = "reference" + str(counter) + "             " + str(len(ref))
        counter += 1
        sentence_info = sentence_info + " " + text
        references_sentences_count += len(ref)

    print(sentence_info) 
    print(
            "avg      SentenceCount reference*            ",
            str(int(references_sentences_count / len(references))),
        ) 


def references_statistical_info(references):
    print_references_token_info(references) # token info
    print_references_sentence_info(references) # sentence info


def print_ostt_duration(OStt_sentences):
    start = OStt_sentences[0][0][0]
    end = OStt_sentences[-1][-1][1]
    duration = float(end) - float(start)
    duration = str("{0:.3f}".format(round(duration, 3)))
    print(
            "OStt     Duration      --                    ", duration
        ) 


def candidate_delay_evaluation_without_partials(evaluation_object):
    delay, missing_tokens = time_based_evaluation(
        evaluation_object.get('Ts'),
        evaluation_object.get('candidate_sentences'),
        evaluation_object.get('OStt_sentences')
        )
    print(
        "tot      Delay         T                     ",
        str("{0:.3f}".format(round(delay, 3))),
    )
    print(
        "avg      Delay         T                     ",
        str("{0:.3f}".format(round((delay / evaluation_object.get('average_refernces_token_count')), 3))),
        )
    print("tot      MissedTokens  T                     ", missing_tokens)

    try:
        temp_folder = os.path.join('.', str(uuid.uuid4()))
        delay, missing_tokens, mWERQuality = word_based_evaluation(evaluation_object, temp_folder)
        print(
            "tot      Delay         W                     ",
            str("{0:.3f}".format(round(delay, 3))),
            )
        print(
            "avg      Delay         W                     ",
            str("{0:.3f}".format(round((delay / evaluation_object.get('average_refernces_token_count')), 3))),
            )
        print("tot      MissedTokens  W                     ", missing_tokens)
        print("tot      mWERQuality   W                     ", mWERQuality)
    except:
        os.chdir(evaluation_object.get('current_path'))
        shutil.rmtree(temp_folder, ignore_errors=True)
        mwerSegmenter_error_message()


def candidate_delay_evaluation_with_partials(evaluation_object):
    delay, missing_tokens = time_based_evaluation(
        evaluation_object.get('Ts'),
        evaluation_object.get('candidate_sentences'),
        evaluation_object.get('OStt_sentences')
        )
    print(
            "tot      Delay         PT                    ",
            str("{0:.3f}".format(round(delay, 3))),
        )
    print(
            "avg      Delay         PT                    ",
            str("{0:.3f}".format(round((delay / evaluation_object.get('average_refernces_token_count')), 3))),
        )
    print("tot      MissedWords   PT                    ", missing_tokens)

    try:
        temp_folder = os.path.join('.', str(uuid.uuid4()))
        delay, missing_tokens, _ = word_based_evaluation(evaluation_object, temp_folder)
        print(
            "tot      Delay         PW                    ",
            str("{0:.3f}".format(round(delay, 3))),
            )
        print(
                "avg      Delay         PW                    ",
                str("{0:.3f}".format(round((delay / evaluation_object.get('average_refernces_token_count')), 3))),
            )
        print("tot      MissedTokens  PW                    ", missing_tokens)
    except:
        os.chdir(evaluation_object.get('current_path'))
        shutil.rmtree(temp_folder, ignore_errors=True)
        mwerSegmenter_error_message()


def get_Ts_with_align(input_aligns, references, OStt_sentences):
    aligns = list()
    for align_file_path in input_aligns:
        aligns.append(read_alignment_file(align_file_path))

    Ts = []
    for index in range(len(references)):
        reference = references[index]
        align = aligns[index]
        if len(align) != len(reference):
            print(
                "len align(",
                len(align),
                ") is not equal to len tt (",
                len(reference),
                ") Maybe GIZA++ failed?",
            )
            sys.exit(1)
        timestamps_table = get_timestamps_table(OStt_sentences, reference, align)
        Ts.append(timestamps_table)
    return Ts


def candidate_delay_evaluation_with_alignment(evaluation_object):
    delay, missing_tokens = time_based_evaluation(
        evaluation_object.get('Ts'),
        evaluation_object.get('candidate_sentences'),
        evaluation_object.get('OStt_sentences')
        )
    print(
        "tot      Delay         PTA                   ",
        str("{0:.3f}".format(round(delay, 3))),
        )
    print(
        "avg      Delay         PTA                   ",
        str("{0:.3f}".format(round((delay / evaluation_object.get('average_refernces_token_count')), 3))),
        )
    print("tot      MissedTokens  PTA                   ", missing_tokens)

    try:
        temp_folder = os.path.join('.', str(uuid.uuid4()))
        delay, missing_tokens, mWERQuality = word_based_evaluation(evaluation_object, temp_folder)
        print(
            "tot      Delay         PWA                   ",
            str("{0:.3f}".format(round(delay, 3))),
            )
        print(
            "avg      Delay         PWA                   ",
            str("{0:.3f}".format(round((delay / evaluation_object.get('average_refernces_token_count')), 3))),
            )
        print("tot      MissedTokens  PWA                   ", missing_tokens)
    except:
        os.chdir(evaluation_object.get('current_path'))
        shutil.rmtree(temp_folder, ignore_errors=True)
        mwerSegmenter_error_message()


def documantlevel_bleu_score_evaluation(references, candidate_sentences):
    bleu_score = calc_bleu_score_documentlevel(references, candidate_sentences)
    print(
        "tot      sacreBLEU     docAsWhole            ",
        str("{0:.3f}".format(round(bleu_score, 3))),
    )


def wordbased_segmenter_bleu_score_evaluation(evaluation_object):
        try:
            temp_folder = "./" + str(uuid.uuid4())
            sacre_score = calc_bleu_score_segmenterlevel(evaluation_object, temp_folder)
            print(
                "avg      sacreBLEU     mwerSegmenter         ",
                str("{0:.3f}".format(round(sacre_score, 3))),
            )
        except:
            os.chdir(evaluation_object.get('current_path'))
            shutil.rmtree(temp_folder, ignore_errors=True)
            mwerSegmenter_error_message()


def time_span_bleu_score_evaluation(evaluation_object):
        try:
            list_bleu_score_scores, avg_SacreBleu = calc_bleu_score_timespanlevel(evaluation_object)
            for x in list_bleu_score_scores:
                print(x)
            print(avg_SacreBleu)
        except:
            pass

def simple_timestamp_evaluation(inputs_object):
    current_path = os.getcwd()
    MovedWords = 1 # count of moving words to each side when we are using Time-based segmentation and word-based segmentation
    references = read_references(inputs_object.get('references', []))
    references_statistical_info(references) # print statistical info
    average_refernces_token_count = get_average_references_token_count(references)
    candidate_sentences = read_candidate_file(inputs_object.get('candidate'))
    OStt_sentences = read_ostt_file(inputs_object.get('ostt'))
    # delay evaluation
    Ts = []
    for reference in references:
        timestamps_table = get_timestamps_table(OStt_sentences, reference)
        Ts.append(timestamps_table)
    evaluation_object = {
        'Ts': Ts,
        'candidate_sentences': candidate_sentences,
        'OStt_sentences': OStt_sentences,
        'language': 'en',
        'SLTev_home': inputs_object.get('SLTev_home'),
        'current_path': current_path, 
        'MovedWords': MovedWords,
        'average_refernces_token_count': average_refernces_token_count,
        'references': references,
        'time_span': 3000
        }
    candidate_delay_evaluation_with_partials(evaluation_object)
    # bleu score evaluation
    wordbased_segmenter_bleu_score_evaluation(evaluation_object)
    #flicker evaluation
    print("tot      Flicker       count_changed_content ", int(calc_flicker_score(candidate_sentences)))


def normal_timestamp_evaluation(inputs_object):
    print_headers()
    current_path = os.getcwd()
    MovedWords = 1 # count of moving words to each side when we are using Time-based segmentation and word-based segmentation
    references = read_references(inputs_object.get('references', []))
    references_statistical_info(references) # print statistical info
    average_refernces_token_count = get_average_references_token_count(references)
    candidate_sentences = read_candidate_file(inputs_object.get('candidate'))
    OStt_sentences = read_ostt_file(inputs_object.get('ostt'))
    print_ostt_duration(OStt_sentences)
    Ts = []
    for reference in references:
        timestamps_table = get_timestamps_table_without_partials(OStt_sentences, reference)
        Ts.append(timestamps_table)
    evaluation_object = {
        'Ts': Ts,
        'candidate_sentences': candidate_sentences,
        'OStt_sentences': OStt_sentences,
        'language': 'en',
        'SLTev_home': inputs_object.get('SLTev_home'),
        'current_path': current_path, 
        'MovedWords': MovedWords,
        'average_refernces_token_count': average_refernces_token_count,
        'references': references,
        'time_span': 3000
        }
    candidate_delay_evaluation_without_partials(evaluation_object)

    Ts = []
    for reference in references:
        timestamps_table = get_timestamps_table(OStt_sentences, reference)
        Ts.append(timestamps_table)
    evaluation_object['Ts'] = Ts
    candidate_delay_evaluation_with_partials(evaluation_object)

    input_aligns = inputs_object.get('align')
    if input_aligns:
        Ts = get_Ts_with_align(input_aligns, references, OStt_sentences)
        evaluation_object['Ts'] = Ts
        candidate_delay_evaluation_with_alignment(evaluation_object)
    # bleu score evaluation
    documantlevel_bleu_score_evaluation(references, candidate_sentences)
    wordbased_segmenter_bleu_score_evaluation(evaluation_object)
    time_span_bleu_score_evaluation(evaluation_object)
    #flicker evaluation
    print("tot      Flicker       count_changed_Tokens  ", int(calc_revise_count(candidate_sentences)))
    print("tot      Flicker       count_changed_content ", int(calc_flicker_score(candidate_sentences)))
    print(
        "mean     flicker across sentences            ",
        str("{0:.3f}".format(round(calc_average_flickers_per_sentence(candidate_sentences), 3))),
        )
    print(
        "mean     flicker across whole documents      ",
        str("{0:.3f}".format(round(calc_average_flickers_per_tokens(candidate_sentences), 3))),
        )

def simple_mt_evaluation(inputs_object):
    current_path = os.getcwd()
    references = read_references(inputs_object.get('references', []))
    average_refernces_token_count = get_average_references_token_count(references)
    mt_sentences = read_candidate_file(inputs_object.get('mt'))

    evaluation_object = {
        'candidate_sentences': mt_sentences,
        'language': 'en',
        'SLTev_home': inputs_object.get('SLTev_home'),
        'current_path': current_path, 
        'average_refernces_token_count': average_refernces_token_count,
        'references': references,
        'time_span': 3000
        }

    # bleu score evaluation
    wordbased_segmenter_bleu_score_evaluation(evaluation_object)

def normal_mt_evaluation(inputs_object):
    print_headers()
    current_path = os.getcwd()
    references = read_references(inputs_object.get('references', []))
    references_statistical_info(references) # print statistical info
    average_refernces_token_count = get_average_references_token_count(references)
    mt_sentences = read_candidate_file(inputs_object.get('mt'))

    evaluation_object = {
        'candidate_sentences': mt_sentences,
        'language': 'en',
        'SLTev_home': inputs_object.get('SLTev_home'),
        'current_path': current_path, 
        'average_refernces_token_count': average_refernces_token_count,
        'references': references,
        'time_span': 3000
        }

    # bleu score evaluation
    documantlevel_bleu_score_evaluation(references, mt_sentences)
    wordbased_segmenter_bleu_score_evaluation(evaluation_object)













