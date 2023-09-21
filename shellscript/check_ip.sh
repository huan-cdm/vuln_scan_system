#! /bin/bash
num=`ping ${1} -c 3 | grep "ttl" | awk -F ' ' '{print $6}' | uniq | sed 's/ttl=//'`

if [ ${num} -lt 100  ];then
    echo "Linux"
elif [ ${num} -ge 100 ];then
    echo "Windows"
else
    echo "Not Found"
fi