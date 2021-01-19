
# SLTev

SLTev is an open-source tool for assessing the quality of spoken language translation (SLT) in a comprehensive way. Based on timestamped reference transcript and reference translation into a target language, SLTev reports the quality, delay and stability of a given SLT candidate output.

SLTev can also evaluate the intermediate steps: the output of automatic speech recognition (ASR) and machine translation (MT).

## Requirements Modules

- python3.5 or higher
- some pip-installed modules:
  - NLTK [1]
  - sacreBLEU [4]
  - requests, gitpython, gitdir
- mwerSegmenter [2]
- mosestokenizer [3]

## File Naming Convention

Depending on whether your system produces (spoken language) translation (SLT), or just the speech recognition (ASR), you should use the following naming of your output files.

The "OSt" means "original speech, transcribed", see the list of abbreviation below.

### SLT format

- OSt file name (e.g. ``03_botel-proti-proudu.en.OSt``) + . + language (e.g. de or cs) + ``.slt``
- e.g. ``03_botel-proti-proudu.en.cs.slt``, ``03_botel-proti-proudu.en.de.slt``
    
### ASR format

- OSt file name (e.g. ``03_botel-proti-proudu.en.OSt``) + . + language (e.g. en) + ``.asr``
- e.g. ``03_botel-proti-proudu.en.en.asr``


## Installation

Download the project from Github:
``` {r, engine='bash'} 
git clone https://github.com/ELITR/SLTev.git
cd SLTev
```

Create and activate a new virtual environment (or use your standard one):
``` {r, engine='bash'} 
virtualenv your-env
source your-env/bin/activate
```

Install the prerequisites:

``` {r, engine='bash'} 
(your-env)$ pip install --upgrade -r requirements.txt
```

## Package Overview

- SLTev-scripts: Contains scripts for running SLTev and ASRev
- examples: Contains examples of inputs files which contains slt-asr-samples and input-files 
- data-preparation: Contains maintenance scripts to prepare data for SLTev, e.g. converting MGIZA outputs to SLTev inputs


## Evaluating on ``elitr-testset``

SLTev works best if you want to evaluate your system on files provided in ``elitr-testset`` (https://github.com/ELITR/elitr-testset).

The procedure is simple:
1. Choose an "index", i.e. a subset of files that you want to test on, here: https://github.com/ELITR/elitr-testset/tree/master/indices
We illustrate the rest with ``khanacademy-for-SLTev`` as the index.

2. Ask SLTev to provide you with the current version of input files:
```
(your-env)$ SLTev -g khanacademy-for-SLTev -outdir my-evaluation-run-1
```
3. Process input files in ``my-evaluation-run-1`` with your system.
```
# Here we simply copy the sample outputs
cp examples/slt-asr-samples/kac*slt ./my-evaluation-run-1
```
4. Run SLTev to get the scores:
```
TODO
```

### Outdated Instructions

This section is needlessly complicated and will be removed.


If you want to use elitr-testset repository, first you need to download elitr-testset repo. You can use SLTev with -g parameter for cloning and downloading elitr-testset repo. Also index files will put in the ./SLTev-cache/OStt-tt-files/ 
``` {r, engine='bash'}
(your-env)$ mkdir <output_directory>
(your-env)$ ./SLTev -g <elitr_index_name> 
```

    parameters:
        -g: generating ELITER files based on the ELITER-Index-Name 
        --commitid: checkout git repo according to the commitid (deafult is HEAD)

    Notes:
        - Index-names are placed in the "https://github.com/ELITR/elitr-testset/tree/master/indices". e.g. iwslt-antrecorp
        - e.g. ./SLTev -g khanacademy-for-SLTev
  
### Evaluate ASR and SLT files based on the ELITER files


#### Single file

``` {r, engine='bash'}
(your-env)$ ./SLTev -e <elitr_index_name> -i <elitr_file_name> -t <segment_time> 
```
    
    parameters:
        -e: evaluating input file based on the ELITER files
        -f: file path for evaluating
        -t: time of each segment for calculate BLEU score (default is 3000)
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
        -i: directory path for evaluating
        -t: time of each segment for calculate BLEU score
        --outdir: output directory path
        --offline: offline cache files are using. (if not, the needed files will downloaded)  
    Notes:
            - e.g. mkdir test1; ./SLTev -e khanacademy-for-SLTev -i ../examples/slt-asr-samples/ --outdir ./test1/;

#### Evaluate ASR files using WER score (Running ASRev)

``` {r, engine='bash'}
(your-env)$ ./SLTev -e <elitr_index_name> -i <SLT_output_directory> -outdir <result_output_directory> --ASRev
```
     
    parameters:
        -e: evaluating input files based on the ELITER files. 
        -i: ditrectory_path/file_path for evaluating
        --outdir: output directory path
        --ASRev (i exist calculte WER score)
    Notes:
            - e.g. ./SLTev -e khanacademy-for-SLTev -i ../examples/slt-asr-samples --outdir ./test/ --ASRev


#### Other parameters

    
- --clean: clean all cache files (SLTev-cache directory) 

## How can we run our data locally?

If you want to use your files locally, please do as follow:
1. make a folder by name <your_indice> in ./SLTev-cache/OStt-tt-files/ path (if ./SLTev-cache/OStt-tt-files/ is not exist please make it)                                                                       
2. put "tt" files (*.TTcs, *.TTde, ..), "OStt" files (*.OStt) and "align" files [outputs of the giza++] (*.align) in <your_indice> folder                                                               
3. do not use -g parameter, just run as follow:                                                                                                                                 
- e.g. ./SLTev -e <your_indice> -i ./submision/  --outdir ./test/ 


## Getting Started with SLTev

Please prepare your data (using data-preparation/elitr-testset-prep.md help), and run scripts as follow:

``` {r, engine='bash'}
(your-env)$ cd SLTev-scripts 
```



## Notes

- Default temporary directory name is "SLTev-cache" (it make automaticly after first SLTev runing)
- You can use Giza++ alignments if they are missed in <elitr-testset> (detail placed in the data-preperation/elitr-testset-prep.md)
- The first line of each output is commit ID.
- For some filse which have more than one tt files, SLTev works as multireference evaluator. (e.g. 03_botel-proti-proudu have two tt files for cs language (03_botel-proti-proudu.TTcs1, 03_botel-proti-proudu.TTcs2))

    
## Terminology and Abbreviations

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
    
