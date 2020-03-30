#! /bin/bash

# we suppose that $1 is asr and $2 is reference  $3 is mt and $4 is parallel_source and $5 is  parallel_ref $6 is output path 


#-------- downnload parallel corpuse from europall in http://www.statmt.org/europarl/ address.

#if [ !  -d "/parallel_corpuse" ]
#then
#        mkdir  parallel_corpuse
#fi
 
#mkdir  parallel_corpuse
#wget http://www.statmt.org/europarl/v7/cs-en.tgz 
#wget http://www.statmt.org/europarl/v7/de-en.tgz 
#mv cs-en.tgz ./parallel_corpuse/ 
#mv de-en.tgz ./parallel_corpuse/ 
#cd parallel_corpuse 
#tar zxvf cs-en.tgz 
#tar zxvf de-en.tgz 

# europarl-v7.cs-en.cs  europarl-v7.cs-en.en are created.
# europarl-v7.de-en.de europarl-v7.de-en.en are created.

#cd .. 
#-------- make source 
python giza++/transcript_to_source.py $1 > source_ref 

#-------- concat source_ref and reference with parallel data 
mkdir concat_data
cat $5 $2 > concat_data/ref_concat
cat $4 source_ref > concat_data/source_concat

 
#-------- giza++ 
git clone https://github.com/lngvietthang/giza-pp.git 
cd giza-pp 
make

#-------- run giza 
mkdir run_giza
cd run_giza
cp ../../giza++/run.sh .
chmod +x run.sh
cp ../../source_ref .
cp ../../concat_data/ref_concat ref_concat
cp ../../concat_data/source_concat source_concat


#------- run giza 
mkdir out_folder
./run.sh ref_concat source_concat ./out_folder

var1=$(wc -l source_ref)

num_line="$(cut -d' ' -f1 <<<"$var1")"
num_line1=$(($num_line * 3))
tail -n $num_line1 out_folder/Result.A3.final > ../../ref_alignment



cd ../../
#-------- mwerSegmenter

chmod +x mwerSegmenter 

#-------- run sltev 

python SLTev.py --asr $1 --ref $2 --mt $3 --align ref_alignment --b_time 300 > $6


