#! /bin/bash
piddd=`docker ps | grep "c225ec7d7309\|cc16809ec3a7\|1a59a03860d8\|13a28833c23c\|a4d53e5ffa62" | wc -l`
githubpid=`docker ps | grep "49883aa2c71d\|249348066d11" | wc -l`
case "${1}" in
	
	startarl)
	docker start c225ec7d7309
	docker start cc16809ec3a7
	docker start 1a59a03860d8 
	docker start 13a28833c23c
	docker start a4d53e5ffa62
	;;

	stoparl)
	docker stop c225ec7d7309
	docker stop cc16809ec3a7 
	docker stop 1a59a03860d8
	docker stop 13a28833c23c
	docker stop a4d53e5ffa62
	;;

	statusarl)
	if [ ${piddd} == 5 ];then
        	echo -e "已开启"
	elif [  ${piddd} -gt 0 ] && [ ${piddd} -lt 5 ]; then
		echo -e "正在启动或正在关闭"
	else
		echo -e "已关闭"
	fi
	;;
	#github监控平台操作
	startgithubplatform)
	docker start 49883aa2c71d
	docker start 249348066d11
	;;

	stopgithubplatform)
	docker stop 49883aa2c71d
	docker stop 249348066d11
	;;

	statusgithubplatform)
	if [ ${githubpid} == 2 ];then
        echo -e "已开启"
	elif [  ${githubpid} -gt 0 ] && [ ${githubpid} -lt 2 ]; then
		echo -e "正在启动或正在关闭"
	else
		echo -e "已关闭"
	fi
	;;

esac
