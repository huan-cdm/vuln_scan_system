#! /bin/bash
# -Pn：目标主机禁用ping，绕过ping扫描
# -sS：SYN扫描，使用最频繁，安全，快
# -sV：对端口上的服务程序版本进行扫描
#-T 1-6设置扫描速度，设置T4最好

/usr/bin/nmap -Pn -sS -sV -T4  $1  -p $2  --min-rate=$3  > /TIP/flask_cnvd/file_txt/nmap_tmp.txt