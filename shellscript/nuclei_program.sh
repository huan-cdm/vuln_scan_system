#! /bin/bash
case "${1}" in
    #开启nuclei扫描
    startnuclei)
    #   常用参数（https://blog.csdn.net/qq_35607078/article/details/131648824）
    #   -bulk-size 限制并行的主机数 默认25 
    #   -c 限制并行的模板数 默认25
    #   -rate-limit 每秒发送的最大请求数 默认150 
    #   -l 批量扫描
    #   -t 要运行的模板或模板目录列表
    #   -timeout 超时前等待的时间(以秒为单位) 默认 10秒
	/TIP/flask_cnvd/nuclei_server/nuclei -l /TIP/flask_cnvd/file_txt/dirsearchtarget.txt -t $2 -c 10 -bulk-size 5  -rate-limit 10 -timeout 3 > /TIP/flask_cnvd/file_txt/nucleiresult.txt
	;;

    #nuclei模板文件查看
    templatenuclei)
    templatenuclei_result=`find $2 -type f`
    echo "${templatenuclei_result}"
    ;;

    #nuclei状态查询
    nucleistatus)
    ps_nuclei=`ps -aux | grep "/TIP/flask_cnvd/nuclei_server/nuclei" | wc -l`
	if (( $ps_nuclei > 1 ))
	then
		echo "正在运行中......"
	else
		echo "已停止"
	fi
    ;;

	


esac