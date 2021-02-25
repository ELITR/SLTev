
import pkg_resources
import os
import sys
import argparse
from utilities import *
from ASRev import *
from evaluator import *

def main(inputs=[], format_orders=[], simple="False"):
    #-----------add SLTev home to the path 
    try:
        sltev_home = pkg_resources.resource_filename('SLTev', '')
    except:
        sltev_home = os.path.dirname(os.path.realpath(sys.argv[0]))
        
        
    # checking arguments
    if len(inputs) != len(format_orders):
        eprint("inputs length and format_orders is not equal.")
        sys.exit(1)
        
    hypos, gold_inputs = splitInputsHypos(inputs, format_orders)

    for hypo_file in hypos:
        gold_files, error = extractHypoGoldFiles(hypo_file, gold_inputs[0])
        if error == 1:
            continue
            
        if hypo_file[1] == "asr":
            # SOURCE cheching
            temp_flag = 0
            for file in gold_files["source"]:
                if checkEmptyLine(file) == 1:
                    temp_flag = 1
                    continue
            if temp_flag == 1:
                continue
            print("Evaluating the file ", hypo_file[0], " in terms of  WER score against ", gold_files["source"][0])
            ASRev(ost=gold_files["source"][0], asr=hypo_file[0], SLTev_home=sltev_home, simple=simple)
            
        elif hypo_file[1] == "asrt":
            # SOURCE cheching
            temp_flag = 0
            for file in gold_files["source"]:
                if checkEmptyLine(file) == 1:
                    temp_flag = 1
                    continue
            if temp_flag == 1:
                continue
            # OStt checking
            if checkEmptyOSttLine(gold_files["ostt"][0]) == 1:
                continue
            parity_state,error = partity_test(gold_files["ostt"][0], gold_files["source"])
            if  parity_state == 0:
                eprint ("Evaulation for ", hypo_file[0] ," failed, the number of Complete lines (C) in ", gold_files["ostt"][0], " and ", ' '.join(gold_files["source"]), ' are not equal')
                eprint(error)
                continue
            # submission checking 
            state = check_input(hypo_file[0])    
            print("Evaluating the file ", hypo_file[0], " in terms of translation quality against ", ' '.join(gold_files["source"]))
            evaluator(ostt=gold_files["ostt"][0], asr=True, tt=gold_files["source"], align=[], mt=hypo_file[0], SLTev_home=sltev_home, simple=simple)
        else:
            eprint("Evaulation for ", hypo_file[0] ," failed, it is not a ASR file")
      
        
def mainPoint():
    args = submissionArgument()
    inputs = list()
    format_orders = list()
    for inp, ords in zip(args.inputs, args.format_orders):
        inputs.append(''.join(inp))
        format_orders.append(''.join(ords))
    main(inputs, format_orders, args.simple) 
    
if __name__ == "__main__":
    args = submissionArgument()
    inputs = list()
    format_orders = list()
    for inp, ords in zip(args.inputs, args.format_orders):
        inputs.append(''.join(inp))
        format_orders.append(''.join(ords))
    main(inputs, format_orders, args.simple)   
