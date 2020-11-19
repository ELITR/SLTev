
Title: SLTev
authors: Ebrahim Ansari, Ondrej Bojar, Mohammad Mahmoudi
Date: 27/10/2020
...

# SLTev

SLTev is a tool for the comprehensive evaluation of (simultaneous) spoken language translation.

## Clone project from git 

You can download the project as follow from Github:

    a) git clone https://github.com/lngvietthang/SLTev-master.git 
    b) cd SLTev-master 


## Requirements

### NLTK [1]

    pip install --user -U nltk

### mwerSegmenter [2]
    
    chmod +x mwerSegmenter 

### mosestokenizer [3]
    pip install mosestokenizer

### Sacre Bleu [4]

    pip install sacrebleu
    
### requests 
    pip install requests
    
### gitpython 
    pip install gitpython
    
### gitdir 
    pip install gitdir



## Input SLT and ASR name format


### SLT format

    - OSt file name without .OSt (e.g. 03_botel-proti-proudu.en.OSt) + . + language (e.g. de or cs) + .slt
    - e.g. 03_botel-proti-proudu.en.cs.slt, 03_botel-proti-proudu.en.de.slt
    
### ASR format

    - OSt file name without .OSt (e.g. 03_botel-proti-proudu.en.OSt) + . + language (e.g. en) + .asr
    - e.g. 03_botel-proti-proudu.en.en.asr


## Usage


### Generate ELITER files based on the ELITER-Index-Name 

    SLTev -g <elitr_index_name> -o <output_directory> --audio
    parameters:
        -g: generating ELITER files based on the ELITER-Index-Name 
        -o: output directory path
        --audio: audios files just will be downoaded
		--noaudio: text files just will be downoaded. 
    Notes:
        - Index-names are placed in the "https://github.com/ELITR/elitr-testset/tree/master/indices". e.g. iwslt-antrecorp
        - e.g. e.g. ./SLTev -g iwslt-consecutive -o ./test/ --audio 
    
        
### Evaluate ASR and SLT files based on the ELITER files


#### Single file

    SLTev -e <elitr_index_name> -i <elitr_file_name> -t <segment_time> 
    parameters:
        -e: evaluating input file based on the ELITER files
        -i: file path for evaluating
        -t: time of each segment for calculate BLEU score
        -alignment: alignment files (manual alignment) are using instead of the ELITER files
        -outfile: outfile (standard output writing there)
        --offline: offline cache files are using. (if not, the needed files will downloaded) 
        Notes:
            - The number of the inputs in -alignment must be equal with tt files (for some files and languages, there are 
            multiple tt files)
            - e.g. ./SLTev -e iwslt-antrecorp -i ./submision/03_botel-proti-proudu.en.asr

#### Multiple files

    SLTev -e <elitr_index_name> -i <SLT_output_directory> -outdir <result_output_directory> 
    parameters:
        -e: evaluating input files based on the ELITER files. 
        -i: ditrectory path for evaluating
        -t: time of each segment for calculate BLEU score
        --outdir: output directory path
        --offline: offline cache files are using. (if not, the needed files will downloaded)  
        Notes:
            - e.g. ./SLTev -e iwslt-antrecorp -i ./submision/ --outdir ./test/

  #### Other parameters

    --clean: clean all cache files (SLTev-cache directory) 



## Notes
    - Default temporary directory name is "SLTev-cache" (it make automaticly after first runing)
    - You can use Giza++ alignments if they are missed in <elitr-testset> (detail placed in the appendix)
    - The first line of each output is commit ID.
    - For some filse which have more than one tt files, SLTev works as multireference evaluator. (e.g. 03_botel-proti-proudu have two tt files for cs language (03_botel-proti-proudu.TTcs1, 03_botel-proti-proudu.TTcs2))
    - If don't use --oflline parameter, the needed files download automatically (If commit-id was be changed). 

    
    

## Terminology

In the following, we use this notation:

* OS  ... original speech (sound)
* OSt ... original speech manually transcribed
* OStt ... original speech manually transcribed with word-level timestamps
* IS  ... human interpreter's speech (sound)
* ISt ... IS manually transcribed with word-level timestamps
* TT ... human textual translation, created from transcribed original speech (OSt); corresponds sentence-by-sentence to OSt

* ASR ... the unrevised output of speech recognition system; timestamped at the word level
* SLT ... the unrevised output of spoken language translation, i.e. sentences in the target language corresponding to sentences in the source language; the source of SLT is OS
* MT  ... the unrevised output of text-based translation; the source of MT is ASR (machine-transcribed OS) or OSt (human-transcribed OS)

## SLTev Modes of Operation

SLTev is designed to support these modes of operation:

* Evaluate SLT against OSt+TT. (This is the primary goal of SLTev, evaluate the output of SLT systems against time-stamped source + reference translation)
* Evaluate ASR+SLT against OSt+TT. (A refined version of the previous, when the SLT system can provide internal details about ASR operation, esp. emission timestamps.)
* Evaluate IS against OSt+TT. (This is an interesting contrastive use of SLTev, to evaluate human interpreters against manually translated correct transcripts.)
* Evaluate MT against TT. (This is plain old MT evaluation.)
* Evaluate ASR against OSt. (This is plain old ASR evaluation, except the segmentation is not prescribed.)

## References

    [1] Steven Bird, Ewan Klein, and Edward Loper. 2009. Natural Language Processing with Python, 1st edition. OReilly Media, Inc.
    [2] Evgeny Matusov, Gregor Leusch, Oliver Bender, and Hermann Ney. 2005b. Evaluating machine-translation output with automatic sentence segmentation. In International Workshop on Spoken Language Translation, pages 148–154, Pittsburgh, PA, USA.
    [3] Philipp Koehn, Hieu Hoang, Alexandra Birch, Chris Callison-Burch, Marcello Federico, Nicola Bertoldi, Brooke Cowan, Wade Shen, Christine Moran, Richard Zens, Chris Dyer, Ondřej Bojar, Alexandra Constantin and Evan Herbst. 2007. Proceedings of the ACL (Association for Computational Linguistics).
    [4] Post, Matt. 2018. Association for Computational Linguistics, pages 186-191. 
    
    
 
## Appendix

### Run SLTev locally

	a) make a folder by name <your_indice> in ./SLTev-cache/OStt-tt-files/ path (if ./SLTev-cache/OStt-tt-files/ is not exist please make it)
	b) put "tt" files (*.TTcs, *.TTde, ..), "OStt" files (*.OStt) and "align" files [outputs of the giza++] (*.align) in <your_indice> folder
	c) in evaluating phase using --offline parameter
		e.g. ./SLTev -e <your_indice> -i ./submision/ --offline --outdir ./test/ 

### Make a new Indices

####  Requirements

	a) git (sudo apt install git-all)

#### Instructions

	a) clone the repo ($ git clone https://github.com/ELITR/elitr-testset/)
	b) make a new folder in "elitr-testset/documents/" path and put all fils there (*.OSt, *.OStt, *.TTde/cs, *.mp3 )
	c) make an indice file in "elitr-testset/indices/" path (make surce you put all path files in "elitr-testset/documents/<your_directory>/" in it.) 
	d) add all files to repo ($ cd eliter-testset; git add *;)
	e) commit all files ($ git commit -m "<your change notes>")
	f) push files ($ git push)
	
### GIZA++

The giza++ is a tool for make alignment between source (OSt) files and target (tt) files. 

#### Requirements

##### python3 (it installed on Ubuntu 16.04 or higher as the default.)

	sudo apt-get install python3.6
	
##### cmake
	
	sudo apt install cmake
	
##### libboost

	sudo apt-get install libboost-all-dev

#### Input  files 

    - OSt file (or OStt file and convert it to OSt with giza++/transcript_to_source.py script)
    - tt file (e.g. *.TTde, *.TTcs)
    - Note:
        -  The number of lines in OSt and tt must be equal. 
        - The number of lines in source parallel and target parallel must be equal. 

#### Convert OStt file to OSt

    python giza++/transcript_to_source.py ostt_file > source_ref 
        1) ostt_file is the input OStt file. 
        2) source_ref is the output file. 
    

#### Running giza++ without parallel data (only using ost and tt files)
    
    run-giza -s <OSt_file> -t <tt_file> -o <ouput_dir> --ncpus <number_of_cpus>
    parameters:
        -s: path of the OSt file
        -t: path of the tt file
        -o: path of the output directory (deafult is ./)
		--ncpus: number of cpus (deafult is 4)
    e.g. ./run-giza -s ./test/polish.OSt -t ./test/polish.TTcs -o ./test/


#### Download and use parallel corpus

You can use the parallel corpus to improve the train of giza++, so you can download and extract them from https://www.statmt.org/europarl/ address or another source.

##### Downloading parallel corpues with wget

	wget <parallel_corpuse_link>
	

#### Running giza++ with an external parallel corpus

    run-giza -s <OSt_file> -t <tt_file> -o <ouput_dir> -ps <source_parallel> -pt <target_parallel> --ncpus <number_of_cpus>
    parameters:
        -s: path of the OSt file
        -t: path of the tt file
        -o: path of the output directory (deafult is ./)
        -ps: path of the source parallel corpus (languege of OSt and source parallel corpus is the same.) 
        -pt: path of the target parallel corpus (languege of tt and target parallel corpus is the same.)
		--ncpus: number of cpus (deafult is 4)
    e.g. ./run-giza -s ./test/polish.OSt -t ./test/polish.TTcs -o ./test/ -ps ./test/europarl-v7.cs-en.en -pt ./test/europarl-v7.cs-en.cs 
    
#### The output 

After running giza++, a file (tt_file_name + .align), generated in the output directory path. for using output, you must put the alignment in the relevent folder. 
For example: 
    -command: ./run-giza -s ./test/polish.OSt -t ./test/polish.TTcs -o ./test/
    -output: ./test/polish.TTcs.align

