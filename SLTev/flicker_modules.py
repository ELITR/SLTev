#!/usr/bin/env python

import argparse
import sys
import sacrebleu
import subprocess as sp
import os
from mosestokenizer import *
from files_modules import *
def calc_change_words(segment1, segment2):
    """
    Receiving two segments and calculating the number of times the first segment words have been changed.
    """
    
    count =0 
    for word in segment1:
        if word not in segment2:
            count += 1
    return count

def calc_revise(MT):
    """
    Calculating the sum of the revises in all MT sentences (by calculating the count of changed words).
    """
    
    flicker_size = 0
    for sentence in MT:
        first_segment = sentence[0][3:-1]
        for segment in sentence[1:]:
            flicker_size += calc_change_words(first_segment, segment[3:-1])
            first_segment = segment[3:-1]
    return flicker_size

def calc_flicker_count(segment1, segment2):
    """
    Receiving two segments (p1, p2) and calculates the distance between the first unmatched word until p1 length. 
    """
    
    f = 0 
    for i in range (len(segment1)):
        if len(segment2) <= i: 
            f = len(segment1) - i
            break
        elif segment1[i] != segment2[i]:
            f = len(segment1) - i
            break 
    return f

def calc_flicker(MT):
    """
    Calculating sum of flickers in all MT sentences.  
    """
    
    flicker_size = 0
    for sentence in MT:
        first_segment = sentence[0][3:-1]
        for segment in sentence[1:]:
            f = calc_flicker_count(first_segment, segment[3:-1])
            flicker_size += f
            first_segment = segment[3:-1]
    return flicker_size

def calc_average_flickers_per_sentence(MT):
    """
    Calculateing the average of flicker per sentence. 
    """
    
    sentence_flickers = []
    for sentence in MT:
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
            f = calc_flicker_count(first_segment, segment[3:-1])
            flicker_size += f
            first_segment = segment[3:-1]
        complet_word_count += float(len(sentence[-1][3:-1]))
    return float(flicker_size) / complet_word_count

