#! /bin/bash
num=`cat /TIP/flask_cnvd/samplesurvive/survive.txt | wc -l`
num_1=$(($num + 1))
echo "${num_1}"