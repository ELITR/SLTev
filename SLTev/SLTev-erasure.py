
import pkg_resources
import os
import sys
import argparse
from utilities import *
from ASRev import *
from evaluator import *
### TODO LISTES
# CHECKING MT AND ASR files (adding C 0 0 0 to the start of each line)
# checking ostt and other files
# checking number lines in OStt and ref and source and OStt

def splitInputsHypos(inputs, format_orders):
    """
    splitting inputs and hypothesis  
    
    :param inputs: a list of the input file paths
    :param format_orders: a list of input formats in order
    :return hypos: a list of the hypothesis files [[hypo_path, format], []]
    :return gold_inputs: a list of the gold input files [{format:[file1, ...], ...}, {format:[file1, ...], ...},]
    """
    
    hypos = list()
    gold_inputs = list()
    temp = {}
    for inp, ords in zip(inputs, format_orders):
        if ords in ['asrt', 'asr', 'slt', 'mt']:
            hypos.append([inp, ords])
            
        else:
            if inp == 'and' and ords == 'and':
                gold_inputs.append(temp)
                temp = {}
            else:
                try:
                    temp[ords].append(inp)
                except:
                    temp[ords] = [inp]
    if temp != {}:
        gold_inputs.append(temp)
        
    return hypos, gold_inputs

def extractHypoGoldFiles(hypo_file, gold_inputs):
    """
    extracting gold files for the hypo
    
    :param hypo_file: path of the hypo file [hypo_path, format]
    :param gold_inputs: a list of gold files [[gold_path, format], []]
    :return error: if an error occurred it will be 1 and otherwise it will be 0
    :return out: a dict of gold files for the hypo {format:file_path}
    """
    
    error = 0
    hypo_name = os.path.split(hypo_file[0])[1]
    out = {}
    if hypo_file[1] == "asr":
        try:
            out["source"] = gold_inputs["source"]
        except:
            eprint("evaluation failed, the source file is not exit for ", hypo_file[0])
            error = 1
            
    elif hypo_file[1] == "asrt":
        try:
            out["source"] = gold_inputs["source"]
        except:
            eprint("evaluation failed, the source file is not exit for ", hypo_file[0])
            error = 1
        try:
            out["ostt"] = gold_inputs["ostt"]
        except:
            eprint("evaluation failed, the ostt file is not exit for ", hypo_file[0])
            error = 1
            
    elif hypo_file[1] == "mt":
        try:
            out["ref"] = gold_inputs["ref"]
        except:
            eprint("evaluation failed, the reference file is not exit for ", hypo_file[0])
            error = 1
            
    elif hypo_file[1] == "slt":
        out = {"ref":"", "ostt":"", "align":""}
        try:
            out["ref"] = gold_inputs["ref"]
        except:
            eprint("evaluation failed, the reference file is not exit for ", hypo_file[0])
            error = 1
        try:
            out["ostt"] = gold_inputs["ostt"]
        except:
            eprint("evaluation failed, the ostt file is not exit for ", hypo_file[0])
            error = 1
        try:
            out["align"] = gold_inputs["align"]
        except:
            out["align"] = []
    return out, error   

def main():
    parser = argparse.ArgumentParser(description="Evaluate outputs of SLT/MT/ASR systems in a reproducible way. Use custom inputs and references, or use inputs and references from https://github.com/ELITR/elitr-testset")
    parser.add_argument("-i", "--inputs", help="path of the input files", type=list, nargs='+' )
    parser.add_argument("-f", "--format_orders", help="format of the input files, fornat can be choiced from the following dictionary keys\n {source : source files, ref: reference, ostt: timestamped gold transcript, align: align files, \
                        slt: timestamped online MT hypothesis, mt: finalized MT hypothesis, asrt:timestamped ASR hypothesis \
                        asr:finalized ASR transcript} ", type=list, nargs='+' )
    parser.add_argument("--simple", help="report a simplified set of scores", action='store_true', default='False')
    args = parser.parse_args()
    
    #-----------add SLTev home to the path 
    try:
        sltev_home = pkg_resources.resource_filename('SLTev', '')
    except:
        sltev_home = os.path.dirname(os.path.realpath(sys.argv[0]))
        
        
    inputs = list()
    format_orders = list()
    for inp, ords in zip(args.inputs, args.format_orders):
        inputs.append(''.join(inp))
        format_orders.append(''.join(ords))
    # checking arguments
    if len(inputs) != len(format_orders):
        eprint("inputs length and format_orders is not equal.")
        sys.exit(1)
        
    hypos, gold_inputs = splitInputsHypos(inputs, format_orders)
    print('hypos', hypos)
    print('gold_inputs', gold_inputs)
    for hypo_file, gold_input in zip(hypos, gold_inputs):
        print('hypo_file', hypo_file)
        print('gold_input', gold_input)
        gold_files, error = extractHypoGoldFiles(hypo_file, gold_input)
        print('gold_files', gold_files)
        if error == 1:
            continue
        if hypo_file[1] == "asr":            
            print("Evaluating the file ", hypo_file[0], " in terms of  WER score against ", gold_files["source"][0])
            ASRev(ost=gold_files["source"][0], asr=hypo_file[0], SLTev_home=sltev_home, simple=args.simple)
            
        elif hypo_file[1] == "asrt":
            print("Evaluating the file ", hypo_file[0], " in terms of translation quality against ", ' '.join(gold_files["source"]))
            evaluator(ostt=gold_files["ostt"][0], asr=True, tt=gold_files["source"], align=[], mt=hypo_file[0], SLTev_home=sltev_home, simple=args.simple)
            
        elif hypo_file[1] == "slt":
            print("Evaluating the file ", hypo_file[0], " in terms of translation quality against ", ' '.join(gold_files["ref"]))
            evaluator(ostt=gold_files["ostt"][0], asr=True, tt=gold_files["ref"], align=gold_files["align"], mt=hypo_file[0], SLTev_home=sltev_home, simple=args.simple)
        
        elif hypo_file[1] == "mt":
            print("Evaluating the file ", hypo_file[0], " in terms of translation quality against ", ' '.join(gold_files["ref"]))
            evaluator(ostt=gold_files["ref"][0], asr=True, tt=gold_files["ref"], align=[], mt=hypo_file[0], SLTev_home=sltev_home, simple=args.simple, time_stamp='False')
    
if __name__ == "__main__":
    main()  
