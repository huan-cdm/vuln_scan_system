#! /bin/bash

if [ ! -n "$1" ] ;then
    cat /TIP/flask_cnvd/file_txt/fscan.txt > /TIP/flask_cnvd/file_txt/filterfscan.txt
else
    cat /TIP/flask_cnvd/file_txt/fscan.txt | grep $1 > /TIP/flask_cnvd/file_txt/filterfscan.txt
fi