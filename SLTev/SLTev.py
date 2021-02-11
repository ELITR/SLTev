#!/usr/bin/env python 

import os
import sys
import argparse
from os import getcwd
import shutil
import git
import pkg_resources
from filelock import FileLock
from sacremoses import MosesTokenizer
from utilities import *
from ASRev import *
from evaluator import *

def main():
    parser = argparse.ArgumentParser(description="Evaluate outputs of SLT/MT/ASR systems in a reproducible way. Use custom inputs and references, or use inputs and references from https://github.com/ELITR/elitr-testset")
    parser.add_argument("-g", metavar="INDEX", help="generate an 'evaluation directory' with inputs for your system based on elitr-testset index called INDEX", type=str)
    parser.add_argument("--simple", help="report a simplified set of scores", action='store_true', default='False') 
    parser.add_argument("--outdir", "-O", help="put outputs (input files for -g, results for -e) in OUTDIR", default= "outdir", type=str)
    parser.add_argument("-T", "--elitr-testset", metavar="DIR", help="use DIR as git clone of elitr-testset instead of elitr-testset", default= "elitr-testset", type=str)
    parser.add_argument("-e", metavar="EVALDIR", help="evaluate evaluation directory EVALDIR", type=str)
    parser.add_argument("--commitid", help="use elitr-testset at commit COMMITID", default= "HEAD", type=str)
    args = parser.parse_args()
    
    #-----------add SLTev home to the path 
    try:
        sltev_home = pkg_resources.resource_filename('SLTev', '')
    except:
        sltev_home = os.path.dirname(os.path.realpath(sys.argv[0]))
    sys.path.insert(1, sltev_home)
    #sacremoses checking
    try:
        tokenize = MosesTokenizer().tokenize
        tokens = tokenize('Hello World!')
        assert tokens==['Hello', 'World', '!'], "sacremoses is badly installed, run as follow for fix: pip install --upgrade sacremoses" 
    except:
        eprint("sacremoses is badly installed, run as follow for fix:\n pip install --upgrade sacremoses")
        sys.exit(1)
    
    SLTev_commit_id = ''
    try:
        repo = git.Repo(os.path.split(sltev_home)[0])
        sha = repo.head.object.hexsha
        SLTev_commit_id = 'SLTev_' + repo.git.rev_parse(sha, short=True) + '-'
    except:
        SLTev_commit_id = ''
    #-----------check output directory 
    if args.e == None and args.g == None:
        parser.print_help()
        sys.exit(1)
        
    output_dir = ''
    if os.path.isdir(args.outdir):
        output_dir = args.outdir
    else:
        os.makedirs(args.outdir, exist_ok=True)
        output_dir = args.outdir

    #----get commit id
    elitr_path = args.elitr_testset
    try:
        repo = git.Repo(elitr_path)
        commit_id = repo.head.commit
    except:
        commit_id = ""
    if args.g != None:
        git_path = "https://github.com/ELITR/elitr-testset.git"
        if os.path.isdir(elitr_path):
            try:
                repo = git.Repo(elitr_path)
                repo.remotes.origin.pull()
                try:
                    population(elitr_path, os.environ.copy()['ELITR_CONFIDENTIAL_PASSWORD']) #link population
                except:
                    eprint("ELITR_CONFIDENTIAL_PASSWORD=... was not used")
                sha = repo.head.object.hexsha
                commit_id = 'elitrtestset_' + repo.git.rev_parse(sha, short=True)
                eprint("elitr-testset pulled")
            except:
                eprint ("pull from elitr-testset at "+elitr_path+" failed; is it a valid git clone? \nTest manually:\n  cd " + elitr_path + "; git pull")
                sys.exit(1)
        else:
            try:
                eprint("cloning elitr-testset repo to the ", elitr_path)
                git.Repo.clone_from(git_path, elitr_path)
                try:
                    population(elitr_path, os.environ.copy()['ELITR_CONFIDENTIAL_PASSWORD']) #link population
                except:
                    eprint("ELITR_CONFIDENTIAL_PASSWORD=... was not used")
                repo = git.Repo(elitr_path)
                sha = repo.head.object.hexsha
                commit_id = 'elitrtestset_' + repo.git.rev_parse(sha, short=True)
            except:
                eprint("cloning from elitr-testset failed, please check your internet conection")
                sys.exit(1)
        #------check commit id 
        if args.commitid != 'HEAD':
            try:
                repo = git.Repo(elitr_path)
                repo.git.checkout(args.commitid)
                eprint("checkout to ", args.commitid, " done.")
            except:
                eprint (args.commitid, ' is not valid')
        try:
            eprint('elitr-testset commit id is: ', commit_id)
            with FileLock(os.path.join(elitr_path, "SLTev.lock")):
                indice_file_path = os.path.join(elitr_path, "indices", args.g)
                populate(elitr_path, args.g, output_dir)
        except:
            eprint ("Generating index ",args.g ," failed. Check ", args.g, " index, it does not seem to exist, also check ", output_dir, ' for write permision'  )
        sys.exit(1)
    #----checking working directory    
    working_dir = args.e

    if os.path.isdir(working_dir):
        eprint ('working directory is ', working_dir)
    else:
        eprint(working_dir, ' is not exist.')
        sys.exit(1)
    #---make signature
    signature =  SLTev_commit_id
    if os.path.isdir(elitr_path):
        try:
            repo = git.Repo(elitr_path)
            sha = repo.head.object.hexsha
            elitr_commit_id = 'elitrtestset_' + repo.git.rev_parse(sha, short=True)
            signature = signature +  elitr_commit_id
        except:
            pass
        
    """
    Naming template:
    - OSt
    <file-name> . <language> . OSt
    -OStt
    <file-name> . <language> . OStt
    -align
    <file-name> . <source-lang> . <target-lang> . align
    -ASR/SLT/MT
    <file-name> . <source-lang> . <target-lang> . asr/slt/mt
    """
    
    submissions, inputs = split_submissions_inputs(working_dir) 
    orig_stdout = sys.stdout    
    if submissions == []:
        eprint("No SLT/ASR/MT files in working directory ", working_dir, " for evaluatin")
    for submission_file in submissions:
        #---check slt/asr/mt format
        state = check_input(submission_file)
        if state:
            continue
        status, tt, ostt, align = SLTev_inputs_per_submmision(submission_file, inputs)
        #empty checking for tt, submission_file
        temp_flag = 0
        for file in tt:
            if checkEmptyLine(file) == 1:
                temp_flag = 1
                continue
        if temp_flag == 1:
            continue
        if checkEmptyLine(submission_file) == 1:
            continue
        #----
        ost_as_ostt = 0
        if ostt == '':
            ost_as_ostt = 1
            path, file = os.path.split(submission_file)
            temp = file
            temp = temp.split('.')
            file =  '.'.join(temp[:-2]) + '.OSt'
            ostt = os.path.join(working_dir, file)
            if os.path.isfile(ostt):
                eprint("there is no OStt file for ", submission_file, " and we are using ", ostt, " instead of OStt")
                if checkEmptyLine(ostt) == 1:
                    continue
            else:
                eprint("evaluation for ", submission_file ," faild, file ", ostt, " is not exist")
                continue
        else:            
            #----checking number of C sentences in OStt and all tt must be equal
            if checkEmptyOSttLine(ostt) == 1:
                continue
            parity_state,error = partity_test(ostt, tt)
            if  parity_state == 0:
                eprint ("evaluation for ", submission_file ," faild, the number of Complete lines (C) in ", ostt, " and ", ' '.join(tt), ' are not equal')
                eprint(error)
                continue
        #----checking MT contain at least one C segment
        if MT_checking(submission_file) == 0:
            eprint("evaluation for ",submission_file , " faild, does not contain any Complete segment (C) for evaluation it must contain at least one C segment")
            continue
        if tt == []:
            eprint ("evaluation faild, no OSt file exist for ", submission_file)
            continue
        if ostt == '':
            eprint("evaluation faild, no OStt file exist for ", submission_file)
            continue
        if align == [] and 'asr' == removeDigits(status):
            eprint("Evaluating the file ", submission_file, " in terms of  WER score against ", tt[0])     
            out_name = os.path.join(output_dir, os.path.split(submission_file)[1]) + ".WER.out" 
            with open(out_name, 'w') as f:
                sys.stdout = f
                print('Signature: ', signature)
                ASRev(ost=tt[0], asr=submission_file, SLTev_home=sltev_home, simple=args.simple)
                sys.stdout = orig_stdout                
            eprint("Results saved in ", out_name)
            eprint("Evaluating the file ", submission_file, " in terms of translation quality against ", ' '.join(tt))
            out_name = os.path.join(output_dir, os.path.split(submission_file)[1]) + ".BLEU.out" 
            with open(out_name, 'w') as f:
                sys.stdout = f
                print('Signature: ', signature)
                evaluator(ostt=ostt, asr=True, tt=tt, align=[], mt=submission_file, SLTev_home=sltev_home, simple=args.simple, ostt_state=ost_as_ostt)
                sys.stdout = orig_stdout
            eprint("Results saved in ", out_name)
            continue
        if align == [] and 'asr' != removeDigits(status):
            eprint("Evaluating the file ", submission_file, " in terms of translation quality against ", ' '.join(tt))
            out_name = os.path.join(output_dir, os.path.split(submission_file)[1])+ ".BLEU.out" 
            with open(out_name, 'w') as f:
                sys.stdout = f
                print('Signature: ', signature)
                evaluator(ostt=ostt, asr=True, tt=tt, align=[], mt=submission_file, SLTev_home=sltev_home, simple=args.simple, ostt_state=ost_as_ostt)
                sys.stdout = orig_stdout
            eprint("Results saved in ", out_name)
            continue
        if align != [] and 'asr' != removeDigits(status):
            if len(align) != len(tt):
                eprint("Evaluating the file ", submission_file, " faild, the number of TT files and align files not equal")
                continue

            eprint("Evaluating the file ", submission_file, " in terms of translation quality against ", ' '.join(tt))
            out_name = os.path.join(output_dir, os.path.split(submission_file)[1]) + ".BLEU.out" 
            with open(out_name, 'w') as f:
                sys.stdout = f
                print('Signature: ', signature)
                evaluator(ostt=ostt, tt=tt, align=align, mt=submission_file, SLTev_home=sltev_home, simple=args.simple, ostt_state=ost_as_ostt)
                sys.stdout = orig_stdout
            eprint("Results saved in ", out_name)
            continue
            
if __name__ == "__main__":
    main()
