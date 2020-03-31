
Title: SLTev
authors: Ebrahim Ansari, Ondrej Bojar, Mohammad Mahmoudi
Date: 23/03/2020
Acknowledgment: XXX
---

# SLTev

SLTev is a tool for comprehensive evaluation of (simultaneous) spoken language translation.

## Input files

	a) asr file (for source language, e.g. in English (ami_devset.IS1001a.OStt file)) 	
	b) mt file (for destination languages, e.g. in Czech and Danish )
	c) reference file (contains sentences in each target languages) 

## Clone project from git 

You can Download project as follow in girhub:

	a) git clone https://github.com/lngvietthang/SLTev-master.git 
	b) cd SLTev-master 


## Requirements

### GIZA++

 To use it, we first need to convert the ASR data to the GIZA++ format with transcript_to_source.py script. After that, we need to install and use GIZA++ as follows. At the end of this step "Result.A3.final" file, which is one of the SLTEV script inputs is generated. 

#### Running transcript_to_source.py Script

	a) python giza++/transcript_to_source.py asr_file > source_ref 
	
		1) asr_file is the input ASR file. 
		2) source_ref is the output file. 
	

#### Install GIZA++

	a) git clone https://github.com/lngvietthang/giza-pp.git
	b) cd giza-pp
	c) make  
	d) cd ../
	e) Will be Created two folders GIZA++-V2 AND MKCLS-V2

#### Download and use parallel corpus

You can use parallel corpuse to imporove train of GIZA++, so you can download and extract them from http://www.statmt.org/europarl/ address or another sources. In the following you should concatation parallel data with source and reference as follow:
	a) mkdir concat_data
	b) cat parallel_ref reference > concat_data/ref_concat
	c) cat parallel_source source_ref > concat_data/source_concat  


#### Running GIZA++ with an external parallel corpus

	a) cd giza-pp  
	b) mkdir run_giza
	c) cd run_giza
	d) cp ../../giza++/run.sh .
	e) chmod +x run.sh
	f) cp ../../source_ref .
	g) cp ../../concat_data/ref_concat ref_concat
	h) cp ../../concat_data/source_concat source_concat
	l) mkdir out_folder
	m) ./run.sh ref_concat source_concat ./out_folder
 	m) Run "wc -l source_ref" and calculate the number of source_ref file and multiple by 3 and put in the nex commond (e.g. num_line = 10 --> num_line1 = (10 * 3) = 30 )
	n) tail -n $num_line1 out_folder/Result.A3.final > ../../ref_alignment
	o) cd ../../
	p) Important notes:
		1) Count of corpuse lines must be greater than 10
		2) Corpuses must be  equel.
		3) Corpouses mustn't contain '#'
		4) Don't put "/" after "out_folder" (out_folder/ is not true)
		5) num_line1 is a integer number which calculate in m section (e.g. 30)
		
#### Running GIZA++ without external parallel corpus

	a) cd giza-pp  
	b) mkdir run_giza
	c) cd run_giza
	d) cp ../../giza++/run.sh .
	e) chmod +x run.sh
	f) cp ../../source_ref .
	g) cp ../../reference ref
	h) mkdir out_folder
	l) ./run.sh ref source_ref ./out_folder
	m) cat out_folder/Result.A3.final > ../../ref_alignment
	n) cd ../../
	o) Important notes:
		1) Count of corpuse lines must be greater than 10
		2) Corpuses must be  equel.
		3) Corpouses mustn't contain '#'
		4) Don't put "/" after "out_folder" (out_folder/ is not true)

### NLTK [1]

	pip install --user -U nltk

### sacrebleu

	pip install sacrebleu

### mwerSegmenter [2]
	
  	a) chmod +x mwerSegmenter 


## Usage

	Single-Reference: Run SLTev.py as follow:
		python SLTev.py --asr asr --ref reference --mt mt --align ref_alignment --b_time 3000

	Multi-Reference: Run SLTev.py as follow:
		python SLTev.py --asr sasr --ref reference1 reference2  --mt mt --align ref_alignment1 ref_alignment2 --b_time 3000
	
	
	parameters:
		--asr: Refers to ASR (time-stamped transcript) file. 
		--ref: Refers to reference files. [contains list of references]
		--mt: Refers to MT file.
		--align: Refers to alignment files. [contains list of aligns], it's optional. 
		--b_time: Refers to the slots length time to calculate blue score (default is 3000).


### Run SLTev.py 

	a) python SLTev.py --asr $1 --ref $2 --mt $3 --align cs_alignment --b_time 300 > $4

### Runing Scripts (automatica evaluation from scratch)
To run scripts in a simple way, you can run use one of these:

#### Run SLTev-without-parallel.sh

	a) chmod +x SLTev-without-parallel.sh
	b) bash SLTev-without-parallel.sh OStt_file ref_file MT_file out_file
	c) Parameters:
		1) Ostt_file --> The path of the OStt file. 
		2) ref_file --> The path of the reference file. 
		3) Mt_file --> The path of the MT file. 
		4) out_file --> The path of the output file (results will save there). 

#### Run SLTev-with-parallel.sh

	a) chmod +x SLTev-with-parallel.sh
	b) bash SLTev-with-parallel.sh OStt_file ref_file MT_file parallel_source_file parallel_ref_file out_file
	c) Parameters:
		1) Ostt_file --> The path of the OStt file. 
		2) ref_file --> The path of the reference file. 
		3) Mt_file --> The path of the MT file. 
		4) parallel_source_file --> The path of the parallel source file. 
		5) parallel_ref_file --> The path of the parallel reference file. 
		6) out_file --> The path of the output file (results will save there).
		
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
