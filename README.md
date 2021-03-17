
# SLTev

SLTev is an open-source tool for assessing the quality of spoken language translation (SLT) in a comprehensive way. Based on timestamped golden transcript and reference translation into a target language, SLTev reports the quality, delay and stability of a given SLT candidate output.

SLTev can also evaluate the intermediate steps alone: the output of automatic speech recognition (ASR) and machine translation (MT).

## Requirements

- python3.6 or higher
- some pip-installed modules:
  - sacrebleu, sacremoses
  - gitpython, gitdir, filelock
- mwerSegmenter 

## File Naming Convention

Depending on whether your system produces (spoken language) translation (SLT), or just the speech recognition (ASR), you should use the following naming template of your input and output files.

### Golden Transcripts: ``.OSt``, ``.OStt``
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
# To populate of elitr-testset links, add ELITR_CONFIDENTIAL_PASSWORD=<password> before SLTev,
#   e.g.: ELITR_CONFIDENTIAL_PASSWORD=myPass SLTev -g SLTev-sample --outdir my-evaluation-run-1
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
Each one of them takes a list of input file paths (-i or --input) and a list of the format of the input files in orders (-f or --file-formats). The input file formats can be chosen from the following items:
* ost: original speech transcribed, i.e. the golden transcript 
* ref: reference translation
* ostt: timestamped golden transcript
* slt: timestamped online MT hypothesis, with partial outputs
* mt: finalized MT hypothesis (i.e. one segment per line; segmentation can differ from the reference one)
* align: align files (output of the MGIZA)
* asrt: timestamped ASR hypothesis, with partial outputs
* asr: finalized ASR hypothesis (i.e. one segment per line; segmentation can differ from the golden one)

#### Evaluating MT

To evaluate the output of a machine translation system without any timing information, use the following command.

Note that SLTev is not intended for the basic case where MT output segment correspond 1-1 to the reference; SLTev will always resegment in some way.

```
MTeval -i file1 file2 ... -f file1_format file2_format ...
# To reduce the number of scores, add --simple 
``` 
Demo example: 
```
git clone https://github.com/ELITR/SLTev.git
cd SLTev
MTeval -i sample-data/sample.en.cs.mt sample-data/sample.cs.OSt -f mt ref
``` 
Should give you output like this:
```
Evaluating the file  sample-data/sample.en.cs.mt  in terms of translation quality against  sample-data/sample.cs.OSt
P ... considering Partial segments in delay and quality calculation (in addition to Complete segments)
T ... considering source Timestamps supplied with MT output
W ... segmenting by mWER segmenter (i.e. not segmenting by MT source timestamps)
A ... considering word alignment (by GIZA) to relax word delay (i.e. relaxing more than just linear delay calculation)
------------------------------------------------------------------------------------------------------------
--       TokenCount    reference1             37
avg      TokenCount    reference*             37
--       SentenceCount reference1             4
avg      SentenceCount reference*             4
tot      sacreBLEU     docAsAWhole            32.786
avg      sacreBLEU     mwerSegmenter          25.850
```

#### Evaluating SLT

Spoken language translation evaluates "machine translation in time". So a time-stamped MT output (``slt``) is compared with the reference translation (non-timed, ``ref``) and the timing of the golden transcript (``ostt``).

```
SLTeval -i file1 file2 ... -f file1_format file2_format ...
# To reduce the number of scores, add --simple 
```
Demo example: 
```
# get sample-data as in the MT example above
SLTeval -i sample-data/sample.en.cs.slt sample-data/sample.cs.OSt sample-data/sample.en.OStt -f slt ref ostt
```
Should give you:
```
Evaluating the file  sample-data/sample.en.cs.slt  in terms of translation quality against  sample-data/sample.cs.OSt
...
tot      Delay         PW                     336.845
...
tot      Flicker       count_changed_content  23
...
tot      sacreBLEU     docAsAWhole            32.786
...
```


#### Evaluating ASR

In basic speech recognition evaluation, timing is ignored. For this type of evaluation, use the following command and provide ASR output (``asr``) and the golden transcript without timestamps (``ost``):

```
ASReval -i file1 file2 ... -f file1_format file2_format ...
# To reduce the number of scores, add --simple 
```
Demo example: 
```
# get sample-data as in the MT example above
ASReval -i sample-data/sample.en.en.asr sample-data/sample.en.OSt -f asr ost
```
Should give you:
```
Evaluating the file  sample-data/sample.en.en.asr  in terms of  WER score against  sample-data/sample.en.OSt
-------------------------------------------------------------
L ... lowercasing
P ... removing punctuation
C ... concatenating all sentences
W ... using mwersegmemter
M ... using Moses tokenizer
-------------------------------------------------------------
LPC    0.265
LPW    0.274
WM     0.323
```

#### Evaluating ASR with timing (ASRT)

ASRT is like SLT but in the source language, i.e. evaluating the time-stamped output of an ASR system (``asrt``) against the golden transcript which has to be provided twice: without timestamps (``ost``) and with timing and partial segments (``ostt``). All the files are in the same language and the ``ost`` file must have the exact same number of segments as there are "C"omplete segments in the ``ostt`` file.

```
ASReval -i file1 file2 ... -f file1_format file2_format ...
# To reduce the number of scores, add --simple 
``` 
Demo example: 
``` 
ASReval -i sample-data/sample.en.en.asrt sample-data/sample.en.OSt sample-data/sample.en.OStt -f asrt ost ostt
```


#### Notes
1. *.asrt and *.slt files have timestamps and, *.mt and *.asr do not have them. 
2. For using ``MTeval``, ``SLTeval``, ``ASReval`` commands, you do not need to follow naming templates, it is the ``-f`` parameter that specifies the use of the file.
3. You can evaluate several hypotheses at once. Also, you can use short file formats. For example, the following commands are equal:

```
MTeval -i file1 hypo1 file2 hypo2 -f ref mt ref mt
```
OR
```
MTeval -i file1 hypo1 file2 hypo2 -f ref mt
```
4. You can use the pipeline as input instead of ``-i`` parameter, for example, the following commands are equal: 

```
MTeval -i file1 hypo1 file2 hypo2 -f ref mt
```
OR
```
echo "file1 hypo1" |  MTeval -f ref mt
```


## Terminology and Abbreviations

* OSt  ... original speech manually transcribed (i.e. golden transcript)
* OStt ... original speech manually transcribed with word-level timestamps
* mt   ... the unrevised output of text-based translation; the source of MT can be .asr (machine-transcribed OS) or .OSt (human-transcribed OS)
* slt  ... timestamped online MT hypothesis, i.e. the output of an MT system ran in online mode, with timestamps recorded
* asr  ... the unrevised output of a speech recognition system
* asrt ... the unrevised output of speech recognition system; timestamped at the word level

    


