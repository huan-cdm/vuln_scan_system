#! /bin/bash
ip=`nslookup ${1} | grep "Address" | grep -v "127.0.0.53#53" | awk -F " " '{print $2}'`
echo "${ip}"