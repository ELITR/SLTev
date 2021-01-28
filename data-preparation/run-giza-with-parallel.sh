while getopts s:t:o:m:n: flag
do
    case "${flag}" in
    s) ost_file=${OPTARG};;
    t) tt_file=${OPTARG};;
    o) out_file=${OPTARG};;
    m) ps_file=${OPTARG};;
    n) pt_file=${OPTARG};;
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
cat $pt_file $tt_file > ./SLTev-cache/mgiza/mgizapp/bin/data.vn;
cp $tt_file ./SLTev-cache/mgiza/mgizapp/bin/original_tt.txt;
cat $ps_file $ost_file > ./SLTev-cache/mgiza/mgizapp/bin/data.en;
chmod +x ./SLTev-cache/mgiza/mgizapp/bin/run.sh;
cd ./SLTev-cache/mgiza/mgizapp/bin/;
bash run.sh;
var1=$(wc -l original_tt.txt);
num_line="$(cut -d' ' -f1 <<<"$var1")";
num_line1=$(($num_line * 3));
tail -n $num_line1 out.txt > ../../../../$out_file;
rm *.*;
cd ../../../../;
