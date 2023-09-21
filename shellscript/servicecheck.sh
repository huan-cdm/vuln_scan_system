#! /bin/bash
#netstat -alntp | grep 5008 | grep -v "TIME_WAIT" | sed -n '1,1p' > /TIP/flask_cnvd/file_txt/servicemonit/flask.txt
#netstat -alntp | grep 3306 | grep -v "TIME_WAIT" | sed -n '2,2p' > /TIP/flask_cnvd/file_txt/servicemonit/mysql.txt

#netstat -alntp | grep 9200 | grep -v "TIME_WAIT" > /TIP/flask_cnvd/file_txt/servicemonit/es.txt
#ps -aux | grep "directoryscan.sh" | sed -n '2,2p' > /TIP/flask_cnvd/file_txt/servicemonit/dirsearch.txt

#ps -aux | grep  "fscan" | sed -n '1,1p' > /TIP/flask_cnvd/file_txt/servicemonit/fscanstatus.txt
#! /bin/bash
case "${1}" in
    web)
	netstat -alntp | grep 5008 | grep -v "TIME_WAIT" | wc -l
	;;

    mysql)
	netstat -alntp | grep 3306 | grep -v "TIME_WAIT" | wc -l
	;;
   
    dirsearch)
	ps -aux | grep dirsearch.py | wc -l
	;;

    elasticsearch)
	netstat -alntp | grep 9200 | grep -v "TIME_WAIT" | wc -l
	;;

    vulmap)
	ps -aux | grep vulmap.py | wc -l
	;;
  
esac