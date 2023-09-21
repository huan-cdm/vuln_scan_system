#! /bin/bash

python3 /TIP/flask_cnvd/vulmap-0.9/vulmap.py -f /TIP/flask_cnvd/file_txt/dirsearchtarget.txt -a ${1} --timeout ${2} --delay ${3} -t ${4} --output-text /TIP/flask_cnvd/file_txt/vulmapscanresult.txt  > /TIP/flask_cnvd/file_txt/vulmapscanresult_tmp.txt