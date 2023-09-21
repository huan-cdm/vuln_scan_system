#! /bin/bash
case "${1}" in
    #过滤黑名单shell脚本
    value1)
	num=`cat /TIP/flask_cnvd/file_txt/filterdirsearch.txt | wc -l`
    if (( $num == 0 ))
    then
        #echo "不存在过滤数据"
        cat /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt > /TIP/flask_cnvd/file_txt/dirsearchfileresult_tmp.txt
        mv /TIP/flask_cnvd/file_txt/dirsearchfileresult_tmp.txt /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt
    else
        #echo "存在过滤数据"
        for i in `cat /TIP/flask_cnvd/file_txt/filterdirsearch.txt`
        do
            cat /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt  | grep -v ${i} > /TIP/flask_cnvd/file_txt/dirsearchfileresult_tmp.txt
            mv /TIP/flask_cnvd/file_txt/dirsearchfileresult_tmp.txt /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt
        done
        
    fi
    ;;

    #过滤白名单shell脚本
    value2)
    data1=`cat /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt | grep $2`
    echo "$data1"
    ;;


    #过滤掉出现次数大于等于5次的数据
    value4)
    for n in `cat /TIP/flask_cnvd/file_txt/thresholdvalue.txt`
    do
        cat /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt  | grep -v ${n} > /TIP/flask_cnvd/file_txt/dirsearchfileresult_tmp.txt
        mv /TIP/flask_cnvd/file_txt/dirsearchfileresult_tmp.txt /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt
    done
    ;;

    #扫描目标文件去重，过滤、保留所有
    
    #去重
    uniqfilterdirsearch)
    sort /TIP/flask_cnvd/file_txt/dirsearchtarget.txt | uniq >  /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_1.txt
    mv /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_1.txt /TIP/flask_cnvd/file_txt/dirsearchtarget.txt
    
    #黑名单过滤
    for p in `cat /TIP/flask_cnvd/file_txt/filter_vuln_url.txt`
    do
        cat /TIP/flask_cnvd/file_txt/dirsearchtarget.txt  | grep -v ${p} > /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_2.txt
        cp /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_2.txt /TIP/flask_cnvd/file_txt/dirsearchtarget.txt
    done
    ;;


    #扫描目标文件去重，过滤、只保留IP地址
    withdrawip)
    #去重
    sort /TIP/flask_cnvd/file_txt/dirsearchtarget.txt | uniq >  /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_1.txt
    mv /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_1.txt /TIP/flask_cnvd/file_txt/dirsearchtarget.txt

    #黑名单过滤
    for p in `cat /TIP/flask_cnvd/file_txt/filter_vuln_url.txt`
    do
        cat /TIP/flask_cnvd/file_txt/dirsearchtarget.txt  | grep -v ${p} > /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_2.txt
        mv /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_2.txt /TIP/flask_cnvd/file_txt/dirsearchtarget.txt
    done

    #指定文件路径
    file="/TIP/flask_cnvd/file_txt/dirsearchtarget.txt"
    #正则表达式匹配IPv4地址
    ip_pattern="(http://|https://)([0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]{1,5}"
    #使用grep命令查找所有匹配的IP地址
    grep -oE "$ip_pattern" "$file" > /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_3.txt
    mv /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_3.txt /TIP/flask_cnvd/file_txt/dirsearchtarget.txt
    ;;

    #过滤目录扫描白名单
    dirscan_white)
    dirscan_white_data=`cat /TIP/flask_cnvd/file_txt/dirsearchtarget.txt | grep $2`
    echo "$dirscan_white_data"
    ;;


esac