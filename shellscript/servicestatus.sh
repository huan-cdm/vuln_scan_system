#! /bin/bash
case "${1}" in
    elasticsearch)
	es=`ps -aux | grep elasticsearch | wc -l`
	if [ ${es} -gt 4 ];then
		echo -e "已启动"
	elif [ ${es} -le 4 ];then
		echo -e "已关闭"
	fi
	;;

    pythons)
	py=`ps -aux | grep main.py | wc -l`
	if [ ${py} -ge 2 ];then
		echo -e "已启动"
	elif [ ${py} -le 1 ];then
		echo -e "已关闭"
	fi
	;;

    mysql)
	mysqls=`ps -aux | grep mysql | wc -l`
	
	if [ ${mysqls} -ge 5 ];then
		echo -e "已启动"
	elif [ ${mysqls} -le 4 ];then
		echo -e "已关闭"
	fi
	;;

    stop_es)
	#关闭Elasticsearch服务
	pides=`ps -aux | grep elasticsearch | awk -F " " '{print $2}'`
	for aes in ${pides}
	do
		kill -9 ${aes}
	done

	es1=`ps -aux | grep elasticsearch | wc -l`
	if [ ${es1} -gt 4 ];then
		echo -e "已启动"
	elif [ ${es1} -le 4 ];then
		echo -e "已关闭"
	fi
    ;;

    restart_es)
	#重启Elasticsearch服务
	repides=`ps -aux | grep elasticsearch | awk -F " " '{print $2}'`
	for aesre in ${repides}
	do
		kill -9 ${aesre}
	done
    nohup runuser -l es -c '/usr/elasticsearch-8.2.2/bin/elasticsearch -d'  > /TIP/flask_cnvd/nohup.out &
    ;;

    restart_mysql)
	#重启mysql服务
	service mysql restart
    ;;

    stop_mysql)
	#关闭mysql服务
	service mysql stop
    ;;

    stop_flask)
	#关闭flask服务
	piddf=`ps -aux | grep main.py | grep python3 |awk -F " " '{print $2}'`
	for ii in ${piddf}
	do
		kill -9 ${ii}
	done
	
esac