#! /bin/bash
case "${1}" in
	killmasscan)
	pidd=`ps -aux | grep masscan |awk -F " " '{print $2}'`
	for ii in ${pidd}
	do
		kill -9 ${ii}
    done
	;;
   	killnmap) 
	pidd=`ps -aux | grep nmap | grep -v "/bin/sh" | grep -v "auto" |awk -F " " '{print $2}'`
	for ii in ${pidd}
	do
		kill -9 ${ii}
    done
	;;

	killdirsearch)
	pidd=`ps -aux | grep "dirsearch.py" |awk -F " " '{print $2}'`
	for ii in ${pidd}
	do
		kill -9 ${ii}
    done
	;;


	killvulmap)
	pipp=`ps -aux | grep vulmap |awk -F " " '{print $2}'`
	for pp in ${pipp}
	do
		kill -9 ${pp}
    done
	;;
	

	killfscan)
	piddd=`ps -aux | grep fscan | awk -F " " '{print $2}'`
	for jj in ${piddd}
	do
		kill -9 ${jj}
	done
	;;

	killsubDomainsBrute)
	pibb=`ps -aux | grep subDomainsBrute.py | awk -F " " '{print $2}'`
	for aa in ${pibb}
	do
		kill -9 ${aa}
	done
	;;

	killelasticsearch)
	pides=`ps -aux | grep elasticsearch | awk -F " " '{print $2}'`
	for es in ${pides}
	do
		kill -9 ${es}
	done
	;;

	killbatchfofa)
	batch_fofa_pid=`ps -aux | grep batchfofa_start.py | awk -F " " '{print $2}'`
	for batch in ${batch_fofa_pid}
	do
		kill -9 ${batch}
	done
	;;

	#kill nuclei
	killnuclei)
	kill_nuclei_pid=`ps -aux | grep nuclei | awk -F " " '{print $2}'`
	for nucleiline in ${kill_nuclei_pid}
	do
		kill -9 ${nucleiline}
	done
	;;


	dirsearchtargetnum)
	num=`cat /TIP/flask_cnvd/file_txt/dirsearchtarget.txt | wc -l`
	echo "${num}"
	;;

esac