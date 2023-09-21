#! /bin/bash
#前端输入状态码，利用httpx程序进行判断，结果放到dirsearchtarge_tmp.txt，在复制到dirsearchtarget.txt文件中用于扫描。
/TIP/flask_cnvd/httpx_server/httpx -l /TIP/flask_cnvd/file_txt/dirsearchtarget.txt -mc $1 > /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp.txt