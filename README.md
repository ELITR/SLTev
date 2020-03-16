---
Title: SLTev
authors: Ebrahim Ansari, Ondrej Bojar, Mohammad Mahmoudi
Date: 02/02/2020
Acknowledgement: XXX
---

# SLTev

SLTev is a tool for comprehensive evaluation of (simultaneous) spoken language translation.

##Input files:
	a) asr file (for source language, e.g. in English (ami_devset.IS1001a.OStt file)) 	
	b) mt_transalte files (for destination languages, e.g. in Czech and Danish (ami_devset.ref.de.correctOrder, ami_devset.ref.cs.correctOrder))
	c) reference file (contains sentences in each target languages) 



## Requirements

### giza++
 To use it, we first need to convert the ASR data to the GIZA++ format with transcript_to_source.py script. After that we need to install and use GIZA++ as follow. In the end of this step "Result.A3.final" file, which is one of the SLTEV script inputs is generated. 

#### Running transcript_to_source.py Script

	a) python transcript_to_source.py asr_file > source_ref
		1) asr_file is the input ASR file. 
		2) source_ref is the output file. 

#### install GIZA++

	a) git clone https://github.com/lngvietthang/giza-pp.git
	b) cd giza-pp
	c) make  
	d) Will be Created two folders GIZA++-V2 AND MKCLS-V2


#### Running GIZA++

	a) cd giza-pp; mkdir run_giza; cd run_giza;
	b) put run.sh in this folder (cp ~/Downloads/run.sh .)
	c) sudo chmod +x run.sh
	d) mkdir "cs/de_folder"  (two folder for cs and de (or more per each translation languages))
	d) ./run.sh "target_ref" "source_ref" "cs/de_folder" 
	e) Output alingment file is "cs/de_folder/Result.A3.final" 
	f) Important notes:
		1) Count of corpuse lines must be greater than 10
		2) Corpuses must be  equel.
		3) Corpouses mustn't contain '#'
		4) Don't put "/" after "cs/de_folder" (cs/de_folder/ is not true)

### NLTK [1]

	pip install --user -U nltk

### mwerSegmenter [2]
	
	a) Put mwerSegmenter (a compiled file) in the same folder.  
  	b) sudo chmod +x mwerSegmenter 


## Usage

	Single-Reference: Run SLTev.py as follow:
		python SLTev.py --asr samples/asr --ref samples/reference --mt samples/mt --align samples/Result.A3.final --b_time 300

	Multi-Reference: Run SLTev.py as follow:
		python SLTev.py --asr samples/asr --ref samples/reference1 samples/reference2  --mt samples/MT --align samples/Result.A3.final1 samples/Result.A3.final2 --b_time 300
	
	
	parameters:
		--asr: Refers to ASR (time-stamped transcript) file. 
		--ref: Refers to reference files. [contains list of references]
		--mt: Refers to MT file.
		--align: Refers to alignment files. [contains list of aligns], it's optional. 
		--b_time: Refers to the slots length time to calculate blue score (default is 200).

### Real example
 
	a)  python SLTev.py --asr inputs/ami_devset.IS1001a.OStt --mt inputs/cs_out.mt --ref  inputs/ami_devset.ref.cs.correctOrder --align inputs/cs_Result.A3.final 

## Terminology

In the following, we use this notation:

* OS  ... original speech (sound)
* OSt ... original speech manually transcribed
* OStt ... original speech manually transcribed with word-level timestamps
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
