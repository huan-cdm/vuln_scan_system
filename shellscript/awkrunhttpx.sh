#! /bin/bash
case "${1}" in
    #查找httpx动态结果文件的最后一行
    tail_httpx)
    tail_httpx_result=`tail -n 1 /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp.txt`
    echo "${tail_httpx_result}"
	;;
    #查找文件行数
    httpx_rows)
    httpx_rows_result=`grep -n $2 /TIP/flask_cnvd/file_txt/dirsearchtarget.txt`
    echo "${httpx_rows_result}"
    ;;
esac