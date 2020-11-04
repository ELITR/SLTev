import os
import sys
import requests
from os import getcwd
from urllib.request import urlopen
import subprocess as sp
import shutil

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

def makeAlignIndexing(root):
    align_dict = {'cs':[], 'de':[]}
    for root, dirs, files in os.walk(root):   
        for f in files:
            file_path = os.path.join(root, f)
            if '.TTcs' in file_path and '.align' == file_path[-6:]:
                align_dict['cs'].append(file_path)
            elif '.TTde' in file_path and '.align' == file_path[-6:]:
                align_dict['de'].append(file_path)
    return align_dict

def makettIndexing(root):
    tt_dict = {'cs':[], 'de':[], 'en':[]}
    for root, dirs, files in os.walk(root):   
        for f in files:
            file_path = os.path.join(root, f)
            if '.TTcs' in file_path and '.align' != file_path[-6:]:
                tt_dict['cs'].append(file_path)
            elif '.TTde' in file_path and '.align' != file_path[-6:]:
                tt_dict['de'].append(file_path)
            elif '.OSt' in file_path and '.OStt' not in file_path and '.align' != file_path[-6:]:
                tt_dict['en'].append(file_path)
    return tt_dict

def makeosttIndexing(root):
    ostt_list = []
    for root, dirs, files in os.walk(root):   
        for f in files:
            file_path = os.path.join(root, f)
            if '.OStt' in file_path:
                ostt_list.append(file_path)
    return ostt_list


def getAlign(names, language, align_dict):
    out = []
    for i in align_dict[language]:
        for name in names:
            if name in i:
                out.append(i)
    return out
def getostt(name,ostt_list):
    out = []
    for i in ostt_list:
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



