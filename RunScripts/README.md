

# Running  Scripts 

We suppose that $1 is OStt and $2 is reference $3 is MT and $4 is output path.


### Clone Project From git 

	a) git clone https://github.com/lngvietthang/SLTev-master.git 
	b) cd SLTev-master 

#### Downnload Parallel Corpuse
Downnload parallel corpuse From Europall in http://www.statmt.org/europarl/ address. and do as bellow:

	a) mkdir  parallel_corpuse
	b) wget http://www.statmt.org/europarl/v7/cs-en.tgz 
	c) wget http://www.statmt.org/europarl/v7/de-en.tgz 
	d) mv cs-en.tgz ./parallel_corpuse/ 
	e) mv de-en.tgz ./parallel_corpuse/ 
	f) cd parallel_corpuse 
	g) tar zxvf cs-en.tgz 
	h) tar zxvf de-en.tgz 
	m)cd .. 
	n) Note:
		1) europarl-v7.cs-en.cs and europarl-v7.cs-en.en will create.
		2) europarl-v7.de-en.de and europarl-v7.de-en.en will create.

	
### Make Source
 
	a) python giza++/transcript_to_source.py $1 > source_ref 

### Concat Source_ref and Reference with Parallel Data 

	a) mkdir concat_data
	b) cat parallel_corpuse/europarl-v7.cs-en.cs $2 > concat_data/cs_concat
	c) cat parallel_corpuse/europarl-v7.cs-en.en source_ref > concat_data/cs_source_concat
	d) cat parallel_corpuse/europarl-v7.de-en.de $3 > concat_data/de_concat
	e) cat parallel_corpuse/europarl-v7.de-en.en source_ref > concat_data/de_source_concat
 
### GIZA++ 

	a) git clone https://github.com/lngvietthang/giza-pp.git 
	b) cd giza-pp 
	c) make

### Run GIZA++
 
	a) mkdir run_giza
	b) cd run_giza
	c) cp ../../giza++/run.sh .
	d) chmod +x run.sh
	e) cp ../../source_ref .
	f) cp ../../concat_data/cs_concat cs_concat
	g) cp ../../concat_data/cs_source_concat cs_source_concat
	l) cp ../../concat_data/de_concat de_concat
	m) cp ../../concat_data/de_source_concat de_source_concat

### Run GIZA++ (e.g. Run Over cs-en)

	a) mkdir cs_folder
	b) ./run.sh cs_concat cs_source_concat ./cs_folder


#### Calculate Number of Source_ref Lines 

 Run following commond to Calculate Number of Source_ref Lines (numline):

	a) wc -l source_ref    (output is numline)
	b) tail -n num_line cs_folder/Result.A3.final > ../../cs_alignment 
	c) cd ../../
	d) Note:
		1) numline is an integer number. 

	
### mwerSegmenter

	a) chmod +x mwerSegmenter 

### Run SLTev.py 

	a) python SLTev.py --asr $1 --ref $2 --mt $3 --align cs_alignment --b_time 300 > $4
	
### Run SLTev-without-parallel.sh

	a) chmod +x RunScripts/SLTev-without-parallel.sh
	b) bash RunScripts/SLTev-without-parallel.sh OStt_file ref_file MT_file out_file
	c) Parameters:
		1) Ostt_file --> The path of the OStt file. 
		2) ref_file --> The path of the reference file. 
		3) Mt_file --> The path of the MT file. 
		4) out_file --> The path of the output file (results will save there). 

### Run SLTev-with-parallel.sh

	a) chmod +x RunScripts/SLTev-with-parallel.sh
	b) bash RunScripts/SLTev-with-parallel.sh OStt_file ref_file MT_file parallel_source_file parallel_ref_file out_file
	c) Parameters:
		1) Ostt_file --> The path of the OStt file. 
		2) ref_file --> The path of the reference file. 
		3) Mt_file --> The path of the MT file. 
		4) parallel_source_file --> The path of the parallel source file. 
		5) parallel_ref_file --> The path of the parallel reference file. 
		6) out_file --> The path of the output file (results will save there). 

