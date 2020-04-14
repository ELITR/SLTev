#! /bin/bash
# we suppose that $1 is OStt and $2 is tt  $3 is mt $4 is output path
#-------- make source 
python giza++/transcript_to_source.py $1 > source_ref; 
#-------- giza++ 
git clone https://github.com/lngvietthang/giza-pp.git; 
cd giza-pp; 
make;
#-------- run giza 
mkdir run_giza;
cd run_giza;
cp ../../giza++/run.sh .;
chmod +x run.sh;
cp ../../source_ref .;
cp $2 ./tt;
#------- run giza over cs-en
mkdir out_folder;
bash run.sh tt source_ref ./out_folder;
cat out_folder/Result.A3.final > ../../ref_alignment;
cd ../../;
#-------- mwerSegmenter
chmod +x mwerSegmenter; 
#-------- run sltev 
python SLTev.py --ostt $1 --tt $2 --mt $3 --align ref_alignment --b_time 3000;
