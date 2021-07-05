#!/usr/bin/env python

import sacrebleu
from files_modules import quality_segmenter


def calc_bleu_score_documentlevel(references, candiate_sentences):
    """
    Calculating bleu score by using sacrebleu module. In this method, all Complete segmented in MT is sys document and all Ts sentences is ref document.

    :param references: a list of references
    :param candiate_sentences: a list of candidate senetnces (partial and complete segments)
    :return sacre_bleu_score: the bleu score
    """

    merge_mt_sentences = []
    for i in range(len(candiate_sentences)):
        mt = candiate_sentences[i][-1][3:-1]
        merge_mt_sentences += mt
    merge_references_sentences = []
    for ref in references:
        l = []
        for sentence in ref:
            l.append(" ".join(sentence[:-1]))
        merge_references_sentences.append(l)

    refs = [" ".join(i) for i in merge_references_sentences]
    sys = " ".join(merge_mt_sentences[:])

    bleu_sacre = sacrebleu.sentence_bleu(sys, refs)
    sacre_bleu_score = bleu_sacre.score
    return sacre_bleu_score


def calc_bleu_score_segmenterlevel(evaluation_object, temp_folder):
    """
    Calculating bleu score sentence by sentence with using mwerSegmenter.

    :param evaluation_object: a pair keys of evaluation elements
    :return sacre_blue_score: the bleu score
    """

    merge_references_sentences = []
    for ref in evaluation_object.get('references'):
        temp = []
        for sentence in ref:
            temp.append(" ".join(sentence[:-1]))
        merge_references_sentences.append(temp)

    segmenter_sentence, _ = quality_segmenter(evaluation_object, temp_folder)
    sys = [" ".join(i) for i in segmenter_sentence]
    refs = merge_references_sentences[:]
    bleu_sacre = sacrebleu.corpus_bleu(sys, refs)
    sacre_bleu_score = bleu_sacre.score
    return sacre_bleu_score


def build_candidate_timestamp_table(sentence_segments):
    """
    Receiving segments of the candaiate sentences and calculates timestamp table of uniq tokens 

    :param sentence_segments: a list of a sentence segments
    :return uniq_words_estimate_time: a dictionary which key is one token of candidate sentence and value is the display time of the
    token.
    """

    uniq_tokens_show_time = {}
    uniq_tokens_estimate_time = {}
    for token in sentence_segments[-1][3:-1]:
        uniq_tokens_estimate_time[token] = 0
        uniq_tokens_show_time[token] = 0

    for segment in sentence_segments:
        tokens = segment[3:-1]
        step = (float(segment[2]) - float(segment[1])) / len(tokens)
        for token in segment[3:-1]:
            try:
                if uniq_tokens_show_time[token] == 0:
                    uniq_tokens_show_time[token] = float(segment[0])
                    uniq_tokens_estimate_time[token] = float(
                        float(segment[1]) + ((tokens.index(token) + 1) * step)
                    )
            except:
                pass
    return uniq_tokens_estimate_time


def get_candidate_sentences_per_time_span(evaluation_object, candidate_end_time):
    time_span = evaluation_object.get('time_span')
    start = 0
    end = time_span
    mt_sentences = list()
    while start <= float(candidate_end_time):
        l = []
        for i in range(len(evaluation_object.get('candidate_sentences'))):
            estimat_word_times = build_candidate_timestamp_table(evaluation_object.get('candidate_sentences')[i])
            for k, v in estimat_word_times.items():
                if v >= start and v <= end:
                    l.append(k)
        mt_sentences.append(l)
        start += time_span
        end += time_span
    return mt_sentences


def get_reference_sentences_per_time_span(evaluation_object, candidate_end_time):
    references_sentences = list()
    time_span = evaluation_object.get('time_span')
    start = 0
    end = time_span
    while start <= float(candidate_end_time):
        l = []
        for i in range(len(evaluation_object.get('Ts'))):
            s = []
            for sentence in evaluation_object.get('Ts')[i]:
                for k, v in sentence.items():
                    if v >= start and v <= end:
                        s.append(k)
            l.append(s)
        references_sentences.append(l)
        start += time_span
        end += time_span
    return references_sentences

def calc_bleu_score_timespanlevel(evaluation_object):
    """
    :param evaluation_object: a pair keys of evaluation elements
    :return bleu_scores: the average bleu score between time-span scores
    :return avg_SacreBleu: a list of time-step scores
    """
    time_span = evaluation_object.get('time_span')
    candidate_end_time = float(evaluation_object.get('candidate_sentences')[-1][-1][2])
    mt_sentences = get_candidate_sentences_per_time_span(evaluation_object, candidate_end_time)
    references_sentences = get_reference_sentences_per_time_span(evaluation_object, candidate_end_time)

    start = 0
    end = time_span
    sacreBLEU_list = []
    bleu_scores = []
    for t in range(len(mt_sentences)):
        try:
            sys = " ".join(mt_sentences[t])
            refs = [" ".join(ref) for ref in references_sentences[t]]
            bleu_sacre = sacrebleu.sentence_bleu(sys, refs)
            sacre_blue_score = bleu_sacre.score
            text1 = (
                "detailed sacreBLEU     span-"
                + format(start, "06")
                + "-"
                + format(end, "06")
                + "     "
                + str("{0:.3f}".format(sacre_blue_score))
            )
            sacreBLEU_list.append(sacre_blue_score)
            start += time_span
            end += time_span
            bleu_scores.append(text1)
        except:
            pass
    avg_SacreBleu = "avg      sacreBLEU     span*                  " + str(
        "{0:.3f}".format(round((sum(sacreBLEU_list) / len(sacreBLEU_list)), 3))
    )
    return bleu_scores, avg_SacreBleu

