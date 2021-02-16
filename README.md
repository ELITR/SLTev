
# SLTev

SLTev is an open-source tool for assessing the quality of spoken language translation (SLT) in a comprehensive way. Based on timestamped reference transcript and reference translation into a target language, SLTev reports the quality, delay and stability of a given SLT candidate output.

SLTev can also evaluate the intermediate steps alone: the output of automatic speech recognition (ASR) and machine translation (MT).

## Requirements

- python3.7 or higher
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

### System Outputs from ASR: ``.asr``
- &lt;file-name&gt; . &lt;source-language&gt; . &lt;source-language&gt; . &lt;asr&gt;
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
```

### Evaluating with Your Custom Reference Files

Put all input (*.OSt, *.OStt, *.align) and output files (*.slt/asr/mt) in a folder (e.g. My-folder) and the evaluation would be similar to part 3 (SLTev -e My-folder)



## Terminology and Abbreviations

In the following, we use this notation:

* OS  ... original speech (sound)
* OSt ... original speech manually transcribed
* OStt ... original speech manually transcribed with word-level timestamps
* IS  ... human interpreter's speech (sound)
* IStt ... IS manually transcribed with word-level timestamps
* TT ... human textual translation, created from transcribed original speech (OSt); corresponds sentence-by-sentence to OSt

* ASR ... the unrevised output of speech recognition system; timestamped at the word level
* SLT ... the unrevised output of spoken language translation, i.e. sentences in the target language corresponding to sentences in the source language; the source of SLT is OS
* MT  ... the unrevised output of text-based translation; the source of MT is ASR (machine-transcribed OS) or OSt (human-transcribed OS)
    

