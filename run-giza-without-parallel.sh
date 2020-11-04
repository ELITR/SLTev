while getopts s:t:o: flag
do
    case "${flag}" in
    s) ost_file=${OPTARG};;
    t) tt_file=${OPTARG};;
    o) out_folder=${OPTARG};;
    esac
done


if [ ! -d "./SLTev-cache/mgiza/mgizapp/bin/" ]; then
  git clone https://github.com/moses-smt/mgiza.git; 
  mv ./mgiza/ ./SLTev-cache/;
  cd ./SLTev-cache/mgiza/mgizapp;
  cmake .;
  make;
  make install;
  cd ../../../;
fi
cp ./giza++/run.sh ./SLTev-cache/mgiza/mgizapp/bin/;
cp ./giza++/configfile ./SLTev-cache/mgiza/mgizapp/bin/;
cp ./giza++/merge_alignment.py ./SLTev-cache/mgiza/mgizapp/bin/;
cp $ost_file ./SLTev-cache/mgiza/mgizapp/bin/data.en;
cp $tt_file ./SLTev-cache/mgiza/mgizapp/bin/data.vn;
chmod +x ./SLTev-cache/mgiza/mgizapp/bin/run.sh;
cd ./SLTev-cache/mgiza/mgizapp/bin/;
bash run.sh;
cat out.txt > ../../../../$out_folder;
rm *.*;
cd ../../../../;
