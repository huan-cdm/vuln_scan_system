#! /bin/bash
#cat /var/log/auth.log | grep $1 > /var/log/tmp_auth.log

if [ ! -n "$1" ] ;then
    cat /var/log/auth.log > /TIP/flask_cnvd/log/tmp_auth.log
else
    cat /var/log/auth.log | grep $1 > /TIP/flask_cnvd/log/tmp_auth.log
fi
