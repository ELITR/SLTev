
Title: ASRev
authors: Ebrahim Ansari, Ondrej Bojar, Mohammad Mahmoudi
Date: 23/04/2020
Acknowledgment: XXX
---

# ASRev

ASRev is a script for the comprehensive evaluation of (simultaneous) the unrevised output of speech recognition system; timestamped at the word level (ASR).


## Input files

    a) OStt file (original song time-stamped transcript file)  or OSt file  
    b) asr file (timestamped at the word)

## Requirements

### mwerSegmenter
    
    a) chmod +x mwerSegmenter
	  
### jiwer

	a) pip install jiwer	

### mosestokenizer

	a) pip install mosestokenizer
	
## Usage

    Run ASRev.py as follow:
        python ASRev.py --ostt ostt --asr asr

    parameters:
        --ostt: Refers to the OStt file. 
		--asr: Refers to the ASR file. 

        
## Terminology

In the following, we use this notation:

* OStt ... original speech manually transcribed with word-level timestamps
* ASR ... the unrevised output of speech recognition system; timestamped at the word level
