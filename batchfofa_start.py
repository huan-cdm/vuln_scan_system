#!/usr/bin/env python3
import os
import time
from config import batchfofasleeptime
fofa_file = open('/TIP/flask_cnvd/file_txt/batchfofatarget.txt',encoding='utf-8')
try:
    for line in fofa_file.readlines():
        ip_domain = os.popen('python3 /TIP/flask_cnvd/batchsearch_fofa.py'+' '+line).read()
        print(ip_domain)
        time.sleep(batchfofasleeptime)
except:
    pass