#! /bin/bash

a=`curl cip.cc/${1} | grep "地址"`
echo "${a}"