#! /bin/bash
#过滤vulmap漏洞扫描结果
cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i $1 -B $2 > /TIP/flask_cnvd/file_txt/vulmapscanfilterresult.txt