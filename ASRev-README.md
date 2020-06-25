
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

### mwerSegmenter [1]
    
    a) chmod +x mwerSegmenter
	  
### jiwer [2]

	a) pip install jiwer	

### mosestokenizer [3]

	a) pip install mosestokenizer
	
## Usage

    Run ASRev.py as follow:
        python ASRev.py --ostt ostt --asr asr

    parameters:
        --ostt: Refers to the OStt or OSt file. 
	--asr: Refers to the ASR file. 

        
## Terminology

In the following, we use this notation:

* OStt ... original speech manually transcribed with word-level timestamps
* ASR ... the unrevised output of speech recognition system; timestamped at the word level
* OSt ... original speech manually transcribed

## References

    [1] Evgeny Matusov, Gregor Leusch, Oliver Bender, and Hermann Ney. 2005b. Evaluating machine-translation output with automatic sentence segmentation. In International Workshop on Spoken Language Translation, pages 148–154, Pittsburgh, PA, USA.
    [2] Klakow, Dietrich and Jochen Peters. 2002. ISSN. 
    [3] Philipp Koehn, Hieu Hoang, Alexandra Birch, Chris Callison-Burch, Marcello Federico, Nicola Bertoldi, Brooke Cowan, Wade Shen, Christine Moran, Richard Zens, Chris Dyer, Ondřej Bojar, Alexandra Constantin and Evan Herbst. 2007. Proceedings of the ACL (Association for Computational Linguistics).
	
