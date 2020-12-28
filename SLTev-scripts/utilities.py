import os
import sys
import requests
from os import getcwd
from urllib.request import urlopen
import subprocess as sp
import shutil
import logging

def runCMD(cmd):
    import os
    try:
        os.system(cmd)
        logging.info(cmd)
    except:
        logging.error('Error occurred ' + cmd)
        
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
                cmd = 'cp ' + file + ' ' + target_path
                runCMD(cmd)    
    else:
        indice = removeExtraSpaces(indice_file_path)
        cmd = 'cp ' + indice + ' ' + target_path
        runCMD(cmd)
        
def populate(indice_file_path, target_path):
    with open(indice_file_path) as f:
        lines = f.readlines()
        lines = [i.strip() for i in lines if i.strip() != '']
    indices = []
    
    for line in lines:
        #TODO RECURRENT #INCLUDE 
        if line[:9] == '#include ':
            indice = removeExtraSpaces(line[9:])
            indice_path = "./elitr-testset/indices/" + indice
            with open(indice_path) as f:
                sub_lines = f.readlines()
                sub_lines = [i.strip() for i in sub_lines if i.strip() != '']
            indices += sub_lines
        else:
            indices.append(line)
            
    for indice in indices:
        if indice[0] == '#':
            logging.info('skip this line')
        else:
            print(indice)
            getIndices(indice, target_path)
def gitLock():
    cmd = "touch " + "./elitr-testset/.git/index.lock"
    runCMD(cmd)
def gitUnLock():
    cmd = "rm " + "./elitr-testset/.git/index.lock"
    runCMD(cmd)
    
def downloadGitFile(url, filename):
    try:
        filedata = urlopen(url)
        datatowrite = filedata.read()

        with open(filename, 'wb') as f:
            f.write(datatowrite)
        return True
    except:
        return False
    
def readIndice(file_path):
    out = []
    with open(file_path, 'r') as f:
        out = f.readlines()
        out = ['/'.join(ele.strip().split('/')[1:]) for ele in out if ele.strip() != ''] 
    return out

def removeDigits(string):
    result = ''.join([i for i in string if not i.isdigit()])
    return result

def makeAlignIndexing(root):
    align_dict = {}
    for root, dirs, files in os.walk(root):   
        for f in files:
            try:
                file_path = os.path.join(root, f)
                split_name = f.split('.')
                file_type = split_name[-1]
                language = split_name[-2]
                if file_type == 'align' and language[:2] == 'TT':
                    la = removeDigits(language[2:])
                    try:
                        align_dict[la].append(file_path)
                    except:
                        align_dict[la] = [file_path]
            except:
                pass
    return align_dict

# def makeAlignIndexing(root):
#     align_dict = {'cs':[], 'de':[]}
#     for root, dirs, files in os.walk(root):   
#         for f in files:
#             file_path = os.path.join(root, f)
#             split_name = f.split('.')
#             file_type = split_name[-1]
#             language = split_name[-2]
#             if '.TTcs' in file_path and '.align' == file_path[-6:]:
#                 align_dict['cs'].append(file_path)
#             elif '.TTde' in file_path and '.align' == file_path[-6:]:
#                 align_dict['de'].append(file_path)
#     return align_dict

def makettIndexing(root):
    tt_dict = {}
    for root, dirs, files in os.walk(root):   
        for f in files:
            file_path = os.path.join(root, f)
            split_name = f.split('.')
            file_type = split_name[-1]
            if file_type[:2] == 'TT':
                la = removeDigits(file_type[2:])
                try:
                    tt_dict[la].append(file_path)
                except:
                    tt_dict[la] = [file_path]
                    
    return tt_dict

# def makettIndexing(root):
#     tt_dict = {'cs':[], 'de':[], 'en':[]}
#     for root, dirs, files in os.walk(root):   
#         for f in files:
#             file_path = os.path.join(root, f)
#             if '.TTcs' in file_path and '.align' != file_path[-6:]:
#                 tt_dict['cs'].append(file_path)
#             elif '.TTde' in file_path and '.align' != file_path[-6:]:
#                 tt_dict['de'].append(file_path)
#             elif '.OSt' in file_path and '.OStt' not in file_path and '.align' != file_path[-6:]:
#                 tt_dict['en'].append(file_path)
#     return tt_dict

def readCommitFile(commit_file):
    out = ''
    try:
        out = open(commit_file, 'r').readline()
    except:
        pass
    return out 

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

def makeosttIndexing(root):
    ostt_list = []
    for root, dirs, files in os.walk(root):   
        for f in files:
            file_path = os.path.join(root, f)
            if '.OStt' == file_path[-5:]:
                ostt_list.append(file_path)
    return ostt_list

def makeostIndexing(root):
    ost_list = []
    for root, dirs, files in os.walk(root):   
        for f in files:
            file_path = os.path.join(root, f)
            if '.OSt' == file_path[-4:]:
                ost_list.append(file_path)
    return ost_list


def getAlign(names, language, align_dict):
    out = []
    for i in align_dict[language]:
        for name in names:
            if name in i and i not in out:
                out.append(i)
    return out
def getostt(name, ostt_list):
    out = []
    for i in ostt_list:
        if name in i:
            out.append(i)
    return out

def getost(name, ost_list):
    out = []
    for i in ost_list:
        if name in i:
            out.append(i)
    return out

def gettt(name, language, tt_dict):
    out = []
    for i in tt_dict[language]:
        if name in i:
            out.append(i)
    return out

def getSLT(root):
    slt_files = []
    for root, dirs, files in os.walk(root):   
        for f in files:
            file_path = os.path.join(root, f)
            if '.slt' in f or '.asr' in f:
                slt_files.append(file_path)
    return slt_files

def getNameLanguageStatus(file_name):
    file_name = file_name.split('/')[-1]
    file_name = file_name.split('.')
    name = '.'.join(file_name[:-2])
    language = file_name[-2]
    asr_status = file_name[-1]
    return name, language, asr_status




