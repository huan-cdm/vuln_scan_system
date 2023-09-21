#! /bin/bash
case "${1}" in
    #提取子域名
    awksub)
    sub=`cat /TIP/flask_cnvd/file_txt/subdomain.txt | awk -F ' ' '{print $1}'`
    echo "${sub}"
	;;
    #提取IP地址
    awksubip)
    subip=`cat /TIP/flask_cnvd/file_txt/subdomain.txt | awk -F ' ' '{print $2}'`
    echo "${subip}"
	;;
esac