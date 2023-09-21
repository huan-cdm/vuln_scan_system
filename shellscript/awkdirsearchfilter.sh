#! /bin/bash
case "${1}" in
    #目录扫描日志最后5行中提取域名用于过滤
    domain)
    domain_value=`tail -n 5 /TIP/flask_cnvd/dirsearch/dirsearch.log | awk -F ' ' '{print $5}'`
    echo "${domain_value}"
	;;
    domainall)
    domainall_value=`tail -n 5 /TIP/flask_cnvd/dirsearch/dirsearch.log`
    echo "${domainall_value}"
    ;;
    ping_test)
    ping_test_value=`ping $2 -c 1 | grep icmp | awk -F ' ' '{print $4}'`
    echo "${ping_test_value}"
    ;;
    ping_test_wc)
    ping_test_value_wc=`ping $2 -c 1 | grep icmp | awk -F ' ' '{print $4}' | wc -l`
    echo "${ping_test_value_wc}"
    ;;

    #fofa目标去重
    uniqfofa_batch)
    sort /TIP/flask_cnvd/file_txt/batchfofatarget.txt | uniq >  /TIP/flask_cnvd/file_txt/batchfofatarget_tmp_1.txt
    cp /TIP/flask_cnvd/file_txt/batchfofatarget_tmp_1.txt /TIP/flask_cnvd/file_txt/batchfofatarget.txt
    sed -i '/\b\([0-9a-fA-F]\{1,4\}:\)\{7\}[0-9a-fA-F]\{1,4\}\b/d' /TIP/flask_cnvd/file_txt/batchfofatarget.txt
    ;;
esac