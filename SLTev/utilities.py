import os
import sys
import requests
from os import getcwd
from urllib.request import urlopen
import subprocess as sp
import shutil
import logging
from pathlib import Path


def removeExtraSpaces(text):
    text = text.replace("\t", "")
    text = text.replace(" ", "")
    return text


   
def getIndices(indice_file_path, target_path):   
    if indice_file_path[-5:] == '.link' or indice_file_path[-4:] == '.url':
        indice = removeExtraSpaces(indice_file_path)
        with open(indice) as link_f:
            link_files = link_f.readlines()
            for file in link_files:
                shutil.copy2(file, target_path)
    else:
        indice = removeExtraSpaces(indice_file_path)
        shutil.copy2(indice, target_path)
        
def populate(indice_file_path, target_path):
    indices = [indice_file_path]
    indices_lines = []
    while indices != []:
        indice_file_path = indices.pop()
        with open(indice_file_path) as f:
            lines = f.readlines()
            lines = [i.strip() for i in lines if i.strip() != '']
        for line in lines:
            #TODO RECURRENT #INCLUDE 
            if line[:9] == '#include ':
                indice = removeExtraSpaces(line[9:])
                indice_path = "./elitr-testset/indices/" + indice
                indices.append(indice_path)
            else:
                indices_lines.append(line)
            
    for indice in indices_lines:
        if indice[0] == '#':
            pass
        else:
            print(indice + ' copied to ' + target_path)
            getIndices(indice, target_path)
            
def gitLock():
    Path("./elitr-testset/.git/index.lock").touch()
def gitUnLock():
    os.remove("./elitr-testset/.git/index.lock")
    
    
def readIndice(file_path):
    out = []
    with open(file_path, 'r') as f:
        out = f.readlines()
        out = ['/'.join(ele.strip().split('/')[1:]) for ele in out if ele.strip() != ''] 
    return out

def removeDigits(string):
    result = ''.join([i for i in string if not i.isdigit()])
    return result

def check_input(in_file):
    lines = open(in_file, 'r').readlines()
    state = 0 
    for i in range(len(lines)):
        line = lines[i].strip().split(' ')
        if line[0] != 'C' and line[0] != 'P':
            text = "File " + in_file + " and line " + str(i) + " is not in proper format  please correct this line as C/P 0 0 0 <text line>"
            state = 1
            print(text)
            break
        try:
            if int(line[1]) > -1 and int(line[2]) > -1 and int(line[3]) > -1:
                continue
        except:
            text = "File " + in_file + " and line " + str(i) + " is not in proper format  please correct this line as C/P 0 0 0 <text line>"
            state = 1
            print(text)
            break
            
    return  state 

def split_submissions_inputs(working_dir):
    """
    split submmisions and inputs files for SLTev evaluation
    """
    submissions = []
    inputs = []
    for root, dirs, files in os.walk(working_dir):   
        for f in files:
            file_path = os.path.join(working_dir, f)
            temp = removeDigits(f.split('.')[-1])
            if temp == 'slt' or temp == 'asr' or temp == 'mt':
                submissions.append(file_path)
            elif temp == 'OSt' or temp == 'OStt' or temp == 'align':
                inputs.append(file_path)
    return submissions, inputs

def SLTev_inputs_per_submmision(submission_file, inputs):
    """
    extact SLTev inputs (tt, align, OStt) from the input files. 
    """
    status, tt, ostt, align = '', [], '', []
    file_name1 = submission_file.split('/')[-1]
    file_name = '.'.join(file_name1.split('.')[:-3])
    source_lang = file_name1.split('.')[-3]
    target_lang = file_name1.split('.')[-2]
    status = file_name1.split('.')[-1]
    for file in inputs:
        input_name = file.split('/')[-1]
        input_name = input_name.split('.')
        if '.'.join(input_name[:-1]) + '.' + removeDigits(input_name[-1])  == file_name + '.' + target_lang + '.OSt':
            tt.append(file)
        elif '.'.join(input_name[:-1]) + '.' + removeDigits(input_name[-1])  == file_name + '.' + source_lang + '.OStt':
            ostt = file
        elif '.'.join(input_name[:-1]) + '.' + removeDigits(input_name[-1])  == file_name + '.' + source_lang + '.' + target_lang + '.align':
            align.append(file)
    return status, tt, ostt, align

    
def count_C_lines(list_line):
    """
    calculating the number of C lines in a list of lines
  
    """
    counter = 0
    for i in list_line:
        if i.strip().split()[0] == 'C':
            counter += 1
    return counter

def partity_test(ostt, tt_list):
    """
    checks the number of C(complete) lines in OStt and OSt
must be equal    
    """
    status = 1
    error = 0 
    with open(ostt) as f:
        ostt_sentence = count_C_lines(f.readlines())
    for file in tt_list:
        with open(file) as f:
            tt_sentence = len(f.readlines())
        if ostt_sentence != tt_sentence:
            status = 0 
            error = "The number of C segment (complete) in " + ostt  + " is "  + ostt_sentence  + " and number of lines in " + file + " is " + tt_sentence
            break
    return status, error

def MT_checking(file):
    """
    check MT that contain at least one C(Complete) segment
    """
    status = 0
    with open(file) as f:
        mt_sentence = count_C_lines(f.readlines())
        if mt_sentence > 0:
            status = 1
    return status

