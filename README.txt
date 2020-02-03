Run SMT.py as follow:
	python SMT.py --asr sampls/ASR --ref sampls/reference sampls/reference  --mt sampls/OUT-MT --ref_d 2 -d 0 --align giza++/Result.A3.final giza++/Result.A3.final --b_time 300

	
	parameters:
		--asr: Refers to ASR file. 
		--ref: Refers to reference files. [contains list of references]
		--mt: Refers to MT file.
		-d: Refers to delay types. [0,1 two type for calculate dalay default is 0]
		--ref_d: Refers to delay reference type. [0,1,2 refer two 3 type of calculate delay]
		--align: Refers to align files. [contains list of aligns], it's maybe null. 
                --b_time: Refers to time to calculate blue score (default is 200)



        
    



