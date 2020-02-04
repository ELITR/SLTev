---
Title: SLTev
Authors: Ebrahim Ansari, Ondrej Bojar, Mohammad Mahmoudi(?)
Date: 02/02/2020
Acknowledgement: XXX
```

# SLTev
SLTev is a tool for comprehensive evaluation of (simultaneous) spoken language translation.

This tool is designed to evaluate systems in "Non-Native Speech Translation" shared task in IWSLT2020: http://workshop2020.iwslt.org/doku.php?id=non_native_speech_translation

## Requirements

### giza++: Follow the below instruction to install and use GIZA++ word alignment tool

	1) Install giza++:
	
		a) git clone https://github.com/lngvietthang/giza-pp.git
		
		b) cd giza-pp
		
		c) make  
		
		d) it will create two folders GIZA++-V2 AND MKCLS-V2 in the current directory
	
	2) Download a parallel corpus (contain 2 files [source, dest]):
		a) you can use europarl corpus, link: http://www.statmt.org/europarl/
	
	3) How to use it:
	
		a) cd giza-pp-master; mkdir pararllel_dataset; (copy those two parallel data in this folder)
	
		b) put run.sh in this folder (e.g., cp ~/Downloads/run.sh .)
		
		c) sudo chmod +x run.sh
		
		d) mkdir out_folder 
		
		d) ./run.sh "source_file" "target_file" "out_folder" 
		
		e) The Output alingment file is "out_folder/Result.A3.final" 
	
	5) Important notes:
	
		a) Count of corpuse lines must be greater than 10
		
		b) Corpus files should have equal lines must be  equel.
		
		c) Corpus must not contain '#'
	
	4) More help:
	
		a) https://hovinh.github.io/blog/2016-01-27-install-giza-ubuntu/ 

### NLTK [1]

	pip install --user -U nltk

### mwerSegmenter [2]

	The compiled file in the sub-directory, mwerSegmenter

## Usage
	Single-Reference: Run SLTev.py as follow:
		python SLTev.py --asr samples/asr --ref samples/reference --mt samples/mt --ref_d 2 -d 0 --align samples/Result.A3.final --b_time 300

	Multi-Reference: Run SLTev.py as follow:
		python SLTev.py --asr samples/asr --ref samples/reference1 samples/reference2  --mt samples/MT --ref_d 2 -d 0 --align samples/Result.A3.final1 samples/Result.A3.final2 --b_time 300
	
	
	parameters:
		--asr: Refers to ASR (time-stamped transcript) file. 
		--ref: Refers to reference files. [contains list of references]
		--mt: Refers to MT file.
		-d: Refers to delay types. [0,1 two type for dalay calculation, default is 0]
		--ref_d: Refers to delay reference type. [0,1,2 refer to 3 types of delay calculation]
		--align: Refers to alignment files. [contains list of aligns], it's optional. 
	            --b_time: Refers to the slots length time to calculate blue score (default is 200)

## Terminology

In the following, we use this notation:

* OS  ... original speech (sound)
* OSt ... original speech manually transcribed with word-level timestamps
* IS  ... human interpreter's speech (sound)
* ISt ... IS manually transcribed with word-level timestamps
* TT ... human textual translation, created from transcribed original speech (OSt); corresponds sentence-by-sentence to OSt

* ASR ... unrevised output of speech recognition system; timestamped at the word level
* SLT ... unrevised output of spoken language translation, i.e. sentences in the target language corresponding to sentences in the source language; the source of SLT is OS
* MT  ... unrevised output of text-based translation; the source of MT is ASR (machine-transcribed OS) or OSt (human-transcribed OS)

## SLTev Modes of Operation

SLTev is designed to support these modes of operation:

* Evaluate SLT against OSt+TT. (This is the primary goal of SLTev, evaluate output of SLT systems against time-stamped source + reference translation)
* Evaluate ASR+SLT agains OSt+TT. (A refined version of the previous, when the SLT system can provide internal details about ASR operation, esp. emission timestamps.)
* Evaluate IS against OSt+TT. (This is an interesting contrastive use of SLTev, to evaluate human interpreters against manually translated correct transcripts.)
* Evaluate MT against TT. (This is plain old MT evaluation.)
* Evaluate ASR against OSt. (This is plain old ASR evaluation, except the segmentation is not prescribed.)

## References
	[1] Steven Bird, Ewan Klein, and Edward Loper. 2009. Natural Language Processing with Python, 1st edition. OReilly Media, Inc.
	[2] Evgeny Matusov, Gregor Leusch, Oliver Bender, and Hermann Ney. 2005b. Evaluating machine translation output with automatic sentence segmentation. In International Workshop on Spoken Language Translation, pages 148–154, Pittsburgh, PA, USA.
