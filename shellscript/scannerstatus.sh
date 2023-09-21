#! /bin/bash
case "${1}" in
    fscanstatus)
	ps_fscan=`ps -aux | grep fscan_amd64` 
	echo "${ps_fscan}"
	;;

	nmapstatus)
	ps_nmap=`ps -aux | grep /usr/bin/nmap | wc -l`
	if (( $ps_nmap > 1 ))
	then
		echo "正在运行中......"
	else
		echo "已停止"
	fi
	;;

	dirsearchstatus)
	ps_dirsearch=`ps -aux | grep dirsearch.py | wc -l`
	if (( $ps_dirsearch > 1 ))
	then
		echo "正在运行中......"
	else
		echo "已停止"
	fi
	;;

	subDomainsBrutestatus)
	ps_subDomainsBrute=`ps -aux | grep subDomainsBrute.py | wc -l`
	if (( $ps_subDomainsBrute > 1 ))
	then
		echo "正在运行中......"
	else
		echo "已停止"
	fi
	;;

	vulmapscanstatus)
	ps_vulmapscan=`ps -aux | grep vulmapscan.sh | wc -l`
	if (( $ps_vulmapscan > 2 ))
	then
		echo "正在运行中......"
	else
		echo "已停止"
	fi
	;;

	
	httpxscanstatus)
	ps_httpxscan=`ps -aux | grep run_httpx.sh | wc -l`
	if (( $ps_httpxscan > 2 ))
	then
		echo "正在运行中......"
	else
		echo "已停止"
	fi
	;;

	#batchfofa
	batchfofastatus)
	ps_batchfofa=`ps -aux | grep batchfofa_start.py | wc -l`
	if (( $ps_batchfofa > 1 ))
	then
		echo "正在运行中......"
	else
		echo "已停止,点击下载按钮下载扫描结果"
	fi
	;;


	batchfofafilenumstatus)
	ps_batchfilenumfofa=`cat /TIP/flask_cnvd/file_txt/batchfofatarget.txt | wc -l`
	if (( $ps_batchfilenumfofa > 1 ))
	then
		echo "目标文件已存在,点击批量检索进行扫描"
	else
		echo "目标文件不存在,在目录扫描模块上传成功后进行扫描"
	fi
	;;

	#文件清洗服务运行状态
	fileclean)
	ps_fileclean=`ps -aux | grep filterdirsearchdata.sh | wc -l`
	if (( $ps_fileclean > 2 ))
	then
		echo "正在运行中......"
	else
		echo "已停止"
	fi
	;;


esac