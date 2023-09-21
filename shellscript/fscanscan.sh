#! /bin/bash
case "${1}" in
    fscanstart)
	/TIP/flask_cnvd/fscan/fscan_amd64 -hf /TIP/flask_cnvd/file_txt/fscantarget.txt -p $2 > /TIP/flask_cnvd/file_txt/fscan_1.txt
	;;

	fscansync)
    num=`cat /TIP/flask_cnvd/file_txt/filterfscan.txt | wc -l`
    if (( $num == 0 ))
    then
        #echo "不存在过滤数据"
        cat /TIP/flask_cnvd/file_txt/fscan.txt > /TIP/flask_cnvd/file_txt/fscan_tmp.txt
        mv /TIP/flask_cnvd/file_txt/fscan_tmp.txt /TIP/flask_cnvd/file_txt/fscan.txt
    else
        #echo "存在过滤数据"
        for i in `cat /TIP/flask_cnvd/file_txt/filterfscan.txt`
        do
            cat /TIP/flask_cnvd/file_txt/fscan.txt  | grep -v ${i} > /TIP/flask_cnvd/file_txt/fscan_tmp.txt
            mv /TIP/flask_cnvd/file_txt/fscan_tmp.txt /TIP/flask_cnvd/file_txt/fscan.txt
        done
        
    fi
	;;
    fscannum)
    num=`cat /TIP/flask_cnvd/file_txt/fscantarget.txt | wc -l`
	echo "${num}"
    ;;

esac