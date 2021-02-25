
# SLTev

SLTev is an open-source tool for assessing the quality of spoken language translation (SLT) in a comprehensive way. Based on timestamped reference transcript and reference translation into a target language, SLTev reports the quality, delay and stability of a given SLT candidate output.

SLTev can also evaluate the intermediate steps alone: the output of automatic speech recognition (ASR) and machine translation (MT).

## Requirements

- python3.6 or higher
- some pip-installed modules:
  - sacrebleu, sacremoses
  - gitpython, gitdir, filelock
- mwerSegmenter 

## File Naming Convention

Depending on whether your system produces (spoken language) translation (SLT), or just the speech recognition (ASR), you should use the following naming template of your input and output files.

### Reference Transcripts: ``.OSt``, ``.OStt``
- &lt;file-name&gt; . &lt;language&gt; . &lt;OSt/OStt&gt;
- e.g. ``kaccNlwi6lUCEM.en.OSt``, ``kaccNlwi6lUCEM.cs.OStt``

### Word Alignment for Better Estimation: ``.align``
- &lt;file-name&gt; . &lt;source-language&gt; . &lt;target-language&gt; . &lt;align&gt;
- e.g. ``kaccNlwi6lUCEM.en.de.align``

### System Outputs from Translation: ``.slt``, ``.mt``
- &lt;file-name&gt; . &lt;source-language&gt; . &lt;target-language&gt; . &lt;slt/mt&gt;
- e.g. ``kaccNlwi6lUCEM.en.de.slt``, ``kaccNlwi6lUCEM.cs.en.mt``

### System Outputs from ASR: ``.asr``, ``.asrt``
- &lt;file-name&gt; . &lt;source-language&gt; . &lt;source-language&gt; . &lt;asr/asrt&gt;
- e.g. ``kaccNlwi6lUCEM.en.en.asr``

## Installation

Install the Python module (Python 3 only)
   
``` 
pip3 install SLTev
```
    
Also, you can install from the source:

``` 
python3 setup.py install
```

## Package Overview

- SLTev: Contains scripts for running SLTev
- sample-data: Contains sample input and output files

## Evaluating

SLTev scoring relies on reference outputs (golden transcript for ASR, reference translation for MT and SLT).

You can run SLTev and provide it with your custom reference outputs, or you can pick the easier option: use our provided test set (``elitr-testset``) to evaluate your system on our inputs. The added benefit of ``elitr-testset`` scoring is that it makes your results comparable to others (subject to SLTev and test set versions, of course).

### Evaluating on ``elitr-testset``

SLTev works best if you want to evaluate your system on files provided in ``elitr-testset`` (https://github.com/ELITR/elitr-testset).

The procedure is simple:
1. Choose an "index", i.e. a subset of files that you want to test on, here: https://github.com/ELITR/elitr-testset/tree/master/indices
We illustrate the rest with ``SLTev-sample`` as the index.

2. Ask SLTev to provide you with the current version of input files:
```
SLTev -g SLTev-sample --outdir my-evaluation-run-1
# To use your existing checkout of elitr-testset, add -T /PATH/TO/YOUR/elitr-testset
# To populate of elitr-testset links, add ELITR_CONFIDENTIAL_PASSWORD=<password> before SLTev (e.g. ELITR_CONFIDENTIAL_PASSWORD=myPass SLTev -g SLTev-sample --outdir my-evaluation-run-1) 
```

3. Run your models on files in ``my-evaluation-run-1`` and put the outputs into the same directory, with filename suffixes as described above.

4. Run SLTev to get the scores:
```
SLTev -e my-evaluation-run-1/
# To aggregate scores instead of produce score files, add --aggregate
# To reduce the number of scores, add --simple
```

### Evaluating with Your Custom Reference Files

In order to evaluate a hypothesis with custom files, you can use ``MTeval``, ``SLTeval``, ``ASReval`` commands as follow:
Each one of them takes a list of input file paths (-i or --input) and a list of the format of the input files in orders (-f or --format_orders). The input file formats can be chosen from the following items:
* source: source files 
* ref: reference
* ostt: timestamped gold transcript
* slt: timestamped online MT hypothesis
* mt: finalized MT hypothesis
* align: align files (output of the MGIZA)
* asr: finalized ASR transcript
* asrt: timestamped ASR hypothesis

#### MT Evaluating  
```
MTeval -i file1 file2 ... -f file1_format file2_format ...
# To reduce the number of scores, add --simple 
``` 
Demo example: 
```
MTeval -i fake-data/sample.en.cs.mt fake-data/sample.cs.OSt -f mt ref
``` 
#### SLT Evaluating 
```
SLTeval -i file1 file2 ... -f file1_format file2_format ...
# To reduce the number of scores, add --simple 
```
Demo example: 
``` 
SLTeval -i fake-data/sample.en.cs.slt fake-data/sample.cs.OSt fake-data/sample.en.OStt -f slt ref ostt
```

#### ASR Evaluating 
```
ASReval -i file1 file2 ... -f file1_format file2_format ...
# To reduce the number of scores, add --simple 
```
Demo example: 
``` 
ASReval -i fake-data/sample.en.en.asr fake-data/sample.en.OSt -f asr source
```


#### ASRT Evaluating 
```
ASReval -i file1 file2 ... -f file1_format file2_format ...
# To reduce the number of scores, add --simple 
``` 
Demo example: 
``` 
ASReval -i fake-data/sample.en.en.asrt fake-data/sample.en.OSt fake-data/sample.en.OStt -f asrt source ostt
```


#### Notes
1. *.asrt and *.slt files have timestamps and, *.mt and *.asr do not have. 
2. For using ``MTeval``, ``SLTeval``, ``ASReval`` commands, you do not need to follow naming templates. 
3. You can evaluate several hypotheses at the same time. For example, suppose you have two ASR systems for a resource file. You can perform the evaluation as follows:
```
ASReval -i system1.asr system2.asr data.source -f asr asr source
```


## Terminology and Abbreviations

* OSt  ... original speech manually transcribed
* OStt ... original speech manually transcribed with word-level timestamps
* mt   ... the unrevised output of text-based translation; the source of MT is ASR (machine-transcribed OS) or OSt (human-transcribed OS)
* slt  ... timestamped online MT hypothesis
* asr  ... the unrevised output of speech recognition system
* asrt ... the unrevised output of speech recognition system; timestamped at the word level

    


