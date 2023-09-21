#! /bin/bash
#过滤nmap扫描结果
cat /TIP/flask_cnvd/file_txt/nmap.txt | grep $1 > /TIP/flask_cnvd/file_txt/filterfnmap.txt
mv /TIP/flask_cnvd/file_txt/filterfnmap.txt /TIP/flask_cnvd/file_txt/nmap.txt