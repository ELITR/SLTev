# SLTev 
![PyPI version](https://img.shields.io/pypi/wheel/SLTev?label=%20PyPI)
![python version](https://img.shields.io/pypi/pyversions/SLTev)
![licence](https://img.shields.io/pypi/l/SLTev)


SLTev is a tool for comprehensive evaluation of (simultaneous) spoken language translation. 

# Table of Contents
1. [What is SLTev?](#SLTev)
2. [Requirements](#Requirements)
3. [File-Naming-Convention](#File-Naming-Convention)
    1. [Golden Transcripts](#Golden-Transcripts)
    2. [Word Alignment](#Word-Alignment)
    3. [System Outputs from Translation](#System-Outputs-from-Translation)
    4. [System Outputs from ASR](#System-Outputs-from-ASR)
4. [Package Overview](#Package-Overview)
5. [Evaluating](#Evaluating)
6. [Evaluating on elitr-testset](#Evaluating-on-elitr-testset)
7. [Evaluating with Your Custom Reference Files](#Evaluating-with-Your-Custom-Reference-Files)
    1.  [Evaluating MT](#Evaluating-MT)
    2.  [Evaluating SLT](#Evaluating-SLT)
    3.  [Evaluating ASR](#Evaluating-ASR)
    4.  [Evaluating ASRT](#Evaluating-ASRT)
    5.  [Multi-docs Evaluation](#Multi-docs)
    6.  [Notes](#Notes)
9. [Parsing index files](#Parsing-index-files)
10. [Terminology and Abbreviations](#Terminology-and-Abbreviations)
11. [CREDITS](#CREDITS)


# SLTev <a name="SLTev"></a>

SLTev is an open-source tool for assessing the quality of spoken language translation (SLT) in a comprehensive way. Based on timestamped golden transcript and reference translation into a target language, SLTev reports the quality, delay and stability of a given SLT candidate output.

SLTev can also evaluate the intermediate steps alone: the output of automatic speech recognition (ASR) and machine translation (MT).

You can see our short presentaion at ``EACL 2021 - System Demonstration`` here: https://slideslive.com/38954658  
Full details in the paper (bibtex below): https://www.aclweb.org/anthology/2021.eacl-demos.9

## Requirements <a name="Requirements"></a>

- python3.6 or higher
- some pip-installed modules:
  - sacrebleu, sacremoses
  - gitpython, gitdir, filelock
- mwerSegmenter 

## File Naming Convention <a name="File-Naming-Convention"></a>

Depending on whether your system produces (spoken language) translation (SLT), or just the speech recognition (ASR), you should use the following naming template of your input and output files.

### Golden Transcripts: ``.OSt``, ``.OStt`` <a name="Golden-Transcripts"></a>
- &lt;file-name&gt; . &lt;language&gt; . &lt;OSt/OStt&gt;
- e.g. ``kaccNlwi6lUCEM.en.OSt``, ``kaccNlwi6lUCEM.cs.OStt``

### Word Alignment for Better Estimation: ``.align`` <a name="Word-Alignment"></a>
- &lt;file-name&gt; . &lt;source-language&gt; . &lt;target-language&gt; . &lt;align&gt;
- e.g. ``kaccNlwi6lUCEM.en.de.align``

### System Outputs from Translation: ``.slt``, ``.mt`` <a name="System-Outputs-from-Translation"></a>
- &lt;file-name&gt; . &lt;source-language&gt; . &lt;target-language&gt; . &lt;slt/mt&gt;
- e.g. ``kaccNlwi6lUCEM.en.de.slt``, ``kaccNlwi6lUCEM.cs.en.mt``

### System Outputs from ASR: ``.asr``, ``.asrt`` <a name="System-Outputs-from-ASR"></a>
- &lt;file-name&gt; . &lt;source-language&gt; . &lt;source-language&gt; . &lt;asr/asrt&gt;
- e.g. ``kaccNlwi6lUCEM.en.en.asr``

## Installation <a name="Installation"></a>

Install the Python module (Python 3 only)
   
``` 
pip3 install SLTev
```
    
Also, you can install from the source:

``` 
python3 setup.py install
```

## Package Overview <a name="Package-Overview"></a>

- SLTev: Contains scripts for running SLTev
- sample-data: Contains sample input and output files
- test: Test files

## Evaluating <a name="Evaluating"></a>


![SLTev architecture](https://raw.githubusercontent.com/ELITR/SLTev/4a1c846c1d94bb49b92878cd452953c8e7633f30/docs/SLTev-elitr-testset-connection.svg)

SLTev has four types of evaluating modules that each one of which supports multiple input and candidate files and calculates score types.

In the following table, for each module, input, candidate, and score types are shown. 

<table > 
<thead>
	<tr>
		<th rowspan="2">Module</th>
		<th colspan="4">Input types</th>
		<th colspan="4">Candidate types</th>
    <th colspan="4">Score types</th>
	</tr>
</thead>
<tbody>
	<tr >
    <td> </td>
    <td >OStt</td>
    <td >OSt</td>
    <td >Ref</td>
    <td >Align</td>
    <td >SLT</td>
    <td >MT</td>
    <td >ASRT</td>
    <td >ASR</td>
    <td >Delay</td>
    <td >Quality</td>
    <td >Flicker</td>
    <td >WER</td>
	</tr>
  	<tr>
    <td> SLTeval</td>
    <td >X</td>
    <td ></td>
    <td >X</td>
    <td >Optional</td>
    <td >X</td>
    <td ></td>
    <td ></td>
    <td ></td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
    <td ></td>
	</tr>
    	<tr>
    <td> MTeval</td>
    <td ></td>
    <td ></td>
    <td >X</td>
    <td ></td>
    <td ></td>
    <td >X</td>
    <td ></td>
    <td ></td>
    <td ></td>
    <td >X</td>
    <td ></td>
    <td ></td>
	</tr>
	<tr>
    <td> ASReval</td>
    <td >X</td>
    <td >X</td>
    <td ></td>
    <td ></td>
    <td ></td>
    <td ></td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
	</tr>
	<tr>
    <td> SLTev -e</td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
    <td >Optional</td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
    <td >X</td>
	</tr>

  
</tbody>
</table>


Moreover, SLTev works with elitr-testset and can automatically use the growing collection of input files of elitr-testset.
Each index in elitr-testset has been created for a specific domain and purpose, containing the list of all relevant files in the **documents** directory in the elitr-testset. SLTev can generate a simple (flat) directory with all files belonging to an index, so that the user does not have to navigate the directory structure, using SLTev with the -g parameter. When SLTev is called this way for the first time, it clones elitr-testset repository to the local system and copies the desired files to the output directory. In subsequent calls, the local clone of the repository is used. After input files are generated, SLTev can evaluate user hypothesis files with generated input files by its modules.


### Evaluating on ``elitr-testset`` <a name="Evaluating-on-elitr-testset"></a>

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

### Evaluating with Your Custom Reference Files <a name="Evaluating-with-Your-Custom-Reference-Files"></a>

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

Please note that candidate files must be at the **before** or **after** of their input files. In the following examples, A and B are correct and C is not.

A) SLTeval -i slt_pth ostt_path ref_path -f slt ostt ref 

B) SLTeval -i ostt_path ref_path slt_path -f ostt ref slt

C) SLTeval -i ostt_path slt_path ref_path -f ostt slt ref


#### Evaluating MT <a name="Evaluating-MT"></a>

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

If you want to calculate the COMET score as well, you need to include the ost file in the source language as src as shown below:
'''
MTeval -i sample-data/sample.en.cs.mt sample-data/sample.en.OSt sample-data/sample.cs.OSt -f mt src ref
'''
This would add an additional line in the output reporting the COMET score:
'''
tot      COMET         docAsWhole             0.770
'''
This is optional.

#### Evaluating SLT <a name="Evaluating-SLT"></a>

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
Similar to MTeval, to calculate COMET score, you need to include the ost file in the source language.


#### Evaluating ASR <a name="Evaluating-ASR"></a>

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
Here we learn that the WER score (lower is better) for this sample file varies between .265 and .323 depending on the pre-processing technique. In ASR research, the most common pre-processing strategy is what we call LPW, i.e. lowecase, remove punctuation and use mWERsegmenter to mimic the segmentation of the reference transcript. If we consider casing and punctuation (labelled WM), the score gets naturally worse.

#### Evaluating ASR with timing (ASRT)  <a name="Evaluating-ASRT"></a>

ASRT is like SLT but in the source language, i.e. evaluating the time-stamped output of an ASR system (``asrt``) against the golden transcript which has to be provided twice: without timestamps (``ost``) and with timing and partial segments (``ostt``). All the files are in the same language and the ``ost`` file must have the exact same number of segments as there are "C"omplete segments in the ``ostt`` file.

```
ASReval -i file1 file2 ... -f file1_format file2_format ...
# To reduce the number of scores, add --simple 
``` 
Demo example: 
``` 
ASReval -i sample-data/sample.en.en.asrt sample-data/sample.en.OSt sample-data/sample.en.OStt -f asrt ost ostt
```

#### Multi-docs Evaluation <a name="Multi-docs"></a>

If you have a file with multiple documents, you can use SLTev modules with ``--docs`` parameter for evaluation. You need to add a separation token to the input and candidate files to separate documents (default is ``###docSpliter###``). Please notice that all input and candidate files must contain the separation token and the number of documents must be equal. Also, the language of each document in a multi-docs file should be equal. 

```
SLTeval/ASReval/MTeval -i file1 file2 ... -f file1_format file2_format ... --docs
# To reduce the number of scores, add --simple 
# To use multi-docs evaluation, add --docs
# To use your separation token, add --splitby "YOURTOKEN" (default is "###docSpliter###")
``` 


#### Notes <a name="Notes"></a>
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

## Parsing index files <a name="Parsing-index-files"></a>
See `SLTev/index_parser.py` for detailed description. Structure of the index file:
```
# SRC -> *.<EXTENSION>
# REF -> *.<EXTENSION>
# ALIGN -> *.<EXTENSION>
PATH_TO_DIRECTORY
PATH_TO_ANOTHER_DIRECTORY_WITH_SAME_EXTENSIONS

# SRC -> *.<EXTENSION>
# REF -> *.<EXTENSION>
PATH_TO_DIRECTORY_WITH_DIFFERENT_EXTENSIONS
```

`SRC` and `REF` annotations are mandatory. Specifying a `SRC` annotation "clears" the rest of the annotations.

Usage:
```
SLTIndexParser path_to_index_file path_to_dataset
```

5. It must be noted that a stable internet connection is necessary in order to download the COMET model to the local
system to calculate the COMET score.

## Terminology and Abbreviations <a name="Terminology-and-Abbreviations"></a>

* OSt  ... original speech manually transcribed (i.e. golden transcript)
* OStt ... original speech manually transcribed with word-level timestamps
* mt   ... the unrevised output of text-based translation; the source of MT can be .asr (machine-transcribed OS) or .OSt (human-transcribed OS)
* slt  ... timestamped online MT hypothesis, i.e. the output of an MT system ran in online mode, with timestamps recorded
* asr  ... the unrevised output of a speech recognition system
* asrt ... the unrevised output of speech recognition system; timestamped at the word level


## CREDITS <a name="CREDITS"></a>

If you use SLTev, please cite the following:

```
@inproceedings{ansari-etal-2021-sltev,
    title = "{SLTEV}: Comprehensive Evaluation of Spoken Language Translation",
    author = "Ansari, Ebrahim  and
      Bojar, Ond{\v{r}}ej  and
      Haddow, Barry  and
      Mahmoudi, Mohammad",
    booktitle = "Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations",
    month = apr,
    year = "2021",
    address = "Online",
    publisher = "Association for Computational Linguistics",
    url = "https://www.aclweb.org/anthology/2021.eacl-demos.9",
    pages = "71--79",
}
```
