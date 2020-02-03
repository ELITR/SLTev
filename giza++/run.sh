#!/usr/bin/env bash
source_file=${1}
target_file=${2}
out_folder=${3}
echo "source file is ${source_file}";
../GIZA++-v2/plain2snt.out "./${source_file}" "./${target_file}";

../mkcls-v2/mkcls "-p${source_file}"   "-V ${source_file}.classes"; 

../mkcls-v2/mkcls "-p${target_file}"  "-V ${target_file}.classes"; 

../GIZA++-v2/snt2cooc.out "./${source_file}.vcb" "./${target_file}.vcb"  "./${source_file}_${target_file}.snt"  > "./${source_file}_${target_file}.snt.cooc"; 

../GIZA++-v2/GIZA++ -S "./${source_file}.vcb" -T "./${target_file}.vcb" -C "./${source_file}_${target_file}.snt" -CoocurrenceFile "./${source_file}_${target_file}.snt.cooc" -o Result -outputpath "./${out_folder}";





#../GIZA++-v2/plain2snt.out ./europarl-v7.cs-en.cs ./europarl-v7.cs-en.en;

#../mkcls-v2/mkcls -peuroparl-v7.cs-en.en  -V europarl-v7.cs-en.en.classes; 

#../mkcls-v2/mkcls -peuroparl-v7.cs-en.cs  -V europarl-v7.cs-en.cs.classes;  

#../GIZA++-v2/snt2cooc.out europarl-v7.cs-en.cs.vcb europarl-v7.cs-en.en.vcb europarl-v7.cs-en.cs_europarl-v7.cs-en.en.snt > europarl-v7.cs-en.cs_europarl-v7.cs-en.en.snt.cooc; 

#../GIZA++-v2/GIZA++ -S europarl-v7.cs-en.cs.vcb -T europarl-v7.cs-en.en.vcb -C europarl-v7.cs-en.cs_europarl-v7.cs-en.en.snt -CoocurrenceFile europarl-v7.cs-en.cs_europarl-v7.cs-en.en.snt.cooc -o Result -outputpath final_out;
