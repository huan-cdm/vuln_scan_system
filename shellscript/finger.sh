#! /bin/bash
num=`nslookup ${1} | grep "Address" | wc -l | uniq`
if [ ${num} -ge 3 ];then
    echo "有CDN"
elif [ ${num} = 1 ];then
    echo "未知CDN"
else
    echo "无CDN"
fi