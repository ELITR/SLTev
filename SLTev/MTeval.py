
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
            
        if hypo_file[1] == "mt":
            temp_flag = 0
            for file in gold_files["ref"]:
                if checkEmptyLine(file) == 1:
                    temp_flag = 1
                    continue
            if temp_flag == 1:
                continue
            
            print("Evaluating the file ", hypo_file[0], " in terms of translation quality against ", ' '.join(gold_files["ref"]))
            evaluator(ostt=gold_files["ref"][0], asr=True, tt=gold_files["ref"], align=[], mt=hypo_file[0], SLTev_home=sltev_home, simple=simple, time_stamp='False')
        else:
            eprint("Evaulation for ", hypo_file[0] ," failed, it is not a MT file")
            
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
