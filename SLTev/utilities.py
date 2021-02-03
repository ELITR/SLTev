import os
import sys
import requests
from os import getcwd
from urllib.request import urlopen
import subprocess as sp
import shutil
import logging
from pathlib import Path

######################################################################
# The utility modules use in the SLTev
######################################################################


# print to STDERR:
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def removeExtraSpaces(text):
    """
    remove free spaces in the input string 
    
    :param text: input string
    :return text: preprocessed output string
    """
    
    text = text.replace("\t", "")
    text = text.replace(" ", "")
    return text
   
def getIndices(indice_file_path, target_path):
    """
    copy files from the index to the target path.
    
    :param indice_file_path: a list of index files 
    :param target_path: path of the target directory
    """
    
    if indice_file_path[-5:] == '.link' or indice_file_path[-4:] == '.url':
        indice = removeExtraSpaces(indice_file_path)
        with open(indice) as link_f:
            link_files = link_f.readlines()
            for file in link_files:
                shutil.copy2(file, target_path)
    else:
        indice = removeExtraSpaces(indice_file_path)
        shutil.copy2(indice, target_path)

def chop_elitr_testset_prefix(path):
    """
    remove elitr-testset from the path 
    
    :param path: input path
    :return : preprocessed path string (removing elitr-testset from the path)
    """
    
    path_split = path.split('/')
    if path_split[0] == "elitr-testset": 
        return '/'.join(path_split[1:])
    else:
        raise ValueError("File name does not start with elitr-testset: "+path)

def populate(elitr_testset_path, indexname, target_path):
    """
    populate and copy index files from elitr-testset to the target directory
    
    :param elitr_testset_path: path of elitr-testset repo
    :param indexname: index name 
    :param target_path: path of the target directory
    """
    
    indice_file_path = os.path.join(elitr_testset_path, "indices", indexname)
    indices = [indice_file_path]
    indices_lines = []
    while indices != []:
        indice_file_path = indices.pop()
        with open(indice_file_path) as f:
            lines = f.readlines()
            lines = [i.strip() for i in lines if i.strip() != '']
        for line in lines:
            if line[:9] == '#include ':
                indice = removeExtraSpaces(line[9:])
                indice_path = os.path.join(elitr_testset_path, "indices", chop_elitr_testset_prefix(indice))
                indices.append(indice_path)
            elif line == "" or line[0] == '#':
                pass
            else:
                indices_lines.append(os.path.join(elitr_testset_path,
                  chop_elitr_testset_prefix(line)))
            
    for indice in indices_lines:
        if indice[0] == '#':
            pass
        else:
            print(indice + ' copied to ' + target_path)
            getIndices(indice, target_path)
    
def readIndice(file_path):
    """
    read an index file
    
    :param file_path: path of the index file
    :return out: a list of sub-filse in the index file
    """
    
    out = []
    with open(file_path, 'r') as f:
        out = f.readlines()
        out = ['/'.join(ele.strip().split('/')[1:]) for ele in out if ele.strip() != ''] 
    return out

def removeDigits(string):
    """
    remove digits from the input string
    
    :param string: input string
    :return result: preprocessed input string (removing digits from the path)
    """
   
    result = ''.join([i for i in string if not i.isdigit()])
    return result

def check_input(in_file):
    """
    check correctness of input files (MT/SLT/ASR files). 
    
    :param in_file: input MT/SLT/ASR file path
    """
   
    lines = open(in_file, 'r').readlines()
    state = 0 
    for i in range(len(lines)):
        line = lines[i].strip().split(' ')
        if line[0] != 'C' and line[0] != 'P':
            text = "File " + in_file + " and line " + str(i) + " is not in proper format  please correct this line as C/P 0 0 0 <text line>"
            state = 1
            eprint(text)
            break
        try:
            if int(line[1]) > -1 and int(line[2]) > -1 and int(line[3]) > -1:
                continue
        except:
            text = "File " + in_file + " and line " + str(i) + " is not in proper format  please correct this line as C/P 0 0 0 <text line>"
            state = 1
            eprint(text)
            break
            
    return  state 

def split_submissions_inputs(working_dir):
    """
    split submmisions and inputs files for SLTev evaluation from working directory (a folder which contains inputs (OStt/OSt/...) and submmisions (SLT/ASR/MT))
    
    :param working_dir: path of working directory. 
    :return submissions: a list of submmisione files
    :return inputs: a list of input files
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
    extract OSt (tt), align, OStt from the input files.
    
    :param submission_file: path of the submission file
    :param inputs: a list of input files (OSt/OStt/align) 
    :return status: state of the submission, a value among (asr, slt, mt)
    :return tt, ostt, align: OSt, OStt, align files  according to the submission file
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
    calculate the number of C lines in a list of lines
    
    :param list_line: a list of lines 
    :return counter: count of complete lines (C ) 
    """
    
    counter = 0
    for i in list_line:
        if i.strip().split()[0] == 'C':
            counter += 1
    return counter

def partity_test(ostt, tt_list):
    """
    checks equalness of  the number of C (complete) lines in OStt and OSt
       
    :param ostt: the path of ostt file
    :param tt_list: a list of tt (OSt) file pthes 
    :return status: error checking state (if safe it equal to 1 and otherwise is 0)   
    :return error: error string (if safe it equal with '')
    """
    
    status = 1
    error = '' 
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
    
    :param file: path of the MT/ASR/SLT file.
    :return status: error checking state (if safe it equal to 1 and otherwise is 0)  
    """
    
    status = 0
    with open(file) as f:
        mt_sentence = count_C_lines(f.readlines())
        if mt_sentence > 0:
            status = 1
    return status


