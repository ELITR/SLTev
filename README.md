
# SLTev

SLTev is an open-source tool for assessing the quality of spoken language translation in a comprehensive way. Based on timestamped reference transcript and reference translation into a target language, THETOOL reports the quality, delay and stability of a given SLT candidate output.

## Required Modules

- python3.5 or Higher

- NLTK [1]

- mwerSegmenter [2]
    
- mosestokenizer [3]

- Sacre Bleu [4]
    
- requests 
    
- gitpython 

- gitdir 


## Input SLT and ASR name format


### SLT format

- OSt file name (e.g. 03_botel-proti-proudu.en.OSt) + . + language (e.g. de or cs) + .slt
- e.g. 03_botel-proti-proudu.en.cs.slt, 03_botel-proti-proudu.en.de.slt
    
### ASR format

- OSt file name (e.g. 03_botel-proti-proudu.en.OSt) + . + language (e.g. en) + .asr
- e.g. 03_botel-proti-proudu.en.en.asr


## Installation

- If you using virtual environment, source your enviornment by the following command:

``` {r, engine='bash'} 
$ source path/to/virtualenv/bin/activate
```

- install needed modules by pip in your enviornment:

``` {r, engine='bash'} 
(your-env)$ pip install --upgrade -r requirements.txt
```

## Clone project from git 

You can download the project as follow in Github:
``` {r, engine='bash'} 
$ git clone https://github.com/lngvietthang/SLTev-master.git 
$ cd SLTev-master 
```

## Package Overview

- SLTev-scripts: Contains scripts for running SLTev and ASRev
- examples: Contains examples of inputs files which contains slt-asr-samples and input-files 
- data-preperation: Contains scripts to prepere data for SLTev script such as MGIZA  

## Getting Started with SLTev

Please prepare your data (using data-preperation/elitr-testset-prep.md help), and run scripts as follow:

``` {r, engine='bash'}
(your-env)$ cd SLTev-scripts 
```

### Generate ELITER files based on the ELITER-Index-Name 

``` {r, engine='bash'}
(your-env)$ mkdir <output_directory>
(your-env)$ ./SLTev -g <elitr_index_name> -o <output_directory> --audio
```

    parameters:
        -g: generating ELITER files based on the ELITER-Index-Name 
        -o: output directory path
        --audio: audios files only generated 
		--noaudio: just text files generated
    Notes:
        - Index-names are placed in the "https://github.com/ELITR/elitr-testset/tree/master/indices". e.g. iwslt-antrecorp
        - e.g. e.g. mkdir ./test; ./SLTev -g khanacademy-for-SLTev -o ./test/ --audio; 
  
### Evaluate ASR and SLT files based on the ELITER files (Running SLTev)


#### Single file

``` {r, engine='bash'}
(your-env)$ ./SLTev -e <elitr_index_name> -i <elitr_file_name> -t <segment_time> 
```
    
    parameters:
        -e: evaluating input file based on the ELITER files
        -f: file path for evaluating
        -t: time of each segment for calculate BLEU score (deafult is 3000)
        -alignment: alignment files (manual alignment) are using instead of the ELITER files
        -outfile: outfile (standard output writing there)
        --offline: offline cache files are using. (if not, the needed files will downloaded) 
    Notes:
        - The number of the inputs in -alignment must be equal with tt files (for some files and languages, there are 
            multiple tt files)
        - e.g. ./SLTev -e khanacademy-for-SLTev -i ../examples/slt-asr-samples/kaccNlwi6lUCEM.en.cs.slt

#### Multiple files

``` {r, engine='bash'}
(your-env)$ mkdir <result_output_directory>
(your-env)$ ./SLTev -e <elitr_index_name> -i <SLT_output_directory> -outdir <result_output_directory>
```
     
    parameters:
        -e: evaluating input files based on the ELITER files. 
        -i: ditrectory path for evaluating
        -t: time of each segment for calculate BLEU score
        --outdir: output directory path
        --offline: offline cache files are using. (if not, the needed files will downloaded)  
    Notes:
            - e.g. mkdir test1; ./SLTev -e khanacademy-for-SLTev -i ../examples/slt-asr-samples/ --outdir ./test1/;

#### Other parameters

    
- --clean: clean all cache files (SLTev-cache directory) 

## How can we run our data locally?

If you want to use your files locally, please do as follow:
1. make a folder by name <your_indice> in ./SLTev-cache/OStt-tt-files/ path (if ./SLTev-cache/OStt-tt-files/ is not exist please make it)                                                                       
2. put "tt" files (*.TTcs, *.TTde, ..), "OStt" files (*.OStt) and "align" files [outputs of the giza++] (*.align) in <your_indice> folder                                                               
3. in evaluating phase using --offline parameter                                                                                                                                    
- e.g. ./SLTev -e <your_indice> -i ./submision/ --offline --outdir ./test/ 


## Evaluta asr files based on the WER score (Running ASRev)

``` {r, engine='bash'}
(your-env)$ ./ASRev --ost <ost_file_path> -asr <asr_file_path>
```
     
    parameters:
        - --ost: OSt file path 
        - --asr: ASR file path

    Notes:
            - e.g. ./ASRev --ost ../examples/input-files/kaccNlwi6lUCEM.en.OSt --asr ../examples/slt-asr-samples/kaccNlwi6lUCEM.en.en.asr


## Notes

- Default temporary directory name is "SLTev-cache" (it make automaticly after first SLTev runing)
- You can use Giza++ alignments if they are missed in <elitr-testset> (detail placed in the data-preperation/elitr-testset-prep.md)
- The first line of each output is commit ID.
- For some filse which have more than one tt files, SLTev works as multireference evaluator. (e.g. 03_botel-proti-proudu have two tt files for cs language (03_botel-proti-proudu.TTcs1, 03_botel-proti-proudu.TTcs2))
- If don't use --oflline parameter, the needed files download automatically. 

    
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
    
