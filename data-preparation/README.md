# Data Preparation

In order to make alignment between source and target, we trusted MGIZA [1] which is a multi-CPU type of GIZA++ [2] that makes alignment between source files and target files.

### Requirements

#### python3 (it installed on Ubuntu 16.04 or higher as the default.)

- sudo apt-get install python3.7

#### cmake

- sudo apt install cmake

#### libboost

- sudo apt-get install libboost-all-dev

### Input  files 

- source file
- target file
- Notes:
    - The number of lines in source and target must be equal. 
    - The number of lines in source parallel and target parallel must be equal. 


### Running giza++ without parallel data
    
``` {r, engine='python'} 
$ ./run-giza -s <source_file> -t <target_file> -o <ouput_dir> --ncpus <number_of_cpus>
```

    - parameters:
        - -s: path of the source file
        - -t: path of the target file
        - -o: path of the output directory (deafult is ./)
        - --ncpus: number of cpus (deafult is 4)
    - e.g. ./run-giza -s ../sample-data/sample.en.OSt -t ../sample-data/sample.cs.OSt -o ./test/


### Download and use parallel corpus

You can use the parallel corpus to improve the train of giza++, so you can download and extract them from https://www.statmt.org/europarl/ address or another source.

#### Downloading parallel corpues with wget

    wget <parallel_corpuse_link>

### Running giza++ with an external parallel corpus

``` {r, engine='python'} 
$ ./run-giza -s <source_file> -t <target_file> -o <ouput_dir> -ps <source_parallel_file> -pt <target_parallel_file> --ncpus <number_of_cpus>
```
    - parameters:
        - -s: path of the source file
        - -t: path of the target file
        - -o: path of the output directory (deafult is ./)
        - -ps: path of the source parallel corpus 
        - -pt: path of the target parallel corpus 
        - --ncpus: number of cpus (deafult is 4)
    

# References

    [1] Qin Gao and Stephan Vogel. 2008. Parallel Implementations of Word Alignment Tool, Association for Computational Linguistics
    [2] Franz Josef Och and Hermann Ney. 2003. A systematic comparison of various statistical alignment models, Computational Linguistics, 29(1):19–51

