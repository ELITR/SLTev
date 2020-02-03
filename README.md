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

OS ... original speech (sound or transcript with word-level timestamps)
IS ... human interpreter's speech (sound or transcript with word-level timestamps)
TT ... human textual translation, created from transcribed original speech; corresponds sentence-by-sentence to OS

ASR ... unrevised output of speech recognition system; timestamped at the word level
SLT ... unrevised output of spoken language translation, i.e. sentences in the target language corresponding to sentences in the source language; the source of SLT is OS
MT  ... unrevised output of text-based translation; the source of MT is ASR (machine-transcribed OS) or OS (human-transcribed OS)
