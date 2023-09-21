#!/usr/bin/env python3
import os
from config import black_list
from tqdm import tqdm
import time
from config import white_list
from config import switch


#提取页面上js链接存到列表函数
def js_link(): 
    #定义存取js链接的列表
    link_js_list = []
    link_result = os.popen('bash ./sub_link.sh subjs').read()
    lines = link_result.splitlines()
    for line in tqdm(lines,desc="爬取网页上js文件地址进度"):
        time.sleep(0.1)
        link_js_list.append(line)
    return link_js_list


#提取js文件中的链接到列表函数
def hidden_js_link():
    js_link_result = js_link()
    #定义存取js隐藏链接的列表
    link_hidden_js_list = []

    for j in tqdm(js_link_result,desc="爬取js文件中的隐藏目录进度"):
        time.sleep(0.1)
        js_hidd_link_result = os.popen('bash ./sub_link.sh linkjs'+''+' '+j).read()

        #将文件存入到列表
        hidden_lines = js_hidd_link_result.splitlines()
        for hiddenline in hidden_lines:
            link_hidden_js_list.append(hiddenline)
    return link_hidden_js_list


#通过黑名单过滤
def linkblack():
    link_hidden_js_list_result = hidden_js_link()
    f1 = open(file='./dicc_http.txt', mode='w')
    f2 = open(file='./dicc.txt', mode='w')
    f3 = open(file='./black.txt', mode='w')
    for a in tqdm(link_hidden_js_list_result,desc="筛选出带http(s)部分进度"):
        time.sleep(0.1)
        #提取带http/https的和不带http/https
        if "http" in a:
            f1.write(str(a)+"\n")
        else:
            f2.write(str(a)+"\n")
    #将黑名单列表写入到黑名单文件中
    for b in tqdm(black_list,desc="过滤黑名单进度"):
        f3.write(str(b)+"\n")
        time.sleep(0.1)



#通过白名单过滤
def linkwhite():
    #定义存取结果列表
    white_result_list = []

    link_hidden_js_list_result = hidden_js_link()
    f1 = open(file='./dicc_http.txt', mode='w')
    f2 = open(file='./dicc.txt', mode='w')

    for a in tqdm(link_hidden_js_list_result,desc="筛选出带http(s)部分进度"):
        time.sleep(0.1)
        #提取带http/https的和不带http/https
        if "http" in a:
            f1.write(str(a)+"\n")
        else:
            f2.write(str(a)+"\n")

    #一定要关闭文件，以确保文件被正常释放
    f1.close()
    f2.close()

    for j in tqdm(white_list,desc="过滤白名单进度"):
        res = os.popen('bash ./sub_link.sh filterwhite'+' '+j+'').read()
        white_result_list.append(res)

    #将列表写入到文件中
    f4 = open(file='./dicc.txt',mode='w')
    for aa in white_result_list:
        f4.write(str(aa))
    f4.close()

    #删除多余的空行
    os.popen('bash ./sub_link.sh filterwhiteline')
    




#程序执行入口
if __name__ == "__main__":

    if int(switch) == 1:
        print("程序执行白名单过滤扫描")
        linkwhite()
        time.sleep(2)
        print("扫描结束(带http协议：dicc_http.txt  不带http协议：dicc1.txt)")

    elif int(switch) == 0:
        print("程序执行黑名单过滤扫描")
        linkblack()
        os.popen('bash ./sub_link.sh filterbalck')
        time.sleep(2)
        print("扫描结束(带http协议：dicc_http.txt  不带http协议：dicc1.txt)")

    else:
        print("配置文件switch字段只允许0/1")