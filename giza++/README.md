#GIZA++

GIZA++ is an extension of the program GIZA which was developed by the Statistical Machine Translation team. In this script we are using GIZA++ to alignment. 

## install GIZA++:

	a) git clone https://github.com/lngvietthang/giza-pp.git

	b) cd giza-pp

	c) make  

	d) it creates two folders GIZA++-V2 AND MKCLS-V2


## Data preparation:

	For running GIZA++, It requires two files: source and target, which target is the reference (it contains target language sentences) file and the source which is achieved by running the following script on ASR file (number of lines in source and target must be equal).


### Running script to create Giza++ source file: 

	a) python transcript_to_source.py ../samples/asr > source_ref

		1) asr is the input time-stamped transcript file which is needed  as the input of SLTev too. 
	
		2) source_ref is the outputs of the above script and contains only completed sentences in the time-stamped transcript.


## How to use it: 

	a) cd giza-pp-master; mkdir pararllel_dataset; (put parallel data in this folder contains two files (source and target files which built in Data preperation phase))

	b) put run.sh in this folder (cp ~/Downloads/run.sh .)
	
	c) sudo chmod +x run.sh
	
	d) mkdir out_folder 
	
	d) ./run.sh "source_file" "target_file" "out_folder" 
	
	e) Output alingment file is "out_folder/Result.A3.final" 


## Important notes:

	a) you can CONCATANATE a bigger parallel corpus (e.g., downloaded from europarl corpus) to the required source-target parallel corpus to improve the accuracy of the trained model.

	b) count of corpuse lines must be greater than 10

	c) corpuses must be  equel.

	d) corpouses shouldn't contain '#'
  

## more help:
	a) https://hovinh.github.io/blog/2016-01-27-install-giza-ubuntu/