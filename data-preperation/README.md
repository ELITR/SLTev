
You can use these scripts to prepare data for use in SLTev.  


### Extract OSt from OStt 

``` {r, engine='python'} 
$ ./giza++/transcript_to_source ostt_file > source_ref
```
	- Input-files:
        - ostt_file is the input OStt file. 
        - source_ref is the output file. 
    e.g. ./giza++/transcript_to_source ../examples/input-files/kaccNlwi6lUCEM.en.OStt > ./kaccNlwi6lUCEM.en.OSt
	
## MGIZA [1]

MGIZA is a multi-CPU type of GIZA++ [2] that makes alignment between source (OSt) files and target (tt) files. 

### Requirements

#### python3 (it installed on Ubuntu 16.04 or higher as the default.)

- sudo apt-get install python3.6
	
#### cmake
	
- sudo apt install cmake
	
#### libboost

- sudo apt-get install libboost-all-dev

### Input  files 

- OSt file (or OStt file and convert it to OSt with giza++/transcript_to_source.py script)
- tt file (e.g. *.TTde, *.TTcs)
- Notes:
    - The number of lines in OSt and tt must be equal. 
    - The number of lines in source parallel and target parallel must be equal. 



### Running giza++ without parallel data (only using ost and tt files
    
``` {r, engine='python'} 
$ mkdir <ouput_dir>
$ ./run-giza -s <OSt_file> -t <tt_file> -o <ouput_dir> --ncpus <number_of_cpus>
```

    - parameters:
        - -s: path of the OSt file
        - -t: path of the tt file
        - -o: path of the output directory (deafult is ./)
		- --ncpus: number of cpus (deafult is 4)
    - e.g. mkdir test;
    ./run-giza -s ../examples/input-files/kaccNlwi6lUCEM.en.OSt -t ../examples/input-files/kaccNlwi6lUCEM.en.TTcs -o ./test/; 


### Download and use parallel corpus

You can use the parallel corpus to improve the train of giza++, so you can download and extract them from https://www.statmt.org/europarl/ address or another source.

#### Downloading parallel corpues with wget

	wget <parallel_corpuse_link>	

### Running giza++ with an external parallel corpus

``` {r, engine='python'} 
$ ./run-giza -s <OSt_file> -t <tt_file> -o <ouput_dir> -ps <source_parallel> -pt <target_parallel> --ncpus <number_of_cpus>
```
    - parameters:
        - -s: path of the OSt file
        - -t: path of the tt file
        - -o: path of the output directory (deafult is ./)
        - -ps: path of the source parallel corpus (languege of OSt and source parallel corpus is the same.) 
        - -pt: path of the target parallel corpus (languege of tt and target parallel corpus is the same.)
		- --ncpus: number of cpus (deafult is 4)
    - e.g. ./run-giza -s ../examples/input-files/kaccNlwi6lUCEM.en.OSt -t ../examples/input-files/kaccNlwi6lUCEM.en.TTcs -o ./test/ -ps ../examples/pararllel-corpus/parallel.en -pt ../examples/pararllel-corpus/parallel.cs 
    
### The output 

After running MGIZA, a file (tt_file_name + .align), generated in the output directory path.
For example: 
    -command: ./run-giza -s ./test/polish.OSt -t ./test/polish.TTcs -o ./test/
    -output: ./test/polish.TTcs.align



# References

    [1] Qin Gao and Stephan Vogel. 2008. Parallel Implementations of Word Alignment Tool, Association for Computational Linguistics
	
	[2] Franz Josef Och and Hermann Ney. 2003. A systematic comparison of various statistical alignment models, Computational Linguistics, 29(1):19–51
