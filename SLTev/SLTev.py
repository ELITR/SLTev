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
import ASReval
import MTeval
import SLTeval

def main():
    parser = argparse.ArgumentParser(description="Evaluate outputs of SLT/MT/ASR systems in a reproducible way. Use custom inputs and references, or use inputs and references from https://github.com/ELITR/elitr-testset")
    parser.add_argument("-g", metavar="INDEX", help="generate an 'evaluation directory' with inputs for your system based on elitr-testset index called INDEX", type=str)
    parser.add_argument("--simple", help="report a simplified set of scores", action='store_true', default='False')
    parser.add_argument("--aggregate", help="aggregate all scores and shows them in the standard output instead of produce score files", action='store_true', default='False')
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
    
    submissions, input_files = split_submissions_inputs(working_dir) 
    orig_stdout = sys.stdout    
    if submissions == []:
        eprint("No SLT/ASR/MT files in working directory ", working_dir, " for evaluatin")
    for submission_file in submissions:

        status, tt, ostt, align = SLTev_inputs_per_submission(submission_file, input_files)
        # making inputs and format_orders
        inputs = [submission_file] 
        format_orders = [removeDigits(status)]
        for i in tt:
            if removeDigits(status) == "asr" or removeDigits(status)== "asrt":
                inputs.append(i)
                format_orders.append("source")
            elif removeDigits(status) == "mt" or removeDigits(status)== "slt":
                inputs.append(i)
                format_orders.append("ref")
        if ostt != "":
            inputs.append(ostt)
            format_orders.append("ostt")
        for i in align:
            inputs.append(i)
            format_orders.append("align")
        # checking tt counts
        if tt == []:
            eprint("Evaluation failed, ther is no tt files for the ", submission_file)
            continue
        if removeDigits(status) == 'asr' :           
            if args.aggregate != 'False':
                print("Evaluating the file ", submission_file, " in terms of  WER score against ", tt[0])
                print('Signature: ', signature)
                ASReval.main(inputs, format_orders, args.simple)
            else:
                out_name = os.path.join(output_dir, os.path.split(submission_file)[1]) + ".WER.out" 
                with open(out_name, 'w') as f:
                    sys.stdout = f
                    print('Signature: ', signature)
                    ASReval.main(inputs, format_orders, args.simple)
                    sys.stdout = orig_stdout                
                eprint("Results saved in ", out_name)
                
        if removeDigits(status) == 'asrt' :       
            if args.aggregate != 'False':
                print("Evaluating the file ", submission_file, " in terms of translation quality against ", ' '.join(tt))
                print('Signature: ', signature)
                ASReval.main(inputs, format_orders, args.simple)
            else:
                out_name = os.path.join(output_dir, os.path.split(submission_file)[1]) + ".BLEU.out" 
                with open(out_name, 'w') as f:
                    sys.stdout = f
                    print('Signature: ', signature)
                    ASReval.main(inputs, format_orders, args.simple)
                    sys.stdout = orig_stdout
                eprint("Results saved in ", out_name)
            continue
            
        if removeDigits(status) == "mt":        
            if args.aggregate != 'False':
                print("Evaluating the file ", submission_file, " in terms of translation quality against ", ' '.join(tt))
                print('Signature: ', signature)
                MTeval.main(inputs, format_orders, args.simple)
            else:
                out_name = os.path.join(output_dir, os.path.split(submission_file)[1])+ ".BLEU.out" 
                with open(out_name, 'w') as f:
                    sys.stdout = f
                    print('Signature: ', signature)
                    MTeval.main(inputs, format_orders, args.simple)
                    sys.stdout = orig_stdout
                eprint("Results saved in ", out_name)
            continue
            
        if removeDigits(status) == "slt":            
            if args.aggregate != 'False':
                print("Evaluating the file ", submission_file, " in terms of translation quality against ", ' '.join(tt))
                print('Signature: ', signature)
                SLTeval.main(inputs, format_orders, args.simple)
            else:
                out_name = os.path.join(output_dir, os.path.split(submission_file)[1]) + ".BLEU.out" 
                with open(out_name, 'w') as f:
                    sys.stdout = f
                    print('Signature: ', signature)
                    SLTeval.main(inputs, format_orders, args.simple)
                    sys.stdout = orig_stdout
                eprint("Results saved in ", out_name)
            continue
            
if __name__ == "__main__":
    main()
