#!/bin/bash
./mkcls -n10 -pdata.en -Vdata.en.vcb.classes;
./mkcls -n10 -pdata.vn -Vdata.vn.vcb.classes;
./plain2snt data.en data.vn;
./snt2cooc data.en_data.vn.cooc data.en.vcb data.vn.vcb data.en_data.vn.snt;
./mgiza configfile;
python3 merge_alignment.py src_trg.dict.A3.final.part00* > out.txt;
