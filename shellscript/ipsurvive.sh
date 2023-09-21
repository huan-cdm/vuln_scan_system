#! /bin/bash
for kk in `cat /TIP/flask_cnvd/samplesurvive/survivequchong.txt`
   do
    ping -c 2 -i 0.3 -W 1 ${kk} &>/dev/null
     if [ $? -eq 0 ];then
         echo "${kk}" >> /TIP/flask_cnvd/samplesurvive/surviveresult.txt
      fi
   done