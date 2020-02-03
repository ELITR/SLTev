# SLTev
SLTev is a tool for comprehensive evaluation of (simultaneous) spoken language translation.

Run SLTev.py as follow:
	python SMT.py --asr sampls/ASR --ref sampls/reference sampls/reference  --mt sampls/OUT-MT --ref_d 2 -d 0 --align giza++/Result.A3.final giza++/Result.A3.final --b_time 300

	
	parameters:
		--asr: Refers to ASR (time-stamped transcript) file. 
		--ref: Refers to reference files. [contains list of references]
		--mt: Refers to MT file.
		-d: Refers to delay types. [0,1 two type for dalay calculation, default is 0]
		--ref_d: Refers to delay reference type. [0,1,2 refer to 3 types of delay calculation]
		--align: Refers to alignment files. [contains list of aligns], it's optional. 
                --b_time: Refers to the slots length time to calculate blue score (default is 200)

# Terminology

In the following, we use this notation:

* OS  ... original speech (sound)
* OSt ... original speech manually transcribed with word-level timestamps
* IS  ... human interpreter's speech (sound)
* ISt ... IS manually transcribed with word-level timestamps
* TT ... human textual translation, created from transcribed original speech (OSt); corresponds sentence-by-sentence to OSt

* ASR ... unrevised output of speech recognition system; timestamped at the word level
* SLT ... unrevised output of spoken language translation, i.e. sentences in the target language corresponding to sentences in the source language; the source of SLT is OS
* MT  ... unrevised output of text-based translation; the source of MT is ASR (machine-transcribed OS) or OSt (human-transcribed OS)

# SLTev Modes of Operation

SLTev is designed to support these modes of operation:

* Evaluate SLT against OSt+TT. (This is the primary goal of SLTev, evaluate output of SLT systems against time-stamped source + reference translation)
* Evaluate ASR+SLT agains OSt+TT. (A refined version of the previous, when the SLT system can provide internal details about ASR operation, esp. emission timestamps.)
* Evaluate IS against OSt+TT. (This is an interesting contrastive use of SLTev, to evaluate human interpreters against manually translated correct transcripts.)
* Evaluate MT against TT. (This is plain old MT evaluation.)
* Evaluate ASR against OSt. (This is plain old ASR evaluation, except the segmentation is not prescribed.)
