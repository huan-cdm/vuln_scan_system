#!/usr/bin/env python3
from config import fofakey
from config import batchfofanum
import sys
import base64
import requests
import json
import re
from config import fofaemail

#批量检索只开通通过IP查询域名，改为fofa语法格式
first_arg = sys.argv[1]
fofa_first_argv= 'ip="' + first_arg + '"'
fofa_first_argv_utf8 = fofa_first_argv.encode('utf-8')
fofa_first_argv_base64=base64.b64encode(fofa_first_argv_utf8)
fofa_argv_str=str(fofa_first_argv_base64,'utf-8')

#调用fofa_api
try:
    url = "https://fofa.info/api/v1/search/all?email="+fofaemail+"&key="+fofakey+"&size="+batchfofanum+"&qbase64="
    hearder={
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        }
    res = requests.get(url+fofa_argv_str,headers=hearder,allow_redirects=False)
    res.encoding='utf-8'
    restext = res.text
    resdic=json.loads(restext)
    resdicresult=resdic['results']
    #定义列表
    result_list = []
    for line in resdicresult:
        matches = re.findall(r"(http(s)?://\S+)", line[0])
        for match in matches:
            result_list.append(match[0])
    unique_list = list(set(result_list))
    print(fofa_first_argv)
    if len(unique_list) == 0:
        print("未查询到IP为"+first_arg+"相关的域名信息")
    else:
        for line1 in unique_list:
            print(line1)
except:
    pass