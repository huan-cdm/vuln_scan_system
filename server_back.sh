#! /bin/bash
if 
[[ $1 = 'start' ]] || [[ $1 = 'stop' ]] || [[ $1 = 'startmot' ]] || [[ $1 = 'stopmot' ]]|| [[ $1 = 'restart' ]] || [[ $1 = 'status' ]] || [[ $1 = 'start_es' ]]|| [[ $1 = 'stop_es' ]];
then
	echo ""
else
	echo "
WebService start      --启动Flask和MySQL服务
WebService stop       --关闭Flask和MySQL服务
WebService startmot   --启动监控程序服务
WebService stopmot    --关闭监控程序服务
WebService restart    --重启Flask服务
WebService start_es   --启动Elasticsearch服务
WebService stop_es    --关闭Elasticsearch服务
WebService status     --查看Flask,MySQL,Elasticsearch,监控程序服务
	"
fi
	
case "${1}" in
	#开启服务
	start)
	echo ".正在启动WEB服务"
	nohup python3 /TIP/flask_cnvd/main.py > /TIP/flask_cnvd/result/main.out &
	nohup python3 /TIP/flask_cnvd/main.py > /TIP/flask_cnvd/result/main.out &
	sleep 0.1s
	echo ".WEB服务已启动"
	sleep 0.1s

	#启动MySQL
	echo ".正在启动MySQL数据库服务"
	service mysql start
	sleep 0.1s
	echo ".MySQL数据库服务启动完成"
	sleep 0.1s

	
	#WEB服务状态
	pid=`ps -aux | grep "main.py" | grep "python3" |awk -F " " '{print $2}'`
	if [ -z "${pid}" ];then
        echo -e ".WEB服务状态:\033[31m stop\033[0m"
	else
        echo -e ".WEB服务状态:\033[32m runing \033[0m"
	fi
	sleep 0.1s

	#MySQL数据库服务状态
	sql=`ps -aux | grep mysql | wc -l`
	if [ ${sql} -gt 1 ];then
		echo -e ".MySQL数据库服务状态:\033[32m runing \033[0m"
	elif [ ${sql} == 1 ];then
		echo -e ".MySQL数据库服务状态:\033[31m stop\033[0m"
	fi

	#Elasticsearch数据库服务状态
	sleep 0.1s
	es=`ps -aux | grep elasticsearch | wc -l`
	if [ ${es} -gt 2 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[32m runing \033[0m"
	elif [ ${es} == 1 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[31m stop\033[0m"
	fi
	time3=$(date "+%Y-%m-%d %H:%M:%S")
	echo '.'$time3
	;;


	#开启监控程序服务
	startmot)
	nohup python3 /TIP/flask_cnvd/service_monitoring.py > /TIP/flask_cnvd/result/service_back.out &
	echo ".监控程序已启动"
	#监控程序运行状态
	sleep 0.1s
	pid=`ps -aux | grep "service_monitoring.py" | grep "python3" |awk -F " " '{print $2}'`
	if [ -z "${pid}" ];then
        echo -e ".监控程序状态:\033[31m stop\033[0m"
	else
        echo -e ".监控程序状态:\033[32m runing \033[0m"
	fi
	;;

	#关闭监控程序服务
	stopmot)
	pidd=`ps -aux | grep service_monitoring.py | grep python3 |awk -F " " '{print $2}'`
	for ii in ${pidd}
	do
		echo ".正在结束进程${ii}"
		kill -9 ${ii}
		sleep 0.1s
	done
	sleep 0.1s
	echo ".监控程序已关闭"
	rm -rf /TIP/flask_cnvd/result/service_back.out
	sleep 0.1s

	#监控程序运行状态
	pid=`ps -aux | grep "service_monitoring.py" | grep "python3" |awk -F " " '{print $2}'`
	if [ -z "${pid}" ];then
        echo -e ".监控程序状态:\033[31m stop\033[0m"
	else
        echo -e ".监控程序状态:\033[32m runing \033[0m"
	fi
	;;

	#开启ES服务
	start_es)
	#启动Elasticsearch
	echo ".正在启动Elasticsearch数据库服务"
	nohup runuser -l es -c '/usr/elasticsearch-8.2.2/bin/elasticsearch -d'  > /TIP/flask_cnvd/result/main.out &
	sleep 0.1s
	echo ".Elasticsearch数据库服务启动完成"
	sleep 0.1s

	#Elasticsearch数据库服务状态
	sleep 0.1s
	es=`ps -aux | grep elasticsearch | wc -l`
	if [ ${es} -gt 2 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[32m runing \033[0m"
	elif [ ${es} == 1 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[31m stop\033[0m"
	fi
	;;


	#关闭ES服务
	stop_es)
	#关闭Elasticsearch服务
	pides=`ps -aux | grep elasticsearch | awk -F " " '{print $2}'`
	for aes in ${pides}
	do
		echo "正在结束进程${aes}"
		kill -9 ${aes}
	done
	sleep 0.1s
	echo ".Elasticsearch数据库服务已关闭"
	sleep 0.1s

	#Elasticsearch数据库服务状态
	sleep 0.1s
	es=`ps -aux | grep elasticsearch | wc -l`
	if [ ${es} -gt 2 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[32m runing \033[0m"
	elif [ ${es} == 1 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[31m stop\033[0m"
	fi
	;;


	#关闭服务
	stop)
	pidd=`ps -aux | grep main.py | grep python3 |awk -F " " '{print $2}'`
	for ii in ${pidd}
	do
		echo ".正在结束进程${ii}"
		kill -9 ${ii}
		sleep 0.1s
	done
	sleep 0.1s
	echo ".WEB服务已关闭"
	rm -rf /TIP/flask_cnvd/result/main.out
	sleep 0.1s
	
	#关闭MySQL
	echo ".正在关闭MySQL数据库服务"
	service mysql stop
	sleep 0.1s
	echo ".MySQL数据库服务关闭完成"
	sleep 0.1s

	

	#WEB服务状态
	pid=`ps -aux | grep "main.py" | grep "python3" |awk -F " " '{print $2}'`
	if [ -z "${pid}" ];then
        echo -e ".WEB服务状态:\033[31m stop\033[0m"
	else
        echo -e ".WEB服务状态:\033[32m runing \033[0m"
	fi

	#MySQL数据库服务状态
	sql=`ps -aux | grep mysql | wc -l`
	if [ ${sql} -gt 1 ];then
		echo -e ".MySQL数据库服务状态:\033[32m runing \033[0m"
	elif [ ${sql} == 1 ];then
		echo -e ".MySQL数据库服务状态:\033[31m stop\033[0m"
	fi
	#Elasticsearch数据库服务状态
	sleep 0.1s
	es=`ps -aux | grep elasticsearch | wc -l`
	if [ ${es} -gt 2 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[32m runing \033[0m"
	elif [ ${es} == 1 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[31m stop\033[0m"
	fi
	time3=$(date "+%Y-%m-%d %H:%M:%S")
	echo '.'$time3
	;;


	#重启服务
	restart)
	pidd=`ps -aux | grep main.py | grep python3 |awk -F " " '{print $2}'`
	for ii in ${pidd}
	do
		echo ".正在结束进程${ii}"
		kill -9 ${ii}
		sleep 0.1s
	done
	echo ".正在重启WEB服务"
	#nohup /usr/bin/python3 /TIP/flask_cnvd/main.py 1>/dev/null 2>&1 &
	nohup python3 /TIP/flask_cnvd/main.py > /TIP/flask_cnvd/result/main.out &
	sleep 0.1s
	echo ".WEB服务重启完成"
	#WEB服务状态
	pid=`ps -aux | grep "main.py" | grep "python3" |awk -F " " '{print $2}'`
	if [ -z "${pid}" ];then
        echo -e ".WEB服务状态:\033[31m stop\033[0m"
	else
        echo -e ".WEB服务状态:\033[32m runing \033[0m"
	fi
	sleep 0.1s
	#MySQL数据库服务状态
	sql=`ps -aux | grep mysql | wc -l`
	if [ ${sql} -gt 1 ];then
		echo -e ".MySQL数据库服务状态:\033[32m runing \033[0m"
	elif [ ${sql} == 1 ];then
		echo -e ".MySQL数据库服务状态:\033[31m stop\033[0m"
	fi
	#Elasticsearch数据库服务状态
	sleep 0.1s
	es=`ps -aux | grep elasticsearch | wc -l`
	if [ ${es} -gt 2 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[32m runing \033[0m"
	elif [ ${es} == 1 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[31m stop\033[0m"
	fi
	time3=$(date "+%Y-%m-%d %H:%M:%S")
	echo '.'$time3
	;;


	#服务运行状态
	status)
	sleep 0.1s
	pid=`ps -aux | grep "main.py" | grep "python3" |awk -F " " '{print $2}'`
	if [ -z "${pid}" ];then
        echo -e ".WEB服务状态:\033[31m stop\033[0m"
	else
        echo -e ".WEB服务状态:\033[32m runing \033[0m"
	fi
	#监控程序运行状态

	sleep 0.1s
	pid=`ps -aux | grep "service_monitoring.py" | grep "python3" |awk -F " " '{print $2}'`
	if [ -z "${pid}" ];then
        echo -e ".监控程序状态:\033[31m stop\033[0m"
	else
        echo -e ".监控程序状态:\033[32m runing \033[0m"
	fi

	#MySQL数据库服务状态
	sleep 0.1s
	sql=`ps -aux | grep mysql | wc -l`
	if [ ${sql} -gt 1 ];then
		echo -e ".MySQL数据库服务状态:\033[32m runing \033[0m"
	elif [ ${sql} == 1 ];then
		echo -e ".MySQL数据库服务状态:\033[31m stop\033[0m"
	fi

	#Elasticsearch数据库服务状态
	sleep 0.1s
	es=`ps -aux | grep elasticsearch | wc -l`
	if [ ${es} -gt 2 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[32m runing \033[0m"
	elif [ ${es} == 1 ];then
		echo -e ".Elasticsearch数据库服务状态:\033[31m stop\033[0m"
	fi
	time3=$(date "+%Y-%m-%d %H:%M:%S")
	echo '.'$time3
esac