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
