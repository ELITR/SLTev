#!/usr/bin/env python3

import sys

def read_ostt(file_name):
    """
    
    Receives ostt file and extracts Completed sentences.  
    
    """
    
    in_file = open(file_name, 'r')
    line = in_file.readline()
    completed = []
    while line:
        temp = line.strip().split(" ")
        if temp[0] == 'C':
            completed.append(' '.join(temp[3:]))
        line = in_file.readline()
    in_file.close()
    return completed
#-------------------- initiate the parser

in_file = sys.argv[1]

if in_file == None:
    print('please insert ostt path')
    sys.exit(1)


#------------------------- read asr file
out_data = read_ostt(in_file)


#------------------------- write in file

temp = '\n'.join(out_data)
print(temp)