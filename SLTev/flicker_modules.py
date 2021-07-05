#!/usr/bin/env python


def calc_change_tokens(segment1, segment2):
    """
    Receiving two segments of a sentence and calculating the number of times the first segment tokens have been changed.

    :param segment1: a list of first segemnt words
    :param segment2: a list of second segemnt words
    :return count: count of revised words
    """

    count = 0
    for token in segment1:
        if token not in segment2:
            count += 1
    return count


def calc_revise_count(candidate_sentences):
    """
    Calculating the sum of the revises in all candidate sentences (by calculating the count of changed tokens).

    :param candidate_sentences: a list of candidate sentences (each sentence has a list of segments)
    :return flicker_size: the sum of revise score for all sentences
    """

    flicker_size = 0
    for sentence in candidate_sentences:
        first_segment = sentence[0][3:-1]
        for segment in sentence[1:]:
            flicker_size += calc_change_tokens(first_segment, segment[3:-1])
            first_segment = segment[3:-1]
    return flicker_size


def calc_flicker_count(segment1, segment2):
    """
    Receiving two segments (p1, p2) and calculates the distance between the first unmatched token until the first segment (p1) length.

    :param segment1: a list of first segemnt tokens
    :param segment2: a list of second segemnt tokens
    :return flicker_count: the flicker score between segment1 and segment2
    """

    flicker_count = 0
    for i in range(len(segment1)):
        if len(segment2) <= i:
            flicker_count = len(segment1) - i
            break
        elif segment1[i] != segment2[i]:
            flicker_count = len(segment1) - i
            break
    return flicker_count


def calc_flicker_score(candidate_sentences):
    """
    Calculating the sum of flickers for all MT sentences.

    :param candidate_sentences: a list of candidate sentences
    :return flicker_size: the sum of flicker score for all sentences
    """

    flicker_size = 0
    for sentence in candidate_sentences:
        first_segment = sentence[0][3:-1]
        for segment in sentence[1:]:
            f = calc_flicker_count(first_segment, segment[3:-1])
            flicker_size += f
            first_segment = segment[3:-1]
    return flicker_size


def calc_average_flickers_per_sentence(candidate_sentences):
    """
    Calculating the average of flicker per sentence.

    :param candidate_sentences: a list of candidate sentences (each sentence has a list of segments)
    :return : the average of flicker score for all sentences
    """

    sentence_flickers = []
    for sentence in candidate_sentences:
        sentence_flicker_size = 0
        first_segment = sentence[0][3:-1]
        for segment in sentence[1:]:
            f = calc_flicker_count(first_segment, segment[3:-1])
            sentence_flicker_size += f
            first_segment = segment[3:-1]
        if float(len(sentence[-1][3:-1])) == 0:
            continue
        average = sentence_flicker_size / float(len(sentence[-1][3:-1]))
        sentence_flickers.append(average)

    if len(sentence_flickers) == 0:
        return 0
    else:
        return sum(sentence_flickers) / float(len(sentence_flickers))


def calc_average_flickers_per_tokens(candidate_sentences):
    """
    Calculates the average of flicker per all tokens in candidate.

    :param candidate_sentences: a list of candidate sentences
    :return : the average of flicker score for all sentences
    """

    flicker_size = 0
    complet_token_count = 0
    for sentence in candidate_sentences:
        first_segment = sentence[0][3:-1]
        for segment in sentence[1:]:
            f = calc_flicker_count(first_segment, segment[3:-1])
            flicker_size += f
            first_segment = segment[3:-1]
        complet_token_count += float(len(sentence[-1][3:-1]))

    return float(flicker_size) / complet_token_count

