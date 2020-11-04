import os
import sys
import argparse
import requests
from os import getcwd
from urllib.request import urlopen
import subprocess as sp
import shutil
from utilities import *

# initiate the parser
parser = argparse.ArgumentParser(description="")
parser.add_argument("-g", help="eliter index name for download files ", const=False, default=False, nargs='?', type=str)
parser.add_argument("-o", help="path of the output dir (default is ./ )", default = "./", type=str)
parser.add_argument("--audio", "-audio", help="if exist just audios saved ", const=True, default=False, nargs='?')
parser.add_argument("--clean", "-clean", help="if exist clean all files in the ./SLTev-cache/", const=True, default=False, nargs='?')
parser.add_argument("-e", help="eliter index name for evaluate files ", const=False, default=False, nargs='?', type=str)
parser.add_argument("-i", help="slt output directory ", const=False, default=False, nargs='?', type=str)
parser.add_argument("--outdir", help="slt output results directory (output of the SLTev) ", default= "./outdir/", type=str)
parser.add_argument("--offline", "-offline", help="if exist just using cache folder ", const=True, default=False, nargs='?')
parser.add_argument("-outfile", help="if exist,standard evaluate output saved in a file.", default=False, nargs='?', type=str)
parser.add_argument("-f", help="eliter file name", type=str)
parser.add_argument("-alignment", help="path of the alignment file", type=list, nargs='+' )
parser.add_argument("-t", help="length times for the bleu  calculation per time ", default = 3000, type=int)
# read arguments from the command line
args = parser.parse_args()
#------- make a temp directory 

#-------actine mwerSegmenter
cmd = "chmod +x mwerSegmenter"
os.system(cmd)

cache_path = "./SLTev-cache/"

if args.clean == True and os.path.isdir(cache_path):
    shutil.rmtree(cache_path)

if os.path.isdir(cache_path):
    pass
else:
    os.mkdir(cache_path)
    ostt_other_path = cache_path + "OStt-tt-files/"
    os.mkdir(ostt_other_path)


if os.path.isdir(args.o):
    pass
else:
    print ("path ", args.o, " is not exist.")
    sys.exit(1)
#----------------get commit id
url = "https://github.com/ELITR/elitr-testset"
cmd =  "git ls-remote " + url + " HEAD"
commit_id = sp.getoutput(cmd).split('\t')[0]
original_stdout = sys.stdout
if args.g != False:
    print("commit id is ", commit_id) 
    git_path = "https://raw.githubusercontent.com/ELITR/elitr-testset/master/"
    indice_path = git_path + "indices/" + args.g
    file_path = cache_path + args.g
    status = downloadGitFile(indice_path, file_path)
    if status == False:
        print(indice_path, " not found")
        sys.exit(1)
    else:
        indice_files = readIndice(file_path)
        if args.audio == False:
            for file in  indice_files:
                file_path = git_path + file
                out_path = args.o + file.split('/')[-1]
                status = downloadGitFile(file_path, out_path)
                if status == True:
                    print(file_path , " downloaded.")
                else:
                    print(file_path , " not found.")
                    
        else:
            for file in  indice_files:
                if '.mp3' == file[-4:] or '.aac' == file[-4:]:
                    file_path = git_path + file
                    out_path = args.o + file.split('/')[-1]
                    status = downloadGitFile(file_path, out_path)
                    if status == True:
                        print(file_path , " downloaded.")
                    else:
                        print(file_path , " not found.")
#---------------Download OStt and tt files per indice id and save in the  ./SLTev-cache/OStt-tt-files/ folder. 
if args.e != False and args.offline == False:
    git_path = "https://raw.githubusercontent.com/ELITR/elitr-testset/master/"
    indice_path = git_path + "indices/" + args.e
    file_path = cache_path + args.e
    status = downloadGitFile(indice_path, file_path)
    if status == False:
        print(indice_path, " not found")
        sys.exit(1)
    else:
        indice_files = readIndice(file_path)
        ostt_de_files_path = cache_path + 'OStt-tt-files/'
        if os.path.isdir(ostt_de_files_path):
            pass
        else:
            os.mkdir(ostt_de_files_path)
        for file in  indice_files:
            if '.OStt' == file[-5:] or '.OSt' == file[-4:] or '.TTde' == file[-5:] or '.TTcs' == file[-5:] or '.TTcs1' == file[-6:] or '.TTcs2' == file[-6:] or '.align' == file[-6:]:
                file_path = git_path + file
                out_path = ostt_de_files_path + file.split('/')[-1]
                status = downloadGitFile(file_path, out_path)
                if status == True:
                    print(file_path , " downloaded.")
                else:
                    print(file_path , " not found.")

# #----------------download giza-outs
# gizaouts_git_path = "https://github.com/ELITR/elitr-testset/tree/master/indices" 
# if args.e != False and args.offline == False:
#     cmd = "gitdir " + gizaouts_git_path
#     os.system(cmd)
#     cmd = "rm -r ./SLTev-cache/giza-outs/"
#     os.system(cmd)
#     cmd = "mv ./giza-outs/ ./SLTev-cache/"
#     os.system(cmd)
    
align_root_path = "./SLTev-cache/OStt-tt-files/"
ostt_root_path = "./SLTev-cache/OStt-tt-files/"
tt_root_path = "./SLTev-cache/OStt-tt-files/"

align_dict = makeAlignIndexing(align_root_path)
ostt_list = makeosttIndexing(ostt_root_path)
tt_dict = makettIndexing(tt_root_path)

#--------------- evaluate per all cache files    
if  args.e != False and args.f != None: 
    name, language, asr_status  = getNameLanguageStatus(args.f)
    #------check the input file
    if os.path.isfile(args.f):
        pass
    else:
        print(args.f, " is not exist.")
        sys.exit(1)

    #---------- get OStt files
    ostt_file = getostt(name, ostt_list)
    tt_file = gettt(name, language, tt_dict) 
    
    #-----------check OStt and tt files (for exist)
    if len(ostt_file) == 0:
        print("commit id is ", commit_id)
        print("OStt file does not exist.")
        sys.exit(1)
    if len(tt_file) == 0:
        print("commit id is ", commit_id)
        print("tt file does not exist.")
        sys.exit(1)
    #------- get align file
    align_file = None
    if asr_status != 'asr':
        if args.alignment == None:
            a_name = [k.split('/')[-1] for k in tt_file]
            align_file = getAlign(a_name, language, align_dict)
            if align_file == None:
                print("The alignment is not exist for ", args.f, ", you can use -alignment for manual alignment" )
                sys.exit(1)
        else:
            align_file = []
            for i in args.alignment:
                align_file.append(''.join(i))
    #--------evaluation
    if asr_status == 'asr':
        if args.outfile == False:
            print("commit id is ", commit_id) 
            cmd = "python evaluator.py --ostt " + ' '.join(ostt_file) + " --tt " + ' '.join(tt_file) + " --mt " + args.f + " --asr True " + " --b_time " + str(args.t)
            os.system(cmd)
        else:
            with open(args.outfile, 'w') as f:
                sys.stdout = f
                print("commit id is ", commit_id)
                sys.stdout = original_stdout
            cmd = "python evaluator.py --ostt " + ' '.join(ostt_file) + " --tt " + ' '.join(tt_file) + " --mt " + args.f + " --asr True " + " --b_time " + str(args.t) + " >> " + args.outfile
            os.system(cmd)
            
            
    else:
        if len(tt_file) != len(align_file):
            print("count of tt files and align files not equel.")
            sys.exit(1)
        if args.outfile == False:
            print("commit id is ", commit_id)
            cmd = "python evaluator.py --ostt " + ' '.join(ostt_file) + " --tt " + ' '.join(tt_file) + " --mt " + args.f + " --align " + ' '.join(align_file) + " --b_time " + str(args.t)
            os.system(cmd)
        else:
            with open(args.outfile, 'w') as f:
                sys.stdout = f
                print("commit id is ", commit_id)
                sys.stdout = original_stdout
            cmd = "python evaluator.py --ostt " + ' '.join(ostt_file) + " --tt " + ' '.join(tt_file) + " --mt " + args.f + " --align " + ' '.join(align_file) + " --b_time " + str(args.t) + " >> " + args.outfile
            os.system(cmd)
    
    
if args.e != False and args.i != False:
    #------check input
    if os.path.isdir(args.outdir):
        pass
    else:
        print(args.outdir, " is not exist, we will create it. ")
        cmd = "mkdir -p " + args.outdir
        os.system(cmd)
    
    slt_files = getSLT(args.i)
    for slt_file in slt_files:
        name, language, asr_status  = getNameLanguageStatus(slt_file)
        #------check the input file
        if os.path.isfile(slt_file):
            pass
        else:
            print(slt_file, " is not exist.")
            sys.exit(1)

        #---------- get OStt file
        ostt_file = getostt(name, ostt_list)
        tt_file = gettt(name, language, tt_dict)
        
        #------------check OStt and tt files (check for existing)
        if asr_status != 'asr':
            out_name = args.outdir + name + '.' + language + '.slt.out'
        else:
            out_name = args.outdir + name +'.'+ language +'.asr.out'
            
        if len(ostt_file) == 0:
            with open(out_name, 'w') as f:
                sys.stdout = f
                print("commit id is ", commit_id)
                print("OStt file does not exist.")
                sys.stdout = original_stdout
                continue
        if len(tt_file) == 0:
            with open(out_name, 'w') as f:
                sys.stdout = f
                print("commit id is ", commit_id)
                print("tt file does not exist.")
                sys.stdout = original_stdout
                continue
        
        #------- get align file
        align_file = None
        if asr_status != 'asr':
            if args.alignment == None:
                a_name = [k.split('/')[-1] for k in tt_file]
                align_file = getAlign(a_name, language, align_dict)
                if align_file == None:
                    print("The alignment is not exist for ", args.f, ", you can use -alignment for manual alignment" )
                    sys.exit(1)
            else:
                align_file = []
                for i in args.alignment:
                    align_file.append(''.join(i)) 
                    
        if asr_status == 'asr':
            out_name = args.outdir + name +'.'+ language +'.asr.out'
            with open(out_name, 'w') as f:
                sys.stdout = f
                print("commit id is ", commit_id)
                sys.stdout = original_stdout
            if len(ostt_file) != 0 and len(tt_file) != 0:         
                cmd = "python evaluator.py --ostt " + ' '.join(ostt_file) + " --tt " + ' '.join(tt_file) + " --mt " + slt_file + " --asr True " + " --b_time " + str(args.t) + " >> " + out_name
                os.system(cmd)     
        else:
            if len(tt_file) != len(align_file):
                print("count of tt files and align files not equel.")
                sys.exit(1)
            out_name = args.outdir + name + '.' + language + '.slt.out'
            with open(out_name, 'w') as f:
                sys.stdout = f
                print("commit id is ", commit_id)
                sys.stdout = original_stdout
            if len(ostt_file) != 0 and len(tt_file) != 0:
                cmd = "python evaluator.py --ostt " + ' '.join(ostt_file) + " --tt " + ' '.join(tt_file) + " --mt " + slt_file + " --align " + ' '.join(align_file) + " --b_time " + str(args.t) + " >> " + out_name
                os.system(cmd)
