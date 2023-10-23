#!/usr/bin/env python3
"""
Pragram Name:[flask_cnvd]
Description:[信息收集系统]
Author:[huan666]
Date:[2021/08/01 12:08]
"""
#----------------------------------------------------------------------------------------#
from operator import imod
from flask import Flask
from flask import  render_template
from flask import request
from flask import session
from flask import redirect
from flask import send_from_directory
from flask import make_response
from flask import jsonify
import pymysql
import time
from flask_bootstrap import Bootstrap
import os
import requests
from bs4 import BeautifulSoup
import re
import base64
import json
import shodan
import logging
import subprocess
import pandas as pd
#指定版本1.2.0,最新版本不支持xlsx格式
import xlrd
import psutil
from elasticsearch import Elasticsearch
from config import fofakey
from config import dict
from config import shodankey
from config import linkconfig
from config import esusername
from config import espassword
from config import esurl
from config import dir_vul_url
#引用外部文件，用于判断前端传入的是IP还是域名
from lib import is_valid_ip
#arl资产探测平台登录方式和账号密码
from config import arlurl
from config import arluserpass
#github监控平台登录方式和账号密码
from config import githuburl
from config import githubpass
#引入自定义debug模块
from config import debugmode
#目录扫描文件白名单过滤
from config import dirscanwhite

app = Flask(__name__,template_folder='./templates')
app.secret_key = "DragonFire"
bootstrap = Bootstrap(app)

#----------------------------------------文件上传------------------------------------------------#
#规则文件上传路径(多个)
UPLOAD_FOLDER2 = 'rulescanupload'
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2  # 设置文件上传的目标文件夹


#样本文件上传路径(多个)
UPLOAD_FOLDER3 = 'samplescanupload'
app.config['UPLOAD_FOLDER3'] = UPLOAD_FOLDER3  # 设置文件上传的目标文件夹

#存活主机IP列表上传路径
UPLOAD_FOLDER4 = 'ipupload'
app.config['UPLOAD_FOLDER4'] = UPLOAD_FOLDER4  # 设置文件上传的目标文件夹

#目录扫描文件上传路径
UPLOAD_FOLDER5 = 'dirsearchfilepath'
app.config['UPLOAD_FOLDER5'] = UPLOAD_FOLDER5  # 设置文件上传的目标文件夹

#fscan端口扫描文件上传路径
UPLOAD_FOLDER6 = 'fscanfilepath'
app.config['UPLOAD_FOLDER6'] = UPLOAD_FOLDER6  # 设置文件上传的目标文件夹

basedir = "/TIP/flask_cnvd"
dirsearchdir = "/TIP/flask_cnvd/dirsearch"
fscandir = "/TIP/flask_cnvd/fscan"
#----------------------------------------文件上传------------------------------------------------#



#----------------------------------------全局配置------------------------------------------------#



#数据库未连接提示信息
datainfo = "数据库未开启,请联系管理员!!!"
#子域名扫描时返回的信息
data2 = "实时扫描待开发中......"
#修改和删除功能关闭返回给前端的信息
datadel = "删除功能已在后端关闭,开启请联系管理员!!!"
dataup = "修改功能已在后端关闭,开启请联系管理员!!!"

#所有模块用数据库查出来的用户名和session中的用户名判断是否相等
db= pymysql.connect(host=dict['ip'],user=dict['username'],  
password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
cur = db.cursor()
sql="select username,password from user_table"
cur.execute(sql)
data = cur.fetchall()
usernameconfig = data[0][0]
#----------------------------------------全局配置------------------------------------------------#




#----------------------------------------漏洞管理模块------------------------------------------------#

#按ID进行删除数据
@app.route("/deletebyid/",methods=['get'])
def deletebyid():
    app.logger.warning('通过ID删除漏洞')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        id = request.args['id']
        sql="delete from vuln_table where id = '%s' " %(id)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return render_template('index.html',data=data)
    except:
        return render_template('error.html',data=datadel)


#漏洞标题添加到数据库
@app.route('/adddata/',methods=['POST'])
def adddata():
    app.logger.warning('漏洞标题添加到数据库')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
        cur = db.cursor()
        vulnname=request.form['vulnname']
        ip=request.form['ip']

        #检查是否存在相同的数据
        sql_select = "select * from vuln_table where vulnname = '%s' "%(vulnname)
        cur.execute(sql_select)
        result = cur.fetchone()

        #定义全局变量将数据存库状态回显给前端
        global indexadddatastatus
        if result:
            indexadddatastatus =""+vulnname+"已存在请不要重复添加"
        else:
            sql_insert = "insert into vuln_table(vulnname,ip,datenow,showandhide) values('%s','%s','%s','%s')" %(vulnname,ip,now,1)
            cur.execute(sql_insert)
            db.commit()
            indexadddatastatus = ""+vulnname+"已经添加成功"
        
        return render_template('index.html')
    except:
        return render_template('error.html',data=datainfo)


#判断漏洞标题是否添加成功回显给前端
@app.route("/showvulntitleinterfaceajax/",methods=['GET'])
def showvulntitleinterfaceajax():
    app.logger.warning('判断漏洞标题是否添加成功回显给前端')
    user = session.get('username')
    if str(user) == usernameconfig:
        global indexadddatastatus
        message_json = {
        "indexadddatastatus":indexadddatastatus
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')



#漏洞网址添加到数据库
@app.route('/addvulnurlinterface/',methods=['POST'])
def addvulnurlinterface():
    app.logger.warning('漏洞网址添加到数据库')

    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum'])
        cur = db.cursor()
        vulnurl = request.form['vulnurl']
        url_value_re = re.search(r'https?://([^/:]+)', vulnurl)
        url_value_result = url_value_re.group(0)
        #检查是否存在相同数据
        sql_select = "select * from vuln_url_table where vulnurl = '%s' "%(url_value_result)
        cur.execute(sql_select)
        result = cur.fetchone()
        #查询vuln_url_table表中总共存在多少条数据
        sql1="select count(*) from vuln_url_table"
        cur.execute(sql1)
        tuple_data = cur.fetchall()
        #元组转换为字符串
        tuple_str_data = str(tuple_data[0][0])
        #定义全局变量给前端显示函数使用
        global vuln_url_message
        global vuln_url_message_show
        if result:
            url_value_result_11 = list(result)[1]

            #如果存在相同数据，返回当前查询到的一条数据回显给前端
            vuln_url_message = url_value_result_11+" "+"已成功入库，请不要重复进行入库操作！！！"+" "+"vuln_url_table表总条数："+tuple_str_data
            vuln_url_message_show = "扫描前黑名单"+url_value_result_11+"已存在请不要重复添加"
            return render_template('index.html')
        else:
            sql_insert = "insert into vuln_url_table(vulnurl) values('%s')"%(url_value_result)
            cur.execute(sql_insert)
            db.commit()
            vuln_url_message = "数据已经添加成功"
            vuln_url_message_show = "扫描前黑名单"+url_value_result_11+"已添加成功"
            return render_template('index.html')
        
    except:
        return render_template('error.html',data=datainfo)


#判断漏洞网址是否添加成功回显给前端
@app.route("/showvulnurlinterfaceajax/",methods=['GET'])
def showvulnurlinterfaceajax():
    app.logger.warning('判断漏洞网址是否添加成功回显给前端')
    user = session.get('username')
    if str(user) == usernameconfig:
        global vuln_url_message
        message_json = {
        "vuln_url_message":vuln_url_message
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')




#目录扫描前黑名单录入状态回显前端
@app.route("/showmuluscanstausbyajax/",methods=['GET'])
def showmuluscanstausbyajax():
    app.logger.warning('目录扫描前黑名单录入状态回显前端')
    user = session.get('username')
    if str(user) == usernameconfig:
        global vuln_url_message_show
        message_json = {
        "vuln_url_message_show":vuln_url_message_show
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')



#异步查询漏洞表数
@app.route("/selectvulnconutbyajax/",methods=['GET'])
def selectvulnconutbyajax():
    app.logger.warning('异步查询漏洞表数给前端展示')
    user = session.get('username')
    if str(user) == usernameconfig:
        global vulncount
        message_json = {
        "vulncount":vulncount
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')



# 通过漏洞名称和IP地址检索
@app.route("/selectbyname",methods=['POST'])
def selectbyname():
    app.logger.warning('通过IP和漏洞名称检索漏洞')
    try:
        oper = request.form['oper']
        vulnname=request.form['vulnname']
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        if oper == str(1):
            try:
                #按漏洞名称模糊查询数据           
                args = '%'+vulnname+'%'
                sql="select vulnname,ip,datenow,id from vuln_table where vulnname like '%s' and showandhide = 1 order by id desc"%args
                cur.execute(sql)
                data = cur.fetchall()
                #按名称查询数据条数
                sql1="select count(vulnname) from vuln_table where vulnname like '%s' and showandhide = 1 "%args
                cur.execute(sql1)
                data1 = cur.fetchall()
                #系统时间
                now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
                #查询IP地址用于异步查询漏洞名称
                sql111="SELECT  ip FROM vuln_table where ip is not null and showandhide = 1  order BY ip DESC "
                cur.execute(sql111)
                data5 = cur.fetchall()
                return render_template('index.html',data=data,data1=data1,data2=str(now),data3=str(vulnname),data5=data5)
            except:
                return render_template('error.html',data=datainfo)
        elif oper == str(2):
            try:
                #按IP精准查询数据并返回给前端
                sql="select vulnname,ip,datenow,id from vuln_table where ip = '%s' and showandhide = 1 order by id desc"%(vulnname)
                cur.execute(sql)
                data = cur.fetchall()
                #按名称查询数据条数
                sql1="select count(id) from vuln_table where ip = '%s' and showandhide = 1"%(vulnname)
                cur.execute(sql1)
                data1 = cur.fetchall()
                #系统时间
                now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
                #查询IP地址用于异步查询漏洞名称
                sql111="SELECT  ip FROM vuln_table where ip is not null and showandhide = 1  order BY ip DESC "
                cur.execute(sql111)
                data5 = cur.fetchall()
                return render_template('index.html',data=data,data1=data1,data2=str(now),data3=str(vulnname),data5=data5)
            except:
                return render_template('error.html',data=datainfo)
    except:
        return render_template('error.html',data=datainfo)


#根据ID查询数据
@app.route("/selectbyid/",methods=['get'])
def selectbyid():
    app.logger.warning('通过ID查询漏洞')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        id = request.args['id']
        sql="select vulnname,ip,datenow,id from vuln_table where id = '%s' and showandhide = 1"%(id)
        cur.execute(sql)
        data = cur.fetchall()
        list_data = list(data)
        global valnnamedata
        global ipdata
        global iddata
        for i in list_data:
            valnnamedata = i[0]
            ipdata = i[1]
            iddata = i[3]
        return render_template('index.html')
    except:
        return render_template('error.html',data=datainfo)


#通过IP反查漏洞名称
@app.route("/selectvulnnamebyip/",methods=['get'])
def selectvulnnamebyip():
    
    app.logger.warning('通过IP反查漏洞名称')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        ip = request.args['ip']
        sql="SELECT vulnname FROM vuln_table WHERE ip = '%s' and showandhide = 1"%(ip)
        cur.execute(sql)
        data = cur.fetchall()
        list_data = list(data)
        global vuln_name
        vuln_name = list_data
        return render_template('index.html')
    except:
        return render_template('error.html',data=datainfo)


#通过漏洞名称反查IP
@app.route("/selectipbyvulnname/",methods=['get'])
def selectipbyvulnname():
    
    app.logger.warning('通过漏洞名称反查IP')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        vulnname = request.args['vulnname']
        sql="SELECT ip FROM vuln_table WHERE ip = '%s' and showandhide = 1 "%(vulnname)
        cur.execute(sql)
        data = cur.fetchall()
        list_data = list(data)
        global ip_name
        ip_name = list_data
        return render_template('index.html')
    except:
        return render_template('error.html',data=datainfo)




#通过漏洞名称反查IP异步回显给前端在展示
@app.route("/selectipbyvulnnameajax/",methods=['GET'])
def selectipbyvulnnameajax():
    app.logger.warning('通过漏洞名称反查IP异步回显给前端在展示')
    user = session.get('username')
    if str(user) == usernameconfig:
        global ip_name
        message_json = {
        "ip_name":ip_name
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')




#通过关键字异步查询漏洞名称
@app.route("/selectvulnnamebykey/",methods=['POST'])
def selectvulnnamebykey():
    
    app.logger.warning('通过关键字异步查询漏洞名称')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        vulnnamekeyajax=request.form['vulnnamekeyajax']
        args = '%'+vulnnamekeyajax+'%'
        sql="select vulnname from vuln_table where vulnname like '%s' and showandhide = 1 order by id desc"%args
        cur.execute(sql)
        data = cur.fetchall()
        list_data = list(data)
        global vuln_name_key
        vuln_name_key = list_data
        #异步查询根据关键字查询出来的漏洞数量
        sql1 = "select count(vulnname) from vuln_table where vulnname like '%s' and showandhide = 1 "%args
        cur.execute(sql1)
        data5 = cur.fetchall()
        global vulncount
        vulncount = list(data5)
        return render_template('index.html')
    except:
        return render_template('error.html',data=datainfo)



#通过关键字异步查询IP地址
@app.route("/selectipbykey/",methods=['POST'])
def selectipbykey():
    
    app.logger.warning('通过关键字异步查询IP地址')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        vulnnamekeyajax=request.form['vulnnamekeyajax']
        args = '%'+vulnnamekeyajax+'%'
        sql="select ip from vuln_table where vulnname like '%s' and showandhide = 1 order by id desc"%args
        cur.execute(sql)
        data = cur.fetchall()
        list_data = list(data)
        global ip_name_key
        ip_name_key = list_data
        
        return render_template('index.html')
    except:
        return render_template('error.html',data=datainfo)


#通过关键字异步查询录入数据时间
@app.route("/selectdatenowbykey/",methods=['POST'])
def selectdatenowbykey():
    
    app.logger.warning('通过关键字异步查询录入数据时间')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        vulnnamekeyajax=request.form['vulnnamekeyajax']
        args = '%'+vulnnamekeyajax+'%'
        sql="select datenow from vuln_table where vulnname like '%s' and showandhide = 1 order by id desc"%args
        cur.execute(sql)
        data = cur.fetchall()
        list_data = list(data)
        global date_now_name_key
        date_now_name_key = list_data
        
        return render_template('index.html')
    except:
        return render_template('error.html',data=datainfo)



#通过IP查询漏洞名称异步回显给前端在展示
@app.route("/selectvulnnamebyipajax/",methods=['GET'])
def selectvulnnamebyipajax():
    app.logger.warning('通过IP查询漏洞名称异步回显给前端在展示')
    user = session.get('username')
    if str(user) == usernameconfig:
        global vuln_name
        message_json = {
        "vuln_name":vuln_name
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')


#通过关键字异步查询漏洞名给前端展示
@app.route("/selectvulnnamebykeyajax/",methods=['GET'])
def selectvulnnamebykeyajax():
    app.logger.warning('通过关键字异步查询漏洞名给前端展示')
    user = session.get('username')
    if str(user) == usernameconfig:
        global vuln_name_key
        global ip_name_key
        message_json = {
        "vuln_name_key":vuln_name_key,
        "ip_name_key":ip_name_key,
        "date_now_name_key":date_now_name_key
        }
        return jsonify(message_json)  
    else:
        return render_template('login.html')



#修改功能根据ID查询数据异步回显给前端在展示
@app.route("/selectbyidajax/",methods=['GET'])
def selectbyidajax():
    app.logger.warning('修改功能根据ID查询数据异步回显给前端在展示')
    user = session.get('username')
    if str(user) == usernameconfig:
        global valnnamedata
        global ipdata
        global iddata
        message_json = {
        "valnname11":valnnamedata,
        "ip11":ipdata,
        "id11":iddata
        }
        return jsonify(message_json)
    
    else:
        return render_template('login.html')



#根据ID修改数据
@app.route("/updatebyid/",methods=['post'])
def updatebyid():
    app.logger.warning('通过ID修改漏洞')
    vulnnames=request.form['vulnnames']
    ips=request.form['ips']
    #利用input框的隐藏属性,从前端传入id值
    ids=request.form['ids']
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
        cur = db.cursor()
        sql = "UPDATE vuln_table set vulnname = '%s' , ip = '%s', datenow = '%s'  where id = '%s' "%(vulnnames,ips,now,ids)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return render_template('index.html')
    except:
        pass



#查询所有漏洞表
@app.route("/index/")
def index():
    app.logger.warning('查询所有漏洞')
    user = session.get('username')
    if str(user) == usernameconfig:
        try:
            #查询所有数据
            db= pymysql.connect(host=dict['ip'],user=dict['username'],  
            password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
            cur = db.cursor()
            sql="select vulnname,ip,datenow,id from vuln_table where showandhide = 1 order by id desc limit 0,5"
            cur.execute(sql)
            data = cur.fetchall()

            #漏洞名称写入到文件中
            sql1 = "select vulnname from vuln_table where showandhide = 1 order by id desc"
            cur.execute(sql1)
            data1 = cur.fetchall()
            f = open(file='/TIP/flask_cnvd/file_txt/漏洞名称.txt', mode='w')
            for ii in list(data1):
                for jj in ii:
                    f.write(str(jj)+"\n")

            #IP地址写入到文件中
            sql2 = "select ip from vuln_table where showandhide = 1 order by id desc"
            cur.execute(sql2)
            data2 = cur.fetchall()
            g = open(file='/TIP/flask_cnvd/file_txt/IP地址.txt', mode='w')
            for aa in list(data2):
                for bb in aa:
                    g.write(str(bb)+"\n")

            #删除None所在的行
            os.popen('sed \'/None/d\' /TIP/flask_cnvd/file_txt/IP地址.txt > /TIP/flask_cnvd/file_txt/IP地址名称.txt')
              
            #ES服务运行状态
            es_status = os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh elasticsearch').read()

            #漏洞标题列表显示状态判断
            sql3 = "select count(id) from vuln_table where showandhide = 1"
            cur.execute(sql3)
            data3 = cur.fetchall()
            num_1_1 = data3[0][0]
            if num_1_1 > 1000:
                indexstatus = "访问权限已开启,可正常查询数据,列表只显示最新5条,查询更多利用异步查询。"
            else:
                indexstatus = "访问权限未开启,不可查询数据。"

            return render_template('index.html',data=data,data4=es_status,data5=indexstatus)
        
        except:
            return render_template('error.html',data=datainfo)
    else:
        return render_template('login.html')



#按时间段查询漏洞标题
@app.route("/selectallbycycle/",methods=['post'])
def selectallbycycle():
    
    app.logger.warning('按时间段查询漏洞标题')
    oper = request.form['oper']
    db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
    cur = db.cursor()
    global vuln_time_list_result
    global date_time_list_result
    global vuln_count_list_result
    try:
        #当天数据
        if oper == str(1):
            #查询当天数据
            sql="select vulnname,ip,datenow,id from vuln_table where to_days(datenow) = to_days(now()) and showandhide = 1 order by id desc"
            cur.execute(sql)
            data = cur.fetchall()
            sql1="select count(vulnname) from vuln_table where to_days(datenow) = to_days(now()) and showandhide = 1 order by id desc"
            cur.execute(sql1)
            data1 = cur.fetchall()
            list_count = []
            for k in data1:
                list_count.append(k[0])
            vuln_count_list_result = str(list_count[0])
           
            list_data = list(data)
            vulnname_time_list = []
            date_time_list = []
            for i in list_data:
                vulnname_time_list.append(i[0])
            for j in list_data:
                date_time_list.append(j[2])
            vuln_time_list_result = vulnname_time_list
            date_time_list_result = date_time_list
            return render_template('index.html',data=data)
        #近7天
        elif oper == str(2):
            #查询近7天
            sql="select vulnname,ip,datenow,id from vuln_table where DATE_SUB(CURDATE(), INTERVAL 7 DAY) <= date(datenow) and showandhide = 1 order by id desc"
            cur.execute(sql)
            data = cur.fetchall()

            sql1="select count(vulnname) from vuln_table where DATE_SUB(CURDATE(), INTERVAL 7 DAY) <= date(datenow) and showandhide = 1 order by id desc"
            cur.execute(sql1)
            data1 = cur.fetchall()
            list_count = []
            for k in data1:
                list_count.append(k[0])
            vuln_count_list_result = str(list_count[0])

            list_data = list(data)
            vulnname_time_list = []
            date_time_list = []
            for i in list_data:
                vulnname_time_list.append(i[0])
            for j in list_data:
                date_time_list.append(j[2])
            vuln_time_list_result = vulnname_time_list
            date_time_list_result = date_time_list
            return render_template('index.html',data=data)
        #近30天
        elif oper == str(3):
            #查询近30天
            sql="select vulnname,ip,datenow,id from vuln_table where DATE_SUB(CURDATE(), INTERVAL 30 DAY) <= date(datenow) and showandhide = 1 order by id desc"
            cur.execute(sql)
            data = cur.fetchall()

            sql1="select count(vulnname) from vuln_table where DATE_SUB(CURDATE(), INTERVAL 30 DAY) <= date(datenow) and showandhide = 1 order by id desc"
            cur.execute(sql1)
            data1 = cur.fetchall()
            list_count = []
            for k in data1:
                list_count.append(k[0])
            vuln_count_list_result = str(list_count[0])

            list_data = list(data)
            vulnname_time_list = []
            date_time_list = []
            for i in list_data:
                vulnname_time_list.append(i[0])
            for j in list_data:
                date_time_list.append(j[2])
            vuln_time_list_result = vulnname_time_list
            date_time_list_result = date_time_list
            return render_template('index.html',data=data)
        #全年
        elif oper == str(4):
            #查询全年数据
            sql="select vulnname,ip,datenow,id from vuln_table where showandhide = 1 order by id desc"
            cur.execute(sql)
            data = cur.fetchall()
            sql1="select count(vulnname) from vuln_table where showandhide = 1 order by id desc"
            cur.execute(sql1)
            data1 = cur.fetchall()
            list_count = []
            for k in data1:
                list_count.append(k[0])
            vuln_count_list_result = str(list_count[0])

            list_data = list(data)
            vulnname_time_list = []
            date_time_list = []
            for i in list_data:
                vulnname_time_list.append(i[0])
            for j in list_data:
                date_time_list.append(j[2])
            vuln_time_list_result = vulnname_time_list
            date_time_list_result = date_time_list
            return render_template('index.html',data=data)
    except:
        return render_template('error.html',data=datainfo)


#根据时间段查询漏洞标题和时间异步展示给前端
@app.route("/selectvulntimebyajax/",methods=['GET'])
def selectvulntimebyajax():
    app.logger.warning('根据时间段查询漏洞标题和时间异步展示给前端')
    user = session.get('username')
    if str(user) == usernameconfig:
        global vuln_time_list_result
        global date_time_list_result
        message_json = {
        "vuln_time_list_result":vuln_time_list_result,
        "date_time_list_result":date_time_list_result,
        "vuln_count_list_result":vuln_count_list_result
        }
        return jsonify(message_json)
    
    else:
        return render_template('login.html')


#mysql数据库数据下载
@app.route("/mysqldownload/")
def mysqldownload():
    app.logger.warning('漏洞名称下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/file_txt/漏洞名称.txt',directory ='/TIP/flask_cnvd/file_txt',filename="漏洞名称.txt",as_attachment=True)
    else:
        return render_template('login.html')

@app.route("/ipdownload/")
def ipdownload():
    app.logger.warning('IP地址下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/file_txt/IP地址名称.txt',directory ='/TIP/flask_cnvd/file_txt',filename="IP地址名称.txt",as_attachment=True)
    else:
        return render_template('login.html')



#根据漏洞标题删除数据
@app.route("/deletevulnnamebyvulnname/",methods=['get'])
def deletevulnnamebyvulnname():
    app.logger.warning('根据漏洞标题删除数据')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        name = request.args['name']
        sql="DELETE from vuln_table WHERE vulnname = '%s' " %(name)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return render_template('index.html')
    except:
        return render_template('error.html')
#----------------------------------------漏洞管理模块------------------------------------------------#









#----------------------------------------系统更新说明模块------------------------------------------------#
#系统更新内容前端展示


@app.route("/showsystemupdate/",methods=['GET'])
def showsystemupdate():
    app.logger.warning('系统更新内容前端展示')
    #更新内容直接填入列表中，重启服务即可前端展示。
    data_list = ["1.增加JavaScript获取时间功能","2.修复已知bug","3.前端界面优化",
    "4.修改功能前端和后端优化","5.新增异步识别用户是否存在功能","6.新增条件搜索框显示和隐藏功能",
    "7.扫描器参数和配置修改","8.新增ajax,异步加载数据","9.新增黑名单功能,可全局过滤扫描结果",
    "10.新增关键字和IP异步查询数据并前端显示","11.漏洞管理模块前端界面优化","12.目录扫描模块新增白名单过滤配置",
    "13.新增通过时间段查询漏洞标题AJAX","14.Jquery在线库变更为本地库","15.目录扫描模块新增原始数据和处理后数据查看",
    "16.前端页面更改为相对路径","17.优化子域名扫描前端结果显示,子域名和IP地址分开进行显示","18.新增配置信息集中管理",
    "19.新增通过SSH隧道访问","20.新增子域名爆破模块子域名列表和IP列表文件下载功能"
    ]
    message_json = {
    "version":"版本信息: v1.6.1",
    "time":"更新时间: 2022/08/28",
    "event":"更新内容:",
     "language":"后端语言: Python3+Flask",
     "database":"数据库: MySQL+Elasticsearch",
     "language1":"前端语言: Jquery+Ajax+HTML+CSS",
    "eventName":data_list,
    "packup":"收起"
    }
    return jsonify(message_json)
    
#----------------------------------------系统更新说明模块------------------------------------------------#





#----------------------------------------系统信息查询说明模块------------------------------------------------#
#前端显示CPU利用率
@app.route("/cpushowinterface/")
def cpushowinterface():
    app.logger.warning('前端显示CPU利用率')
    user = session.get('username')

    if str(user) == usernameconfig:
        cpu_percent = psutil.cpu_percent(interval=1)
        message_json = {
        "cpurate":"cpu利用率: "+str(cpu_percent)
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')

#----------------------------------------系统信息查询说明模块------------------------------------------------#





#----------------------------------------用户管理模块------------------------------------------------#
#手动清除session功能
@app.route('/clearsession/',methods=['get'])
def clearsession():
    
    app.logger.warning('手动清除session功能')
    session.clear()
    return render_template('login.html',data1="已成功退出当前用户!")



#用户列表
@app.route("/userlist/")
def userlist():
    app.logger.warning('查询所有用户')
    user = session.get('username')
    if str(user) == usernameconfig:
        try:
            db= pymysql.connect(host=dict['ip'],user=dict['username'],  
            password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
            cur = db.cursor()
            sql="select username,password,id from user_table order by id desc"
            cur.execute(sql)
            data = cur.fetchall()
        except:
            return render_template('error.html',data=datainfo)
        return render_template('usermanage.html',data=data)
    else:
        return render_template('login.html')


#判断用户是否存在
@app.route("/judgeisuser/",methods=['POST'])
def judgeisuser():
    try:
        app.logger.warning('判断用户是否存在')
        username=request.form['username']
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql="select username from user_table where username = '%s' "%(username)
        cur.execute(sql)
        data = cur.fetchall()
        #全局变量所有方法均可调用
        global userresult
        userresult = ""
        #判断前端传递过来的用户是否为空
        if len(username) == 0:
            userresult = "账号为空，请输入账号！"
        else:
            if len(data) >0:
                userresult = "账号"+username+"存在！"
            else:
                userresult = "账号"+username+"不存在！"
        return render_template('login.html')
    except:
        pass



#将判断用户是否存在发送给前端利用ajax
@app.route("/judgeuserinist/",methods=['GET'])
def judgeuserinist():
    app.logger.warning('显示用户是否存在')
    global userresult
    message_json = {
        "message":userresult
    }
    return jsonify(message_json)



#用户注册
@app.route('/registered/',methods=['POST'])
def registered():
    
    app.logger.warning('用户注册')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
        cur = db.cursor()
        username=request.form['username']
        password=request.form['password']
        sql_insert = "insert into user_table(username,password) values('%s','%s')" %(username,password)
        cur.execute(sql_insert)  
        sql="select username,password,id from user_table order by id desc"
        cur.execute(sql)
        data = cur.fetchall()
        db.commit()
        db.rollback()
        data7_tmp = username+"已注册成功"
        return render_template('login.html',data=data,data7=data7_tmp)
    except:
        return render_template('error.html',data=datainfo)



#按ID删除用户
@app.route("/deleteuserbyid/",methods=['get'])
def deleteuserbyid():
    app.logger.warning('通过ID删除用户')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        id = request.args['id']
        sql="delete from user_table where id = '%s' " %(id)
        cur.execute(sql)
        sql="select username,password,id from user_table order by id desc"
        cur.execute(sql)
        data = cur.fetchall()
        db.commit()
        db.rollback()
        return render_template('usermanage.html',data=data)
    except:
        return render_template('error.html',data=datadel)



#根据ID查询用户
@app.route("/selectuserbyid/",methods=['get'])
def selectuserbyid():
    app.logger.warning('通过ID查询用户')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        id = request.args['id']
        sql="select username,password,id from user_table where id = '%s' "%(id)
        cur.execute(sql)
        data = cur.fetchall()
        list_data = list(data)
        global username_data_1
        global password_data_1
        global id_data_1
        for i in list_data:
            username_data_1 = i[0]
            password_data_1 = i[1]
            id_data_1 = i[2]
        return render_template('updateuser.html')
    except:
        return render_template('error.html',data=datainfo)


#修改功能根据ID查询用户数据异步回显给前端在展示
@app.route("/selectuserbyidajax/",methods=['GET'])
def selectuserbyidajax():
    app.logger.warning('修改功能根据ID查询数据异步回显给前端在展示')
    user = session.get('username')
    if str(user) == usernameconfig:
        global username_data_1
        global password_data_1
        global id_data_1
        message_json = {
        "username_data_1":username_data_1,
        "password_data_1":password_data_1,
        "id_data_1":id_data_1
       
        }
        return jsonify(message_json)
    
    else:
        return render_template('login.html')



#根据ID修改用户数据
@app.route("/updateuserbyid/",methods=['post'])
def updateuserbyid():
    app.logger.warning('通过ID修改用户')
    username=request.form['username1']
    password=request.form['password1']
    #利用input框的隐藏属性,从前端传入id值。
    id=request.form['id1']
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql = "UPDATE user_table set username = '%s' , password = '%s' where id = '%s' "%(username,password,id)
        cur.execute(sql)
        db.commit()
        db.rollback()
        #return redirect("/userlist/")
        return render_template('usermanage.html')
    except:
        return render_template('error.html',data=dataup)


#跳转到登录页面
@app.route("/loginpage/")
def loginpage():
    
    app.logger.warning('跳转到登录页面')   
    return render_template('login.html')

#登录功能实现
@app.route('/login/',methods=['post'])
def login():
    
    app.logger.warning('登录功能实现')
    username = request.form['username']
    password = request.form['password']
    db= pymysql.connect(host=dict['ip'],user=dict['username'],  
    password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
    cur = db.cursor()
    sql="select username,password from user_table"
    cur.execute(sql)
    data = cur.fetchall()
    sql = "UPDATE count_table SET num_count = num_count + 1 where id = 1"
    cur.execute(sql)
    db.commit()
    db.rollback()

    if str(username) == data[0][0] and str(password) == data[0][1]:
        session['username'] = username
        return redirect("/index/")
    else:
        return render_template('login.html',data1="账号或密码输入有误,请重新输入!",data2=username,data3=password)
#----------------------------------------用户管理模块------------------------------------------------#



    
   



#----------------------------------------系统基础配置模块------------------------------------------------#
#跳转到系统状态
@app.route("/systemstatus/")
def systemstatus():
    
    app.logger.warning('系统应用服务状态')
    user = session.get('username')
    if str(user) == usernameconfig:

        #python-flask
        flask_status = os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh pythons').read()

        #mysql
        mysql_status = os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh mysql').read()

        #elasticsearch
        es_status = os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh elasticsearch').read()

        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql = "SELECT COUNT(id) FROM vuln_table WHERE showandhide = 1"
        cur.execute(sql)
        data = cur.fetchall()
        num_id = data[0][0]

        #判断漏洞标题页面数据状态
        if num_id > 2000:
            indexstatus = "已开启"
        else:
            indexstatus = "已关闭"
        
        return render_template('status.html',data1=flask_status,data2=mysql_status,data3=es_status,data4=indexstatus)
    else:
        return render_template('login.html')



#flask状态异步展示给前端
@app.route("/flasksystemstatusinist/",methods=['GET'])
def flasksystemstatusinist():
    app.logger.warning('flask状态异步展示给前端')
    global flask_status_1
    message_json = {
        "flask_status_1":flask_status_1
    }
    return jsonify(message_json)

#mysql状态异步展示给前端
@app.route("/mysqlsystemstatusinist/",methods=['GET'])
def mysqlsystemstatusinist():
    app.logger.warning('mysql状态异步展示给前端')
    global mysql_status_1
    message_json = {
        "mysql_status_1":mysql_status_1
    }
    return jsonify(message_json)

#es状态异步展示给前端
@app.route("/essystemstatusinist/",methods=['GET'])
def essystemstatusinist():
    app.logger.warning('es状态异步展示给前端')
    global es_status_1
    message_json = {
        "es_status_1":es_status_1
    }
    return jsonify(message_json)


#漏洞标题状态异步展示给前端
@app.route("/indexsystemstatusinist/",methods=['GET'])
def indexsystemstatusinist():
    app.logger.warning('漏洞标题状态异步展示给前端')
    global indexstatus_1
    message_json = {
        "indexstatus_1":indexstatus_1
    }
    return jsonify(message_json)




#系统应用层服务启动和关闭
@app.route("/operservice/",methods=['post'])
def operservice():
    app.logger.warning('系统应用层服务启动和关闭')
    user = session.get('username')
    oper = request.form['oper']
    global es_status_1
    global mysql_status_1
    global flask_status_1
    if str(user) == usernameconfig:
        try:
            if oper == "stopesservice":
                os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh stop_es')
                #elasticsearch
                es_status = os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh elasticsearch').read()
                es_status_1 = es_status
                return render_template('status.html')

            elif oper == "restartesservice":
                os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh restart_es')
                #elasticsearch
                es_status = os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh elasticsearch').read()
                es_status_1 = es_status
                return render_template('status.html')

            elif oper == "restartmysqlservice":
                os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh restart_mysql')
                #mysql
                mysql_status = os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh mysql').read()
                mysql_status_1 = mysql_status
                return render_template('status.html')

            elif oper == "stopmysqlservice":   
                os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh stop_mysql')
                #mysql
                mysql_status = os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh mysql').read()
                mysql_status_1 = mysql_status
                return render_template('status.html')

            elif oper == "stopflaskservice":
                os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh stop_flask')
                #python-flask
                flask_status = os.popen('bash /TIP/flask_cnvd/shellscript/servicestatus.sh pythons').read()
                flask_status_1 = flask_status
                return render_template('status.html')
            else:
                return render_template('dictionary.html')
        except:
            pass
    else:
        return render_template('login.html')




#ES服务状态异步动态显示给前端
@app.route("/estatusbyajax/",methods=['GET'])
def estatusbyajax():
    app.logger.warning('ES服务状态异步动态显示给前端')
    user = session.get('username')
    if str(user) == usernameconfig:
        global esservice
        message_json = {
        "esservice":esservice
       
        }
        return jsonify(message_json)
    
    else:
        return render_template('login.html')



#访问记录
@app.route("/accessrecord/")
def accessrecord():
    app.logger.warning('访问记录')
    user = session.get('username')
    if str(user) == usernameconfig:
        try:
            db= pymysql.connect(host=dict['ip'],user=dict['username'],  
            password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
            cur = db.cursor()
            sql="select ip,locate,nowdate,user,id from ip_table order by id desc"
            cur.execute(sql)
            data = cur.fetchall()
        except:
            pass
        return render_template('accessrecords.html',data=data)
    else:
        return render_template('login.html')


#按ID删除访问记录
@app.route("/deleteaccessbyid/",methods=['get'])
def deleteaccessbyid():
    app.logger.warning('通过ID删除访问记录')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        id = request.args['id']
        sql="delete from ip_table where id = '%s' " %(id)
        cur.execute(sql)
        sql1="select ip,locate,nowdate,user,id from ip_table order by id desc"
        cur.execute(sql1)
        data = cur.fetchall()
        db.commit()
        db.rollback()
        return render_template('accessrecords.html',data=data)
    except:
        pass


#清空记录
@app.route("/deleteaccessall/")
def deleteaccessall():
    app.logger.warning('清空记录')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql="delete from ip_table"
        cur.execute(sql)
        sql1="select ip,locate,nowdate,user,id from ip_table order by id desc"
        cur.execute(sql1)
        data = cur.fetchall()
        db.commit()
        db.rollback()
        return render_template('accessrecords.html',data=data)
    except:
        pass



#跳转到日志管理模块
@app.route("/managelog/")
def managelog():
    app.logger.warning('跳转到日志管理模块')
    user = session.get('username')
    if str(user) == usernameconfig:
        logsize_tmp0 = os.popen('du -sh /TIP/flask_cnvd/log/info.log').read()
        logsize0 = logsize_tmp0.replace("/TIP/flask_cnvd/log/info.log","")

        logsize_tmp1 = os.popen('du -sh /var/log/mysql/mysql.log').read()
        logsize1 = logsize_tmp1.replace("/var/log/mysql/mysql.log","")

        
        logsize_tmp2 = os.popen('du -sh /var/log/auth.log').read()
        logsize2 = logsize_tmp2.replace("/var/log/auth.log","")
        return render_template('managelog.html',data6=logsize0,data7=logsize1,data8=logsize2)
    else:
        return render_template('login.html')


#日志管理模块功能
@app.route("/managelogfunc/",methods=['post'])
def managelogfunc():
    
    app.logger.warning('日志管理模块功能实现')
    oper = request.form['oper']
    name = request.form['name']
    
    try:
        if oper == str(1):
            rule_list = []
            rule_file = open("/TIP/flask_cnvd/log/info.log",encoding='utf-8')

            logsize_tmp0 = os.popen('du -sh /TIP/flask_cnvd/log/info.log').read()
            logsize0 = logsize_tmp0.replace("/TIP/flask_cnvd/log/info.log","")

            logsize_tmp1 = os.popen('du -sh /var/log/mysql/mysql.log').read()
            logsize1 = logsize_tmp1.replace("/var/log/mysql/mysql.log","")

            
            logsize_tmp2 = os.popen('du -sh /var/log/auth.log').read()
            logsize2 = logsize_tmp2.replace("/var/log/auth.log","")
            for line in rule_file.readlines():
                rule_list.append(line)
            return render_template('managelog.html',data=rule_list,data6=logsize0,data7=logsize1,data8=logsize2)
        elif oper == str(2):
            rule_list = []
            rule_file = open("/var/log/mysql/mysql.log",encoding='utf-8')
            logsize_tmp0 = os.popen('du -sh /TIP/flask_cnvd/log/info.log').read()
            logsize0 = logsize_tmp0.replace("/TIP/flask_cnvd/log/info.log","")

            logsize_tmp1 = os.popen('du -sh /var/log/mysql/mysql.log').read()
            logsize1 = logsize_tmp1.replace("/var/log/mysql/mysql.log","")

            
            logsize_tmp2 = os.popen('du -sh /var/log/auth.log').read()
            logsize2 = logsize_tmp2.replace("/var/log/auth.log","")

            for line in rule_file.readlines():
                rule_list.append(line)
            return render_template('managelog.html',data=rule_list,data6=logsize0,data7=logsize1,data8=logsize2)
        elif oper == str(3):
            rule_list = []
            os.popen('bash /TIP/flask_cnvd/shellscript/filterlog.sh'+' '+name)

            rule_file = open("/TIP/flask_cnvd/log/tmp_auth.log",encoding='utf-8')
            logsize_tmp0 = os.popen('du -sh /TIP/flask_cnvd/log/info.log').read()
            logsize0 = logsize_tmp0.replace("/TIP/flask_cnvd/log/info.log","")

            logsize_tmp1 = os.popen('du -sh /var/log/mysql/mysql.log').read()
            logsize1 = logsize_tmp1.replace("/var/log/mysql/mysql.log","")

            
            logsize_tmp2 = os.popen('du -sh /var/log/auth.log').read()
            logsize2 = logsize_tmp2.replace("/var/log/auth.log","")

            for line in rule_file.readlines():
                rule_list.append(line)
            return render_template('managelog.html',data=rule_list,data6=logsize0,data7=logsize1,data8=logsize2,data789=name)

    except:
        pass


#清空数据库日志
@app.route("/clearmysqllog/",methods=['post'])
def clearmysqllog():
    
    app.logger.warning('清空数据库日志')
    os.popen('rm -rf /var/log/mysql/mysql.log').read()
    os.popen('service mysql restart').read()
    return render_template('managelog.html')

#清空WEb日志
@app.route("/clearweblog/",methods=['post'])
def clearweblog():
    
    app.logger.warning('清空Web访问日志')
    os.popen('rm -rf /TIP/flask_cnvd/log/info.log')
    os.popen('touch /TIP/flask_cnvd/log/info.log')
    return render_template('managelog.html')




#清空系统日志
@app.route("/clearsystemlog/",methods=['post'])
def clearsystemlog():
    
    app.logger.warning('清空系统日志')
    os.popen('rm -rf /var/log/auth.log')
    os.popen('reboot')
    return render_template('managelog.html')




#显示漏洞标题页面数据
@app.route("/showindexpagedata/")
def showindexpagedata():
    app.logger.warning('显示漏洞标题页面数据')
    user = session.get('username')
    if str(user) == usernameconfig:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql = "UPDATE vuln_table set showandhide = 1"
        cur.execute(sql)
        db.commit()
        db.rollback()

        sql1 = "SELECT COUNT(id) FROM vuln_table WHERE showandhide = 1"
        cur.execute(sql1)
        data = cur.fetchall()
        num_id = data[0][0]

        #判断漏洞标题页面数据状态
        if num_id > 2000:
            indexstatus = "已开启"
        else:
            indexstatus = "已关闭"

        #设置全局变量
        global indexstatus_1
        indexstatus_1 = indexstatus
        return render_template('status.html')
    else:
        return render_template('login.html')



#隐藏漏洞标题页面数据
@app.route("/hideindexpagedata/")
def hideindexpagedata():
    app.logger.warning('隐藏漏洞标题页面数据')
    user = session.get('username')
    if str(user) == usernameconfig:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql = "UPDATE vuln_table set showandhide = 0"
        cur.execute(sql)
        db.commit()
        db.rollback()

        sql1 = "SELECT COUNT(id) FROM vuln_table WHERE showandhide = 1"
        cur.execute(sql1)
        data = cur.fetchall()
        num_id = data[0][0]

        #判断漏洞标题页面数据状态
        if num_id > 2000:
            indexstatus = "已开启"
        else:
            indexstatus = "已关闭"

        #设置全局变量
        global indexstatus_1
        indexstatus_1 = indexstatus
        return render_template('status.html')
    else:
        return render_template('login.html')
#----------------------------------------系统基础配置模块------------------------------------------------#




#----------------------------------------fscan扫描模块------------------------------------------------#
#跳转到fscan扫描器界面
@app.route("/fscanner/")
def fscanner():
    app.logger.warning('跳转到fscan扫描器界面')
    user = session.get('username')
    if str(user) == usernameconfig:
        os.popen('bash /TIP/flask_cnvd/shellscript/scannerstatus.sh fscanstatus > /TIP/flask_cnvd/file_txt/fscanstatus.txt')
        fscan_status_file = open('/TIP/flask_cnvd/file_txt/fscanstatus.txt',encoding='utf-8')
        fscan_status_list = []
        for linen in fscan_status_file.readlines():
            fscan_status_list.append(linen)
        try:
            fscanall_file = open("/TIP/flask_cnvd/file_txt/fscan.txt",encoding='utf-8')
            fscanall_file_list1=[]
            for line in fscanall_file.readlines():
                fscanall_file_list1.append(line)
        except:
            pass 
        num = os.popen('bash /TIP/flask_cnvd/shellscript/fscanscan.sh fscannum').read()
        num_1 = "文件行数: "+ num
        return render_template('scanner.html',data3=fscan_status_list,data=fscanall_file_list1,data4=num_1)
    else:
        return render_template('login.html')


#fscan提交扫描任务
@app.route("/fscan/",methods=['post'])
def fscan():
    app.logger.warning('fscan提交扫描任务')
    operport = request.form['operport']
    try:
        os.popen('bash /TIP/flask_cnvd/shellscript/fscanscan.sh fscanstart'+''+' '+operport+'')
        return render_template('scanner.html')
    except:
        return render_template('error.html')


#fscan黑名单录入并写入到文件中
@app.route("/filterfscan/",methods=['post'])
def filterfscan():
    
    app.logger.warning('fscan黑名单录入并写入到文件中')
    user = session.get('username')
    keyvalue = request.form['keyvalue']

    if str(user) == usernameconfig:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql_insert = "insert into fscan_blacklist_table(name)  values('%s')" %(keyvalue)
        cur.execute(sql_insert)  
        db.commit()
        db.rollback()
        #生成文件用于过滤扫描结果
        sql1 = "select name from fscan_blacklist_table order by id desc"
        cur.execute(sql1)
        data1 = cur.fetchall()
        f = open(file='/TIP/flask_cnvd/file_txt/filterfscan.txt', mode='w')
        for ii in list(data1):
            for jj in ii:
                f.write(str(jj)+"\n")
        return render_template('scanner.html')
    else:
        return render_template('login.html')



#清空fscan扫描结果
@app.route("/clearfscanresult/",methods=['post'])
def clearfscanresult():
    app.logger.warning('清空fscan扫描结果')
    try:
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/fscan.txt')
        os.popen('rm -rf /TIP/flask_cnvd/fscanfilepath/*')
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/fscantarget.txt')
        os.popen('touch /TIP/flask_cnvd/file_txt/fscan.txt')
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/fscan_1.txt')
        return render_template('scanner.html')
    except:
        return render_template('error.html')


#fscan扫描结果下载
@app.route("/fscanfiledownload/")
def fscanfiledownload():
    app.logger.warning('fscan扫描结果下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/file_txt/fscan.txt',directory ='/TIP/flask_cnvd/file_txt',filename="fscan.txt",as_attachment=True)
    else:
        return render_template('login.html')



#fscan扫描目标添加
@app.route("/addfscantargettxt/",methods=['post'])
def addfscantargettxt():
    app.logger.warning('fscan扫描目标添加')
    try:
        os.popen('mv /TIP/flask_cnvd/fscanfilepath/* /TIP/flask_cnvd/file_txt/fscantarget.txt')
        return render_template('scanner.html')
    except:
        return render_template('error.html')

#fscan扫描结果复制
@app.route("/copyfscanresult/",methods=['get'])
def copyfscanresult():
    app.logger.warning('fscan扫描结果复制')
    try:
        os.popen('cp /TIP/flask_cnvd/file_txt/fscan_1.txt /TIP/flask_cnvd/file_txt/fscan.txt')
        return render_template('scanner.html')
    except:
        return render_template('error.html')


#后台结束fscan进程
@app.route("/killfscan/",methods=['post'])
def killfscan():
    app.logger.warning('后台结束fscan扫描器进程')
    try:
        os.popen('bash /TIP/flask_cnvd/shellscript/killscan.sh killfscan').read()
        os.popen('bash /TIP/flask_cnvd/shellscript/scannerstatus.sh fscanstatus > /TIP/flask_cnvd/file_txt/fscanstatus.txt')
        fscan_status_file = open('/TIP/flask_cnvd/file_txt/fscanstatus.txt',encoding='utf-8')
        fscan_status_list = []
        for linen in fscan_status_file.readlines():
            fscan_status_list.append(linen)
        return render_template('scanner.html',datak="fscan进程已结束",data3=fscan_status_list)
    except:
        pass


#过滤fscan扫描器的扫描结果
@app.route("/filterscanresult/",methods=['post'])
def filterscanresult():
    app.logger.warning('过滤fscan扫描器扫描结果')
    fscanname = request.form['fscanname']
    try:

        os.popen('bash /TIP/flask_cnvd/shellscript/filterfscandata.sh'+' '+fscanname)
        resule_list_filter = []
        result_file_filter = open('/TIP/flask_cnvd/file_txt/filterfscan.txt',encoding='utf-8')
        for filterline in result_file_filter.readlines():
            resule_list_filter.append(filterline)

        fscan_status_file = open('/TIP/flask_cnvd/file_txt/fscanstatus.txt',encoding='utf-8')
        fscan_status_list = []
        for linen in fscan_status_file.readlines():
            fscan_status_list.append(linen)
        return render_template('scanner.html',data=resule_list_filter,dataa=fscanname,data3=fscan_status_list)
    except:
        pass


#fscan批量端口扫描文件上传
@app.route("/fscanfileupload/",methods=['post'])
def fscanfileupload():
    user = session.get('username')
    result = "上传成功"
    if str(user) == usernameconfig:
        app.logger.warning('fscan批量端口扫描文件上传')
        try:
            file_dir = os.path.join(fscandir, app.config['UPLOAD_FOLDER6'])
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)  
            f = request.files['file']  
            fname = f.filename
            f.save(os.path.join(file_dir, fname))
        except:
            pass
        return render_template('scanner.html',datainfo = result)
    else:
        return render_template('login.html')



#fscan端口扫描黑名单查看
@app.route("/Queryingfscanblacklist/",methods=['GET'])
def Queryingfscanblacklist():
    
    app.logger.warning('fscan端口扫描黑名单查看')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql="select name from fscan_blacklist_table order by id desc"
        cur.execute(sql)
        data1 = cur.fetchall()
        list_data1 = list(data1)
        global query_black_fscan_list
        query_black_fscan_list = list_data1
        return render_template('scanner.html')
    except:
        return render_template('error.html')


#fscan端口扫描黑名单前端展示
@app.route("/QueryingBlackfscanlistbyajax/",methods=['GET'])
def QueryingBlackfscanlistbyajax():
    app.logger.warning('fscan端口扫描黑名单前端展示')
    user = session.get('username')
    if str(user) == usernameconfig:
        global query_black_fscan_list
        message_json = {
        "query_black_fscan_list":query_black_fscan_list
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')


#fscan黑名单同步
@app.route("/flushfilterfscan/",methods=['get'])
def flushfilterfscan():
    app.logger.warning('fscan黑名单同步')
    user = session.get('username')
    if str(user) == usernameconfig:
        os.popen('bash /TIP/flask_cnvd/shellscript/fscanscan.sh fscansync')
        return render_template('scanner.html')
    else:
        return render_template('login.html')


#根据名称删除fscan扫描黑名单
@app.route("/deletefscanblackbyname/",methods=['get'])
def deletefscanblackbyname():
    app.logger.warning('根据名称删除fscan扫描黑名单')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        name = request.args['name']
        sql="DELETE from fscan_blacklist_table WHERE name = '%s' " %(name)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return render_template('scanner.html')
    except:
        return render_template('error.html')
#----------------------------------------fscan扫描模块------------------------------------------------#






#----------------------------------------指纹识别模块------------------------------------------------#
#跳转到指纹识别界面
@app.route("/finger/")
def finger():
    app.logger.warning('跳转到指纹识别界面')
    user = session.get('username')
    if str(user) == usernameconfig:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum'])
        cur = db.cursor()
        sql_finger="SELECT title,container,finger,cdntitle,opersystem,serverip,port,banner,cmsfinger,id,location,url FROM finger_table ORDER BY id DESC"
        cur.execute(sql_finger)
        sql_finger_data=cur.fetchall()
        return render_template('fingerprint.html',data=sql_finger_data)
    else:
        return render_template('login.html')



#根据ID删除指纹信息
@app.route("/deletefinger/",methods=['post'])
def deletefinger():
    app.logger.warning('根据ID删除指纹信息')
    id=request.form['id']
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql="DELETE FROM finger_table where id = '%s' " %(id)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return redirect("/finger/")
    except:
        pass


#指纹识别功能实现
@app.route("/fingerdemo/",methods=['POST'])
def fingerdemo():
    
    app.logger.warning('指纹识别功能实现')
    url=request.form['url']
    hearder={
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
    }

    #网站标题
    try:
        res = requests.get(url,headers=hearder,allow_redirects=False)
        res.encoding='utf-8'
        title_tmp0 = re.findall("<title>.*</title>",res.text)
        title_tmp1 = title_tmp0[0]
        title_tmp2 = title_tmp1.replace("<title>","")
    except:
        pass
    try:
        titletext = title_tmp2.replace("</title>","")
    except:
        titletext = "Not Found"
    #提取HTTP响应头(WEB容器识别)
    try:
        resheader = res.headers
    except:
        pass
    #WEB容器
    try:
        resheader_server = resheader['Server']
    except:
        resheader_server = "Not Found"
    #指纹框架
    try:
        resheader_language = resheader['X-Powered-By']
    except:
        resheader_language = "Not Found"
    #判断是否存在CDN
    CDN_tmp = re.findall("//.*",url)
    CDN_tmp_1 = CDN_tmp[0]
    CDN_tmp_2 = CDN_tmp_1.replace("//","")
    CDN_tmp_3 = CDN_tmp_2.replace("/","")

    #调用Tide团队指纹识别脚本，识别Banner和CMS_finger
    try:
        Banner_text_tmp = os.popen('bash /TIP/flask_cnvd/shellscript/TideFinger.sh'+' '+url+' '+'Banner').read()
        Banner_text_tmp1 = Banner_text_tmp.replace("[1;31m","")
        Banner_text_tmp2 = Banner_text_tmp1.replace("[0m","")
        Banner_text_tmp3 = Banner_text_tmp2.replace("[1;32m","")
        Banner_text_tmp4 = Banner_text_tmp3.replace("|",",")
        Banner_text = Banner_text_tmp4.replace("Banner: ","")

    except:
        Banner_text = "Not Found"


    try:
        CMS_finger_text1 = os.popen('bash /TIP/flask_cnvd/shellscript/TideFinger.sh'+' '+url+' '+'CMS_finger').read()
        CMS_finger_text2 = CMS_finger_text1.replace("CMS_finger:","")
        CMS_finger_text3 = CMS_finger_text2.replace("[1;","")
        CMS_finger_text4 = CMS_finger_text3.replace("31m","")
        CMS_finger_text5 = CMS_finger_text4.replace("[0m","")
        CMS_finger_text = CMS_finger_text5.replace("32m ","")
        

    except:
        CMS_finger_text = "Not Found"


    #判断域名是否存在www字符串
    if "www" in CDN_tmp_3:
        #CDN识别
        CDN_tmp_4 = CDN_tmp_3.replace("www.","")
        try:
            CDN = os.popen('bash /TIP/flask_cnvd/shellscript/finger.sh'+' '+CDN_tmp_4).read()
        except:
            CDN = "Not Found"
        #服务器IP识别
        IP = os.popen('bash /TIP/flask_cnvd/shellscript/domain_ip.sh'+' '+CDN_tmp_4).read()
        try:
            IP_P = os.popen('bash /TIP/flask_cnvd/shellscript/domain_ip_1.sh'+' '+CDN_tmp_4).read()
        except:
            IP_P = "Not Found"
        try:
            apis = shodan.Shodan(shodankey)
            result=apis.host(IP)
        except:
            pass
        #端口信息
        try:
            resultdata = result['ports']
        except:
            resultdata = "Not Found"

        #利用ping的ttl值判断操作系统，ttl值大于100windows系统，ttl值小于100Linux操作系统。
        try:
            data7 = os.popen('bash /TIP/flask_cnvd/shellscript/check_ip.sh'+' '+IP_P).read()
        except:
            data7 = "Not Found"

        #IP位置识别
        try:
            localtiondata_1 = os.popen('bash /TIP/flask_cnvd/shellscript/location.sh'+' '+IP_P).read()
            localtiondata_2 = localtiondata_1.replace("地址","")
            localtiondata = localtiondata_2.replace(":","")

        except:
            localtiondata = "Not Found"

        #指纹识别结果存入数据库
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum'])
        cur = db.cursor()
        sql_insertt = "insert into finger_table(title,container,finger,cdntitle,opersystem,serverip,port,banner,cmsfinger,location,url) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %(titletext,resheader_server,resheader_language,CDN,data7,IP_P,resultdata,Banner_text,CMS_finger_text,localtiondata,url)
        cur.execute(sql_insertt)
        db.commit()
        db.rollback()
        return render_template('fingerprint.html')
    else:

        #CDN识别
        try:
            CDN_1 = os.popen('bash /TIP/flask_cnvd/shellscript/finger.sh'+' '+CDN_tmp_3).read()
        except:
            CDN_1 = "Not Found"

        #服务器IP识别
        IP_1 = os.popen('bash /TIP/flask_cnvd/shellscript/domain_ip.sh'+' '+CDN_tmp_3).read()
        
        try:
            IP_1_p = os.popen('bash /TIP/flask_cnvd/shellscript/domain_ip_1.sh'+' '+CDN_tmp_3).read()
        except:
            IP_1_p = "Not Found"
        try:
            apis = shodan.Shodan(shodankey)
            result=apis.host(IP_1)   
        except:
            pass
        try:
            resultdata = result['ports']
        except:
            resultdata = "Not Found"

        #利用ping的ttl值判断操作系统，ttl值大于100windows系统，ttl值小于100Linux操作系统。
        try:
            data7 = os.popen('bash /TIP/flask_cnvd/shellscript/check_ip.sh'+' '+IP_1_p).read()
        except:
            data7 = "Not Found"

        #IP位置识别
        try:
            localtiondata_1 = os.popen('bash /TIP/flask_cnvd/shellscript/location.sh'+' '+IP_1_p).read()
            localtiondata_2 = localtiondata_1.replace("地址","")
            localtiondata = localtiondata_2.replace(":","")
        except:
            localtiondata = "Not Found"

        #指纹识别结果存入数据库
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum'])
        cur = db.cursor()
        sql_insertt = "insert into finger_table(title,container,finger,cdntitle,opersystem,serverip,port,banner,cmsfinger,location,url) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')" %(titletext,resheader_server,resheader_language,CDN,data7,IP_1_p,resultdata,Banner_text,CMS_finger_text,localtiondata,url)
        cur.execute(sql_insertt)
        db.commit()
        db.rollback()
        return render_template('fingerprint.html')
#----------------------------------------指纹识别模块------------------------------------------------#




#----------------------------------------fofa接口模块------------------------------------------------#
#跳转到fofa搜索页面
@app.route("/subdomainpage/")
def subdomainpage():
    
    app.logger.warning('跳转到fofa搜索页面')
    user = session.get('username')
    if str(user) == usernameconfig:
        #fofa扫描服务状态
        fofa_status_list = os.popen('bash /TIP/flask_cnvd/shellscript/scannerstatus.sh batchfofastatus').read()
        fofa_filenum_status_list = os.popen('bash /TIP/flask_cnvd/shellscript/scannerstatus.sh batchfofafilenumstatus').read()
        #文件行数
        fofa_file_num = os.popen('cat /TIP/flask_cnvd/file_txt/batchfofatarget.txt | wc -l').read()
        return render_template('subdomain.html',data01=fofa_status_list,data02=fofa_filenum_status_list,data03=fofa_file_num)
    else:
        return render_template('login.html')


#跳转到子域名搜索界面
@app.route("/fofasubdomain/")
def fofasubdomain():
    
    app.logger.warning('跳转到子域名搜索界面')
    user = session.get('username')
    if str(user) == usernameconfig:
        return render_template('fofasubdomain.html')
    else:
        return render_template('login.html')



#子域名搜索功能，调用fofa接口查询
@app.route("/fofasubdomainfunc/",methods=['POST'])
def fofasubdomainfunc():
    app.logger.warning('子域名搜索')
    resuledomainerror = ["数据接口或者搜索语法有误,请重试!"]
    try:
        
        domain1=request.form['domain']
        num=request.form['num']
        domain = domain1.replace("www.","")
        part1=domain.encode('utf-8')
        partbase64=base64.b64encode(part1)
        str1=str(partbase64,'utf-8')
        url = "https://fofa.info/api/v1/search/all?email=weakchicken@qq.com&key="+fofakey+"&size="+num+"&qbase64="
        hearder={
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            }
        res = requests.get(url+str1,headers=hearder,allow_redirects=False)
        res.encoding='utf-8'
        restext = res.text
        resdic=json.loads(restext)
        resdicresult=resdic['results']
        resuledomain = []
        resultdomain_list = []
        for ii in resdicresult:
            resuledomain.append(ii[0])
        for line in resuledomain:
            line_1 = line.replace("https://","")
            line_1_1 = line_1.replace("http://","")
            resultdomain_list.append(line_1_1)
        resulenull = ["未查询到相关数据"]
        #列表数据追加到文件中
        f = open(file='/TIP/flask_cnvd/file_txt/FofaSubdomain.txt',mode='w')
        for ii in resultdomain_list:
            f.write(str(ii)+"\n")
        if len(resultdomain_list) == 0:
            return render_template('fofasubdomain.html',data=resulenull,data1=domain)
        else:
            return render_template('fofasubdomain.html',data=resultdomain_list,data1=domain)
    
    except:
        return render_template('fofasubdomain.html',data=resuledomainerror,data1=domain)


#FofaSubdomain.txt文件下载
@app.route("/fofasubdomaindownload/")
def fofasubdomaindownload():
    app.logger.warning('Fofasubdomain文件下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/file_txt/FofaSubdomain.txt',directory ='/TIP/flask_cnvd/file_txt',filename="FofaSubdomain.txt",as_attachment=True)
    else:
        return render_template('login.html')


#调用fofapi查询数据
@app.route("/domainsearch/",methods=['POST'])
def domainsearch():
    resuledomainerror = ["数据接口或者搜索语法有误,请重试!"]
    app.logger.warning('Fofa搜索')
    domain1=request.form['domain']
    oper=request.form['oper']
    num=request.form['num']
    domain = domain1.replace("www.","")
    part1=domain.encode('utf-8')
    partbase64=base64.b64encode(part1)
    str1=str(partbase64,'utf-8')
    if oper == str(1):
        try:
            url = "https://fofa.info/api/v1/search/all?email=weakchicken@qq.com&key="+fofakey+"&size="+num+"&qbase64="
            hearder={
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                }
            res = requests.get(url+str1,headers=hearder,allow_redirects=False)
            res.encoding='utf-8'
            restext = res.text
            resdic=json.loads(restext)
            resdicresult=resdic['results']
            resuledomain = []
            resuledomain1 = []
            
            for ii in resdicresult:
                resuledomain.append(ii[0])
            resulenull = ["未查询到相关数据"]

            #判断是否为http开头的字符串
            for jj in resuledomain:
                if 'http' in jj:
                    resuledomain1.append(jj)
            
            #列表数据追加到文件中
            f = open(file='/TIP/flask_cnvd/file_txt/FofaSearch.txt',mode='w')
            for ij in resuledomain1:
                f.write(str(ij)+"\n")
            
            if len(resuledomain) == 0:
                
                return render_template('subdomain.html',data=resulenull,data1=domain,data003=domain1)
            else:
                return render_template('subdomain.html',data=resuledomain1,data1=domain,data003=domain1)
        
        except:
            return render_template('subdomain.html',data=resuledomainerror,data1=domain)
    
    elif oper == str(2):
        try:
            
            url = "https://fofa.info/api/v1/search/all?email=weakchicken@qq.com&key="+fofakey+"&size="+num+"&qbase64="
            hearder={
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                }
            res = requests.get(url+str1,headers=hearder,allow_redirects=False)
            res.encoding='utf-8'
            restext = res.text
            resdic=json.loads(restext)
            resdicresult=resdic['results']
            resuledomain = []
            for ii in resdicresult:
                resuledomain.append(ii[1])
            resulenull = ["未查询到相关数据"]
            #列表数据追加到文件中
            f = open(file='/TIP/flask_cnvd/file_txt/FofaSearch.txt',mode='w')
            for ij in resuledomain:
                f.write(str(ij)+"\n")
            
            if len(resuledomain) == 0:
                
                return render_template('subdomain.html',data=resulenull,data1=domain,data003=domain1)
            else:
                return render_template('subdomain.html',data=resuledomain,data1=domain,data003=domain1)
        except:
            return render_template('subdomain.html',data=resuledomainerror,data1=domain)


#fofa扫描结果文件预览
@app.route("/fofasearchpreview/")
def fofasearchpreview():
    app.logger.warning('fofa扫描结果文件预览')
    user = session.get('username')
    if str(user) == usernameconfig:
        lines = []
        with open('/TIP/flask_cnvd/file_txt/fofaSearchresult.txt', 'r') as f:
            for line in f:
                lines.append(line.strip())
        return '<br>'.join(lines)
        
    else:
        return render_template('login.html')
    

#启动fofa批量检索接口
@app.route("/startbatchfofainterface/")
def startbatchfofainterface():
    
    app.logger.warning('启动fofa批量检索接口')
    user = session.get('username')
    if str(user) == usernameconfig:
        os.popen('python3 /TIP/flask_cnvd/batchfofa_start.py > /TIP/flask_cnvd/file_txt/fofaSearchresult.txt')
        return render_template('subdomain.html')
    else:
        return render_template('login.html')
    

#fofa目标文件去重接口
@app.route("/uniqbatchfofainterface/")
def uniqbatchfofainterface():
    
    app.logger.warning('fofa目标文件去重接口')
    user = session.get('username')
    if str(user) == usernameconfig:
        os.popen('bash /TIP/flask_cnvd/shellscript/awkdirsearchfilter.sh uniqfofa_batch')
        return render_template('subdomain.html')
    else:
        return render_template('login.html')


#结束fofa扫描接口进程
@app.route("/killbatchfofainterface/")
def killbatchfofainterface():
    
    app.logger.warning('结束fofa扫描接口进程')
    user = session.get('username')
    if str(user) == usernameconfig:
        os.popen('bash /TIP/flask_cnvd/shellscript/killscan.sh killbatchfofa')
        return render_template('subdomain.html')
    else:
        return render_template('login.html')


#----------------------------------------fofa接口模块------------------------------------------------#
    



#----------------------------------------子域名扫描模块------------------------------------------------#
#跳转到子域名扫描界面
@app.route("/subdomainsbrutescan/")
def subdomainsbrutescan():
    app.logger.warning('跳转到子域名扫描界面')
    user = session.get('username')
    if str(user) == usernameconfig:
        subdomainsbrute_status_list = os.popen('bash /TIP/flask_cnvd/shellscript/scannerstatus.sh subDomainsBrutestatus').read()
        #子域名显示给前端        
        awk_sub = os.popen('bash /TIP/flask_cnvd/shellscript/awksubdomain.sh awksub').read()
        awk_sub_list = []
        for i in awk_sub.splitlines():
            awk_sub_list.append(i)
        #删除列表中最后面两个元素ALL和Output
        del awk_sub_list[-2:]
        
        #IP地址回显给前端
        awk_sub_ip= os.popen('bash /TIP/flask_cnvd/shellscript/awksubdomain.sh awksubip').read()
        awk_sub_ip_list = []
        for j in awk_sub_ip.splitlines():
            j_tmp = j.replace(",","")
            awk_sub_ip_list.append(j_tmp)
        #删除列表中最后面两个元素ALL和Output
        del awk_sub_ip_list[-2:]

        #将两个列表进行打包，转为为元组类型，然后回显给前端进行展示。
        tuple_list = zip(awk_sub_list,awk_sub_ip_list)
        tuple_list_result = []
        for k in tuple_list:
            tuple_list_result.append(k)
        list_tuple_list = tuple(tuple_list_result)
       
        #将子域名写入到子域名列表.txt
        file_domain_file = open(file='/TIP/flask_cnvd/file_txt/子域名列表.txt',mode='w')
        #删除列表为空的元素
        while '' in awk_sub_list:
            awk_sub_list.remove('')
        for ii in awk_sub_list:
            file_domain_file.write(ii+"\n")

        #将IP写入到子域名IP列表.txt
        file_domain_ip_file =  open(file='/TIP/flask_cnvd/file_txt/子域名IP列表.txt',mode='w')
        #删除列表为空的元素
        while '' in awk_sub_ip_list:
            awk_sub_ip_list.remove('')
        #子域名IP列表去重
        awk_sub_ip_list_1 = list(set(awk_sub_ip_list))
        for jj in awk_sub_ip_list_1:
            file_domain_ip_file.write(jj+"\n")

        return render_template('subdomainsbrutescan.html',data1=subdomainsbrute_status_list,data2=list_tuple_list)
    else:
        return render_template('login.html')


#子域名扫描前初始化
@app.route("/subdomainsbrutescanInitialize/",methods=['POST'])
def subdomainsbrutescanInitialize():
    
    app.logger.warning('子域名扫描前初始化')
    user = session.get('username')
    if str(user) == usernameconfig:
        try:
            os.popen('rm -rf /TIP/flask_cnvd/subDomainsBrute/tmp/')
            os.popen('rm -rf /TIP/flask_cnvd/file_txt/subdomain.txt')
            os.popen('touch /TIP/flask_cnvd/file_txt/subdomain.txt')
        except:
            pass
        return render_template('subdomainsbrutescan.html')
    else:
        return render_template('login.html')


#结束子域名扫描进程
@app.route("/killsubdomainsbrutescan/",methods=['POST'])
def killsubdomainsbrutescan():
    
    app.logger.warning('结束子域名扫描进程')
    user = session.get('username')
    if str(user) == usernameconfig:
        try:
            os.popen('bash /TIP/flask_cnvd/shellscript/killscan.sh killsubDomainsBrute')
        except:
            pass
        return render_template('subdomainsbrutescan.html')
    else:
        return render_template('login.html')


#subDomainsBrute子域名扫描功能
@app.route("/subDomainsBrutefunc/",methods=['post'])
def subDomainsBrutefunc():
    app.logger.warning('子域名扫描功能')
    user = session.get('username')
    domain = request.form['domain']
    dict = request.form['dict']
    list = ["扫描任务已下发............"]
    if str(user) == usernameconfig:
        if dict == str(1):
            os.popen('bash /TIP/flask_cnvd/shellscript/subdomain.sh subDomainsBrutescan1'+''+' '+domain+'')
            return render_template('subdomainsbrutescan.html',data=list)
        elif dict == str(2):
            os.popen('bash /TIP/flask_cnvd/shellscript/subdomain.sh subDomainsBrutescan2'+''+' '+domain+'')
            return render_template('subdomainsbrutescan.html',data=list)
        else:
            return render_template('subdomainsbrutescan.html',data=list)
    else:
        return render_template('login.html')


#子域名扫描模块子域名列表下载
@app.route("/subdomainlistfiledown/")
def subdomainlistfiledown():
    app.logger.warning('子域名扫描模块子域名列表下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/file_txt/子域名列表.txt',directory ='/TIP/flask_cnvd/file_txt',filename="子域名列表.txt",as_attachment=True)
    else:
        return render_template('login.html')


#子域名扫描模块IP列表下载
@app.route("/subdomainiplistfiledown/")
def subdomainiplistfiledown():
    app.logger.warning('子域名扫描模块IP列表下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/file_txt/子域名IP列表.txt',directory ='/TIP/flask_cnvd/file_txt',filename="子域名IP列表.txt",as_attachment=True)
    else:
        return render_template('login.html')
#----------------------------------------子域名扫描模块------------------------------------------------#





#----------------------------------------dirsearch目录扫描模块------------------------------------------------#
#dirsearch扫描结果下载
@app.route("/dirsearchfiledownload/")
def dirsearchfiledownload():
    app.logger.warning('dirsearch扫描结果下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/file_txt/dirsearchfileresult.txt',directory ='/TIP/flask_cnvd/file_txt',filename="dirsearchfileresult.txt",as_attachment=True)
    else:
        return render_template('login.html')



#dirsearch目标文件下载
@app.route("/dirsearchtargeetdown/")
def dirsearchtargeetdown():
    app.logger.warning('dirsearch目标文件下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/file_txt/dirsearchtarget.txt',directory ='/TIP/flask_cnvd/file_txt',filename="dirsearchtarget.txt",as_attachment=True)
    else:
        return render_template('login.html')



#dirsearch目标文件去重和过滤接口
@app.route("/uniqdirsearchtargetinterface/",methods=['POST'])
def uniqdirsearchtargetinterface():
    app.logger.warning('dirsearch目标文件去重和过滤接口')
    user = session.get('username')
    if str(user) == usernameconfig:
        fileqingxiname = request.form['fileqingxiname']
        if int(fileqingxiname) == 1:
            
            #将漏洞链接表中的字段写入到文件中
            db= pymysql.connect(host=dict['ip'],user=dict['username'],  
            password=dict['password'],db=dict['dbname'],port=dict['portnum'])
            cur = db.cursor()
            sql = "select vulnurl from vuln_url_table order by id desc"
            cur.execute(sql)
            data = cur.fetchall()
            f = open('/TIP/flask_cnvd/file_txt/filter_vuln_url.txt',mode='w')
            for i in list(data):
                for j in i:
                    f.write(str(j)+"\n")

            #扫描目标文件去重，过滤、只保留IP地址
            os.popen('bash /TIP/flask_cnvd/shellscript/filterdirsearchdata.sh withdrawip')

            return render_template('dirsearchscan.html')

        else:
            #将漏洞链接表中的字段写入到文件中
            db= pymysql.connect(host=dict['ip'],user=dict['username'],  
            password=dict['password'],db=dict['dbname'],port=dict['portnum'])
            cur = db.cursor()
            sql = "select vulnurl from vuln_url_table order by id desc"
            cur.execute(sql)
            data = cur.fetchall()
            f = open('/TIP/flask_cnvd/file_txt/filter_vuln_url.txt',mode='w')
            for i in list(data):
                for j in i:
                    f.write(str(j)+"\n")

            #扫描目标文件去重，过滤，保留所有
            os.popen('bash /TIP/flask_cnvd/shellscript/filterdirsearchdata.sh uniqfilterdirsearch')
    
            return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')



#跳转到目录扫描界面
@app.route("/dirsearchscan/")
def dirsearchscan():
    app.logger.warning('跳转到目录扫描界面')
    user = session.get('username')
    if str(user) == usernameconfig:
        dirsearch_list = [] #回显给前端的处理后数据，不带http状态码(2023.05.29修改data)。
        dir_list_status_code = [] #回显给前端的原始数据，带http状态码。
        dir_no_swa_list = []
        
        #无后缀的URL列表
        dir_no_swa_list_1 = []
        global dir_no_swa_list_1_1
        dir_no_swa_list_1_1 = dir_no_swa_list_1

        dirsearch_file = open('/TIP/flask_cnvd/file_txt/dirsearchfileresult.txt',encoding='utf-8')
        for line in dirsearch_file.readlines():
            dir_list_status_code.append(line)
            #捕获异常，报错直接PASS
            try:
                dirsearch_re = re.findall("http://.*|https://.*",line)
                dirsearch_list.append(dirsearch_re[0])
            except:
                pass

        #遍历不带状态码的URL列表,利用正则匹配出http://www.baidu.com/
        for b in dirsearch_list:
            no_swa = re.findall("http://.*?/|https://.*?/",b)
            dir_no_swa_list.append(no_swa)
        for c in dir_no_swa_list:
            dir_no_swa_list_1.append(c[0])


        #目录扫描状态，回显给前端。
        dir_status_list = os.popen('bash /TIP/flask_cnvd/shellscript/scannerstatus.sh dirsearchstatus').read()

        #vulmap漏洞扫描状态，回显给前端
        vulmap_status_list = os.popen('bash /TIP/flask_cnvd/shellscript/scannerstatus.sh vulmapscanstatus').read()

        #httpx运行状态
        httpx_status_list = os.popen('bash /TIP/flask_cnvd/shellscript/scannerstatus.sh httpxscanstatus').read()

        #nuclei运行状态
        nuclei_status_list = os.popen('bash /TIP/flask_cnvd/shellscript/nuclei_program.sh nucleistatus').read()

        #文件清洗服务运行状态
        file_clean_status = os.popen('bash /TIP/flask_cnvd/shellscript/scannerstatus.sh fileclean').read()

        #单条数据回显给前端
        try:
            db= pymysql.connect(host=dict['ip'],user=dict['username'],  
            password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
            cur = db.cursor()
            sql="select url,id from scan_table order by id desc"
            cur.execute(sql)
            dirdata = cur.fetchall()
        except:
            pass

        #回显给前端的目标文件行数
        num = os.popen('bash /TIP/flask_cnvd/shellscript/killscan.sh dirsearchtargetnum').read()
        num11 = int(num) + 1 
        if num11 == 1:
            num11_1 = 0
        else:
            num11_1 = num11
        num_1 = "URL数量: "+" "+str(num11_1)
        num_2 = str(num11_1)

        #回显给前端的漏洞数量
        vuln_num = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapcount').read()
        vuln_num_int = int(vuln_num)
        if vuln_num_int == 0:
            vuln_num_int_1 = "漏洞数量："+"目前暂无漏洞"
        else:
            vuln_num_int_1 = "漏洞数量："+str(vuln_num_int)

        #回显给前端的目录扫描数量
        dirsearch_count_tmp = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh dirsearchscancount').read()
        if int(dirsearch_count_tmp) == -2:
            dirsearch_count = "目录数量（过滤前）："+"目前暂无漏洞"
        else:
            dirsearch_count = "目录数量（过滤前）："+str(dirsearch_count_tmp)

        #判断目录扫描漏洞数量是否有更新
        dirsearch_count_copy = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh dirsearchscancountcopy').read()

        #将str类型转为int类型进行比较大小
        dirsearch_count_tmp_int = int(dirsearch_count_tmp)
        dirsearch_count_copy_int = int(dirsearch_count_copy)
        if dirsearch_count_tmp_int > dirsearch_count_copy_int:
            dirsearch_data_judgment = "系统检测到有数据更新,点击原始数据同步更新数据"
        else:
            dirsearch_data_judgment = "目前暂无数据更新,有更新在点击原始数据同步更新"

        
        #httpx扫描进度展示
        #取httpx扫描过程中文件的最后一行字符串
        tail_httpx = os.popen('bash /TIP/flask_cnvd/shellscript/awkrunhttpx.sh tail_httpx').read()
        #httpx扫描过程中最后一行字符串在目标文件所在行数
        httpx_rows = os .popen('bash /TIP/flask_cnvd/shellscript/awkrunhttpx.sh httpx_rows'+' '+tail_httpx).read()
        #利用正则表达式匹配行数
        httpx_rows_regular = re.findall("\d+",httpx_rows)

        #判断列表是否为空,如果为空等于0,如果不为空等于httpx_rows_regular[0]
        if len(httpx_rows_regular) == 0:
            httpx_rows_result = "0"
        else:
            httpx_rows_result = httpx_rows_regular[0]

        #目录扫描同步后的数量
        dirsearch_sync_value = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh dirsearchsyncresult').read()
        dirsearch_sync_value_result = "目录数量（过滤后）："+str(dirsearch_sync_value)
        mark = httpx_rows_result+ "/" +num_2

        return render_template('dirsearchscan.html',data=dirsearch_list,data5=dir_status_list,data6=dirdata,data7=num_1,
        data09=dir_list_status_code,data11=vulmap_status_list,data12=vuln_num_int_1,data13=dirsearch_count,data14=dirsearch_data_judgment,
        data15=httpx_status_list,data16=mark,data18=dirsearch_sync_value_result,data19=nuclei_status_list,
        data20=file_clean_status)
    else:
        return render_template('login.html')




#目录扫描查询原始数据接口
@app.route("/queryorigindatainterface/",methods=['post'])
def queryorigindatainterface():

    app.logger.warning('目录扫描查询原始数据接口')
    user = session.get('username')
    url_data = request.form['url_data']
    if str(user) == usernameconfig:
        list_result = []
        global global_item_origin_data
        file_result = open('/TIP/flask_cnvd/file_txt/dirsearchfileresult.txt',encoding='utf-8')
        #将文件存到列表中用于检索
        for line in file_result.readlines():
            list_result.append(line)
        #前端传入的字符在列表中查找，查找到显示完整的字符串
        for item in list_result:
            if url_data in item:
                global_item_origin_data_1 = item

        #域名归属公司查询
        url = "https://icp.chinaz.com/"
        hearder = {
        'Cookie':'qHistory=Ly9pY3AuY2hpbmF6LmNvbS9qZC5jb21f572R56uZ5aSH5qGI5p+l6K+i; cz_statistics_visitor=68f8740c-7d0c-2be1-809e-b02636111b44; Hm_lvt_ca96c3507ee04e182fb6d097cb2a1a4c=1678588537; Hm_lpvt_ca96c3507ee04e182fb6d097cb2a1a4c=1678588537',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
        'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'
        }
        url_value_re = re.search(r'https?://([^/:]+)', url_data)
        url_value_result = url_value_re.group(1)
        res = requests.get(url+url_value_result,headers=hearder,allow_redirects=False)
        res.encoding = 'utf-8'
        soup=BeautifulSoup(res.text,'html.parser')
        soup_p = soup.find_all('p')
        soup_p_value = soup_p[10]
        soup_p_value_text = soup_p_value.text
        if is_valid_ip(url_value_result):
            soup_p_value_text_1 = "无法通过IP查询公司名称"
        else:
            soup_p_value_text_1 = soup_p_value_text
        global_item_origin_data = "原始数据："+global_item_origin_data_1+"  "+"域名备案信息："+soup_p_value_text_1
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')



#目录扫描查询原始数据接口前端展示
@app.route("/queryorigindatainterfacebyajax/",methods=['GET'])
def queryorigindatainterfacebyajax():
    app.logger.warning('目录扫描查询原始数据接口前端展示')
    global global_item_origin_data

    message_json = {
    "global_item_origin_data":global_item_origin_data
   
    }
    return jsonify(message_json)




#屏蔽设定的阈值策略
@app.route("/filterthresholdvalue/",methods=['get'])
def filterthresholdvalue():
    app.logger.warning('屏蔽设定的阈值策略')
    user = session.get('username')
    if str(user) == usernameconfig:

        thresholdname = request.args['thresholdname']
        #重复数大于4的列表元素
        dir_no_swa_list_2 = []
        #无后缀的URL列表,原始数据。
        global dir_no_swa_list_1_1

        #遍历新列表dir_no_swa_list_1，利用count函数判断出现的次数，大于4次的，追加到新的列表中，用于去重使用。
        for d in dir_no_swa_list_1_1:
            #列表元素出现的次数
            num_m = dir_no_swa_list_1_1.count(d)
            #列表中次数大于等于5的存到列表dir_no_swa_list_2
            if num_m >= int(thresholdname):
                dir_no_swa_list_2.append(d)

        #利用集合set去重列表，存到列表dir_no_swa_list_2_removal中
        dir_no_swa_list_2_removal = list(set(dir_no_swa_list_2))
        

        #将全局的列表写入到文件中，屏蔽阈值使用。
        f = open(file='/TIP/flask_cnvd/file_txt/thresholdvalue.txt', mode='w')
        for ii in dir_no_swa_list_2_removal:
            f.write(str(ii)+"\n")
    
        #调用shell脚本进行屏蔽操作
        os.popen('bash /TIP/flask_cnvd/shellscript/filterdirsearchdata.sh value4')
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')



#目录扫描功能实现
@app.route("/dirsearchscanfun/",methods=['post'])
def dirsearchscanfun():
    app.logger.warning('dirsearch目录扫描实现')
    user = session.get('username')
    filename = request.form['filename']
    thread = request.form['thread']
    statuscode = request.form['statuscode']
    level = request.form['level']
    dict = request.form['dict']
    list = ["扫描任务已下发............"]
    
    if str(user) == usernameconfig:
        
        os.popen('bash /TIP/flask_cnvd/shellscript/directoryscan.sh dirsearchscan'+''+' '+filename+''+' '+level+''+' '+statuscode+''+' '+dict+''+' '+thread+'')
        return render_template('dirsearchscan.html',data=list)
    else:
        return render_template('login.html')



#dirsearch扫描后黑名单录入并写入到文件中
@app.route("/filterdirsearch/",methods=['post'])
def filterdirsearch():
    
    app.logger.warning('dirsearch扫描后黑名单录入并写入到文件中')
    user = session.get('username')
    keyvalue = request.form['keyvalue']

    if str(user) == usernameconfig:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        
        #检查是否存在相同数据
        sql_select = "select * from blacklist_table where name = '%s' "%(keyvalue)
        cur.execute(sql_select)
        result = cur.fetchone()
        global dirsearch_vuln_url_message
        if result:
            dirsearch_vuln_url_message = "扫描后黑名单"+keyvalue+"已存在请不要重复添加"
        else:
            sql_insert = "insert into blacklist_table(name)  values('%s')" %(keyvalue)
            cur.execute(sql_insert)  
            db.commit()
            dirsearch_vuln_url_message = "扫描后黑名单"+keyvalue+"已添加成功"


        #生成文件用于过滤扫描结果
        sql1 = "select name from blacklist_table order by id desc"
        cur.execute(sql1)
        data1 = cur.fetchall()
        f = open(file='/TIP/flask_cnvd/file_txt/filterdirsearch.txt', mode='w')
        for ii in list(data1):
            for jj in ii:
                f.write(str(jj)+"\n")
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')


#判断扫描后黑名单添加状态
@app.route("/showdirsearchstatusinterfaceajax/",methods=['GET'])
def showdirsearchstatusinterfaceajax():
    app.logger.warning('判断扫描后黑名单添加状态')
    user = session.get('username')
    if str(user) == usernameconfig:
        global dirsearch_vuln_url_message
        message_json = {
        "dirsearch_vuln_url_message":dirsearch_vuln_url_message
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')



#dirsearch白名单录入并写入到文件中
@app.route("/filterdirsearchbywhite/",methods=['post'])
def filterdirsearchbywhite():
    
    app.logger.warning('dirsearch白名单录入并写入到文件中')
    user = session.get('username')
    keyvalue1 = request.form['keyvalue1']

    if str(user) == usernameconfig:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql_insert = "insert into whitelist_table(name)  values('%s')" %(keyvalue1)
        cur.execute(sql_insert)  
        db.commit()
        db.rollback()
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')



#屏蔽关键词设置(黑名单)
@app.route("/flushfilter/",methods=['get'])
def flushfilter():
    app.logger.warning('屏蔽关键词设置(黑名单)')
    user = session.get('username')
    if str(user) == usernameconfig:
        os.popen('bash /TIP/flask_cnvd/shellscript/filterdirsearchdata.sh value1')
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')



#屏蔽关键词设置(白名单)
@app.route("/flushfilterbywhite/",methods=['get'])
def flushfilterbywhite():
    app.logger.warning('屏蔽关键词设置(白名单)')
    user = session.get('username')
    if str(user) == usernameconfig:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql1 = "select name from whitelist_table order by id desc"
        cur.execute(sql1)
        data1 = cur.fetchall()
        #白名单从数据库查询出来是元组格式转换列表格式
        tup_list = []
        for i in data1:
            tup_list.append(i[0])

        #遍历白名单列表执行shell脚本，将执行的结果追加到结果列表中
        result_list = []
        for j in tup_list:
            result = os.popen('bash /TIP/flask_cnvd/shellscript/filterdirsearchdata.sh value2'+' '+j+'').read()
            result_list.append(result)

        #将存入到列表中的结果写入到最终的文件中用于前端展示
        f = open(file='/TIP/flask_cnvd/file_txt/dirsearchfileresult.txt', mode='w')
        for ii in result_list:
            f.write(str(ii))

        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')


#目录扫描后黑名单查询
@app.route("/QueryingBlacklist/",methods=['GET'])
def QueryingBlacklist():
    
    app.logger.warning('目录扫描后黑名单查询')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql="select name from blacklist_table order by id desc"
        cur.execute(sql)
        data = cur.fetchall()
        list_data = list(data)
        global query_black_list
        query_black_list = list_data
        return render_template('dirsearchscan.html')
    except:
        return render_template('error.html',data=datainfo)



#目录扫描前黑名单查询
@app.route("/queryingbeforeblacklist/",methods=['GET'])
def queryingbeforeblacklist():
    
    app.logger.warning('目录扫描前黑名单查询')
    user = session.get('username')
    if str(user) == usernameconfig:
        
        #数据库连接部分
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        
        #sql语句扫描前黑名单查询部分
        sql="SELECT vulnurl from vuln_url_table order by id desc"
        cur.execute(sql)
        data = cur.fetchall()
        list_data1 = list(data)
        global query_before_black_list
        query_before_black_list = list_data1

        #sql语句扫描后黑名单查询部分
        sql_after = "select * from blacklist_table order by id desc"
        cur.execute(sql_after)
        data_after =  cur.fetchall()
        list_data_after = list(data_after)
        message_json = {
        "query_before_black_list":query_before_black_list,
        "query_before_black_list_len":"扫描前黑名单数量: "+str(len(query_before_black_list)),
        "query_after_black_list_len":"扫描后黑名单数量: "+str(len(list_data_after))
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')




#目录扫描白名单查看
@app.route("/QueryingWhitelist/",methods=['GET'])
def QueryingWhitelist():
    
    app.logger.warning('目录扫描白名单查看')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql="select name from whitelist_table order by id desc"
        cur.execute(sql)
        data1 = cur.fetchall()
        list_data1 = list(data1)
        global query_white_list
        query_white_list = list_data1
        return render_template('dirsearchscan.html')
    except:
        return render_template('error.html',data=datainfo)



#目录扫描程序日志处理
@app.route("/dirsearchlogoperation/")
def dirsearchlogoperation():

    app.logger.warning('目录扫描程序日志处理')
    user = session.get('username')
    if str(user) == usernameconfig:

        #只给前端回显域名信息
        dirsearchlog = os.popen('bash /TIP/flask_cnvd/shellscript/awkdirsearchfilter.sh domain').read()
        dirsearchlog_list_1 = []
        for i in dirsearchlog.splitlines():
            i_tmp = i.replace("\"","")
            i_tmp_1 = re.findall("http://.*?/|https://.*?/",i_tmp)
            dirsearchlog_list_1.append(i_tmp_1)

        #定义全局变量
        global dirsearchlog_listresult
        dirsearchlog_list = []
        for j in dirsearchlog_list_1:
            dirsearchlog_list.append(j[0])
        dirsearchlog_listresult = dirsearchlog_list
       
       #给前端回显全部日志信息
        dirsearchalllog = os.popen('bash /TIP/flask_cnvd/shellscript/awkdirsearchfilter.sh domainall').read()
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')


#目录扫描程序日志前端展示
@app.route("/Queryingdirsearchlogbyajax/",methods=['GET'])
def Queryingdirsearchlogbyajax():
    app.logger.warning('目录扫描程序日志前端展示')
    user = session.get('username')
    if str(user) == usernameconfig:
        global dirsearchlog_listresult
        message_json = {
        "dirsearchlog_listresult":dirsearchlog_listresult
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')


#目录扫描黑名单前端展示
@app.route("/QueryingBlacklistbyajax/",methods=['GET'])
def QueryingBlacklistbyajax():
    app.logger.warning('目录扫描黑名单前端展示')
    user = session.get('username')
    if str(user) == usernameconfig:
        global query_black_list
        message_json = {
        "query_black_list":query_black_list
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')


#目录扫描白名单前端展示
@app.route("/QueryingWhitelistbyajax/",methods=['GET'])
def QueryingWhitelistbyajax():
    app.logger.warning('目录扫描白名单前端展示')
    user = session.get('username')
    if str(user) == usernameconfig:
        global query_white_list
        message_json = {
        "query_white_list":query_white_list
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')



#dirsearch扫描结果复制给前端页面展示
@app.route("/dirsearchcopyfile/")
def dirsearchcopyfile():
    
    app.logger.warning('dirsearch扫描结果复制给前端页面展示')
    user = session.get('username')
   
    if str(user) == usernameconfig:
        os.popen('cp /TIP/flask_cnvd/dirsearch/reports/*/* /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt')
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')
   


#后台结束dirsearch进程
@app.route("/killdirsearch/",methods=['post'])
def killdirsearch():
    app.logger.warning('后台结束dirsearch扫描器进程')
    try:
        os.popen('bash /TIP/flask_cnvd/shellscript/killscan.sh killdirsearch')
        return render_template('dirsearchscan.html')
    except:
        pass


#dirsearch添加扫描目标
@app.route("/adddirsearchdata/",methods=['post'])
def adddirsearchdata():
    
    app.logger.warning('dirsearch扫描目标录入') 
    try:

        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        url = request.form['url']
        sql_insert = "insert into scan_table(url)  values('%s')" %(url)
        cur.execute(sql_insert)  
        db.commit()
        db.rollback()
        return render_template('dirsearchscan.html')
    except:
        return render_template('error.html')

#按ID删除dirsearch扫描目标
@app.route("/deletedirsearchbyid/",methods=['get'])
def deletedirsearchbyid():
    app.logger.warning('通过ID删除dirsearch扫描目标')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        id = request.args['id']
        sql="delete from scan_table where id = '%s' " %(id)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return render_template('dirsearchscan.html')
    except:
        return render_template('error.html')


#根据名称删除目录扫描后黑名单
@app.route("/deletedirsearchblackbyname/",methods=['get'])
def deletedirsearchblackbyname():
    app.logger.warning('根据名称删除目录扫描后黑名单')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        name = request.args['name']
        sql="DELETE from blacklist_table WHERE name = '%s' " %(name)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return render_template('dirsearchscan.html')
    except:
        return render_template('error.html')



#根据名称删除目录扫描前黑名单
@app.route("/deletedirsearcscanbeforehblackbyname/")
def deletedirsearcscanbeforehblackbyname():
    
    app.logger.warning('根据名称删除目录扫描前黑名单')
    user = session.get('username')
   
    if str(user) == usernameconfig:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        vulnurl = request.args['vulnurl']
        sql="DELETE from vuln_url_table WHERE vulnurl = '%s' " %(vulnurl)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')



#根据名称删除目录扫描白名单
@app.route("/deletedirsearchwhitebyname/",methods=['get'])
def deletedirsearchwhitebyname():
    app.logger.warning('根据名称删除目录扫描白名单')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        name = request.args['name']
        sql="DELETE from whitelist_table WHERE name = '%s' " %(name)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return render_template('dirsearchscan.html')
    except:
        return render_template('error.html')




#目录扫描文件上传XLSX转文本
@app.route("/baseconfile/")
def baseconfile():
    app.logger.warning('目录扫描文件上传XLSX转文本')
    user = session.get('username')
    if str(user) == usernameconfig:
        
        #dirsearchfilepath目录下的excel文件重名为1.xlsx
        os.popen('mv /TIP/flask_cnvd/dirsearch/dirsearchfilepath/* /TIP/flask_cnvd/dirsearch/dirsearchfilepath/1.xlsx')
        #打开excel表格
        excel = xlrd.open_workbook('/TIP/flask_cnvd/dirsearch/dirsearchfilepath/1.xlsx')
        #获取指定Sheet表单页
        sheet = excel.sheet_by_name(dir_vul_url)
        nrows = sheet.nrows
        #定义url存储列表url_list
        url_list = []
        for i in range(0,nrows):
            url_list.append(sheet.row_values(i)[0])
        
        #循环列表url_list写入到文件dirsearchtarget.txt
        f = open(file='/TIP/flask_cnvd/file_txt/dirsearchtarget.txt',mode='w')
        for ii in url_list:
            f.write(str(ii)+"\n")
            
        return render_template('dirsearchscan.html')

    else:
        return render_template('login.html')



#目录扫描文件上传XLSX压缩包转文本
@app.route("/packagebaseconfileinterface/")
def packagebaseconfileinterface():
    app.logger.warning('目录扫描文件上传XLSX压缩包转文本')
    user = session.get('username')
    if str(user) == usernameconfig:
        
        #dirsearchfilepath目录下的excel文件压缩包重命名为target.zip
        os.popen('mv /TIP/flask_cnvd/dirsearch/dirsearchfilepath/* /TIP/flask_cnvd/dirsearch/dirsearchfilepath/target.zip')
        #解压文件
        zip_file = "/TIP/flask_cnvd/dirsearch/dirsearchfilepath/target.zip"
        extract_path = os.path.join(os.getcwd(), "/TIP/flask_cnvd/dirsearch/dirsearchfilepath")
        # 构建命令行参数
        unzip_args = ["unzip", "-q", "-o", zip_file, "-d", extract_path]
        # 执行命令
        subprocess.Popen(unzip_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        os.popen('mv /TIP/flask_cnvd/dirsearch/dirsearchfilepath/*/* /TIP/flask_cnvd/dirsearch/dirsearchfilepath/')
        #删除压缩包
        os.popen('rm -rf /TIP/flask_cnvd/dirsearch/dirsearchfilepath/*.zip')
        
        # 定义要读取的文件夹路径
        folder_path = "/TIP/flask_cnvd/dirsearch/dirsearchfilepath"
        # 获取文件夹下的所有文件名
        file_names = os.listdir(folder_path)
        # 遍历文件夹下的所有Excel文件，读取每个文件的数据
        #data = pd.DataFrame()
        url_list = []
        for file_name in file_names:
            if file_name.endswith('.xlsx'):
                file_path = os.path.join(folder_path, file_name)
                excel = xlrd.open_workbook(file_path)
                #获取指定Sheet表单页
                sheet = excel.sheet_by_name(dir_vul_url)
                nrows = sheet.nrows
                #定义url存储列表url_list
                for i in range(0,nrows):
                    url_list.append(sheet.row_values(i)[0])
        #print(url_list)
        #print(len(url_list))
        #将列表存入到文件中
        f = open(file='/TIP/flask_cnvd/file_txt/dirsearchtarget.txt',mode='w')
        for ii in url_list:
            f.write(str(ii)+"\n")
        return render_template('dirsearchscan.html')

    else:
        return render_template('login.html')



#fofa批量检索目标文件转换接口
@app.route("/textrenameinterface/")
def textrenameinterface():
    app.logger.warning('fofa批量检索目标文件转换接口')
    user = session.get('username')
    if str(user) == usernameconfig:
        
        #dirsearchfilepath目录下的文本文件重命名为/TIP/flask_cnvd/file_txt/batchfofatarget.txt
        os.popen('mv /TIP/flask_cnvd/dirsearch/dirsearchfilepath/*.txt /TIP/flask_cnvd/file_txt/batchfofatarget.txt')
                
        return render_template('dirsearchscan.html')

    else:
        return render_template('login.html')


#dirsearch目录扫描文件上传
@app.route("/dirsearchfileupload/",methods=['post'])
def dirsearchfileupload():
    user = session.get('username')
    result = "上传结果："+" "+"成功"
    if str(user) == usernameconfig:
        app.logger.warning('目录扫描文件上传')
        try:
            file_dir = os.path.join(dirsearchdir, app.config['UPLOAD_FOLDER5'])
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)  
            f = request.files['file']  
            fname = f.filename
            f.save(os.path.join(file_dir, fname))
        except:
            pass
        #扫描状态，回显给前端。
        dir_status_list = "刷新查看服务状态"
        #vulmap漏洞扫描状态，回显给前端
        vulmap_status_list = "刷新查看服务状态"
        #httpx运行状态
        httpx_status_list = "刷新查看服务状态"

        #回显给前端的目标文件行数
        num = os.popen('bash /TIP/flask_cnvd/shellscript/killscan.sh dirsearchtargetnum').read()
        num11 = int(num) + 1 
        if num11 == 1:
            num11_1 = 0
        else:
            num11_1 = num11
        num_1 = "目标行数: "+" "+str(num11_1)

        #回显给前端的漏洞数量
        vuln_num = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapcount').read()
        vuln_num_int = int(vuln_num)
        if vuln_num_int == 0:
            vuln_num_int_1 = "漏洞数量："+"目前暂无漏洞"
        else:
            vuln_num_int_1 = "漏洞数量："+str(vuln_num_int)

        #回显给前端的目录扫描数量
        dirsearch_count_tmp = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh dirsearchscancount').read()
        if int(dirsearch_count_tmp) == -2:
            dirsearch_count = "目录数量（过滤前）："+"目前暂无漏洞"
        else:
            dirsearch_count = "目录数量（过滤前）："+str(dirsearch_count_tmp)

        #判断目录扫描漏洞数量是否有更新
        dirsearch_count_copy = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh dirsearchscancountcopy').read()

        #将str类型转为int类型进行比较大小
        dirsearch_count_tmp_int = int(dirsearch_count_tmp)
        dirsearch_count_copy_int = int(dirsearch_count_copy)
        if dirsearch_count_tmp_int > dirsearch_count_copy_int:
            dirsearch_data_judgment = "系统检测到有数据更新,点击原始数据同步更新数据"
        else:
            dirsearch_data_judgment = "目前暂无数据更新,有更新在点击原始数据同步更新"

        #目录扫描同步后的数量
        dirsearch_sync_value = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh dirsearchsyncresult').read()
        dirsearch_sync_value_result = "目录数量（过滤后）："+str(dirsearch_sync_value)

        #文件上传大小
        dirsearch_scan_file_size_1 = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh dirsearchscan_file_size').read()
        dirsearch_scan_file_size = "文件大小："+"  "+dirsearch_scan_file_size_1
    

        return render_template('dirsearchscan.html',datainfo = result,data5=dir_status_list,data7=num_1,data11=vulmap_status_list,data12=vuln_num_int_1,
        data13=dirsearch_count,data14=dirsearch_data_judgment,data15=httpx_status_list,data18=dirsearch_sync_value_result,data21=dirsearch_scan_file_size,
        data20=httpx_status_list,data19=httpx_status_list,data16=httpx_status_list)
    else:
        return render_template('login.html')




#删除dirsearch缓存
@app.route("/deletedirsearchcache/",methods=['get'])
def deletedirsearchcache():
    app.logger.warning('删除dirsearch缓存')
    try:
        os.popen('rm -rf /TIP/flask_cnvd/dirsearch/reports/*')
        os.popen('rm -rf /TIP/flask_cnvd/dirsearch/log/*')
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/dirsearchfile.txt')
        os.popen('touch /TIP/flask_cnvd/file_txt/dirsearchfile.txt')
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt')
        os.popen('touch /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt')
        
        #清空文件上传目录下的所有文件
        os.popen('rm -rf /TIP/flask_cnvd/dirsearch/dirsearchfilepath/*')

        return render_template('dirsearchscan.html')
    except:
        return render_template('error.html')




#目录扫描文件过滤状态码通过httpx
@app.route("/filterstatuscodebyhttpx/",methods=['post'])
def filterstatuscodebyhttpx():
    app.logger.warning('目录扫描文件过滤状态码通过httpx')
    user = session.get('username')
    statuscodename = request.form['statuscodename']

    if str(user) == usernameconfig:
        
        os.popen('bash /TIP/flask_cnvd/shellscript/run_httpx.sh'+''+' '+statuscodename)
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')



#目录扫描临时文件复制到目标文件
@app.route("/copydirsearchtmpinterface/")
def copydirsearchtmpinterface():
    app.logger.warning('目录扫描临时文件复制到目标文件')
    user = session.get('username')

    if str(user) == usernameconfig:
        
        os.popen('cp /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp.txt /TIP/flask_cnvd/file_txt/dirsearchtarget.txt')
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')





#域名检测接口
@app.route("/pingtestinterface/",methods=['post'])
def pingtestinterface():
    app.logger.warning('ping测试')
    user = session.get('username')
    pingvaluename = request.form['pingvaluename']

    if str(user) == usernameconfig:
        
        #域名反查IP
        ping_test_result_1 = os.popen('bash /TIP/flask_cnvd/shellscript/awkdirsearchfilter.sh ping_test'+' '+pingvaluename).read()
        ping_test_result_2 = ping_test_result_1.replace(":","")
        ping_test_result_3 = "IP："+ping_test_result_2
        if len(ping_test_result_1) == 1:
            ping_test_result_33 = "IP："+"主机禁ping，无法获取ip地址"
        else:
            ping_test_result_33 = ping_test_result_3
        global  ping_test_result
        ping_test_result = ping_test_result_33
        
        #IP归属地
        localtiondata_1 = os.popen('bash /TIP/flask_cnvd/shellscript/location.sh'+' '+ping_test_result_2).read()
        global localtiondata
        localtiondata = localtiondata_1

        #ICP备案信息查询
        url = "https://icp.chinaz.com/"
        hearder = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36',
                'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'
            }
        res = requests.get(url+pingvaluename,headers=hearder,allow_redirects=False)
        res.encoding = 'utf-8'
        soup=BeautifulSoup(res.text,'html.parser')
        soup_p = soup.find_all('p')
        soup_p_value = soup_p[10]
        soup_p_value_text = soup_p_value.text
        soup_p_value_text_11 = "公司名称："+soup_p_value_text
        global domainicpdata
        domainicpdata =  soup_p_value_text_11

        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')



#ping测试前端展示
@app.route("/pingtestinterfaceshow/",methods=['GET'])
def pingtestinterfaceshow():
    app.logger.warning('ping测试前端展示')
    global ping_test_result

    message_json = {
    "ping_value":ping_test_result,
    "local_value":localtiondata,
    "icp_value":domainicpdata
    }
    return jsonify(message_json)




#扫描前黑名单批量入库接口
@app.route("/scanbeforeinsertinterface/",methods=['POST'])
def scanbeforeinsertinterface():
    app.logger.warning('扫描前黑名单批量入库接口')
    user = session.get('username')
    if str(user) == usernameconfig:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum'])
        cur = db.cursor()

        urls = request.get_json()
        urls_re_list = []
        for url in urls:
            #从http://www.xx.com/1.html中匹配出www.xx.com
            pattern = r"https?://([^/]+)"
            urls_re_1 = re.search(pattern,url)
            urls_re = urls_re_1.group(1)
            urls_re_list.append(urls_re)

        #存取入库结果文件
        insert_data_list = []
        for j in urls_re_list:
            #检查是否存在相同数据
            sql_select = "select * from vuln_url_table where vulnurl = '%s' "%(j)
            cur.execute(sql_select)
            result = cur.fetchone()
            if result:
                url_value_result_11 = list(result)[1]
                #如果存在相同数据，返回当前查询到的一条数据回显给前端
                vuln_url_message1 = url_value_result_11+" "+"已存在，请不要重复进行入库操作"
                insert_data_list.append(vuln_url_message1)
                
            else:
                sql_insert = "insert into vuln_url_table(vulnurl) values('%s')"%(j)
                cur.execute(sql_insert)
                db.commit()
                vuln_url_message2 = "扫描前黑名单"+url_value_result_11+"已入库成功"
                insert_data_list.append(vuln_url_message2)
        
        global insert_data_list_result
        insert_data_list_result = insert_data_list

        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')


#扫描前黑名单批量入库接口结果回显给前端
@app.route("/scanbeforeinsertinterfacebyajax/",methods=['GET'])
def scanbeforeinsertinterfacebyajax():
    app.logger.warning('扫描前黑名单批量入库接口结果回显给前端')
    global insert_data_list_result

    message_json = {
    "insert_data_list_result":insert_data_list_result
    }
    return jsonify(message_json)
    


#扫描后黑名单批量入库接口
@app.route("/scanafterinsertinterface/",methods=['POST'])
def scanafterinsertinterface():
    app.logger.warning('扫描后黑名单批量入库接口')
    user = session.get('username')

    if str(user) == usernameconfig:
        #数据库连接信息
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum'])
        cur = db.cursor()
        #接收前端传入的json数据
        urls = request.get_json()
        urls_re_list = []
        for url in urls:
            #从http://www.xx.com/1.html中匹配出www.xx.com
            pattern = r"https?://([^/]+)"
            urls_re_1 = re.search(pattern,url)
            urls_re = urls_re_1.group(1)
            urls_re_list.append(urls_re)

        #存取入库结果文件
        insert_data_list = []
        for p in urls_re_list:
            #检查是否存在相同数据
            sql_select = "select * from blacklist_table where name = '%s' "%(p)
            cur.execute(sql_select)
            result = cur.fetchone()
            if result:
                url_value_result_11 = list(result)[1]
                #如果存在相同数据，返回当前查询到的一条数据回显给前端
                vuln_url_message1 = url_value_result_11+" "+"已存在，请不要重复进行入库操作"
                insert_data_list.append(vuln_url_message1)
                
            else:
                sql_insert = "insert into blacklist_table(name) values('%s')"%(p)
                cur.execute(sql_insert)
                db.commit()
                vuln_url_message2 = "扫描后黑名单"+url_value_result_11+"已入库成功"
                insert_data_list.append(vuln_url_message2)

        #定义全局变量用于前端在展示
        global insert_after_data_list_result
        insert_after_data_list_result = insert_data_list

        #生成文件用于过滤扫描结果
        sql1 = "select name from blacklist_table order by id desc"
        cur.execute(sql1)
        data1 = cur.fetchall()
        f = open(file='/TIP/flask_cnvd/file_txt/filterdirsearch.txt', mode='w')
        for ii in list(data1):
            for jj in ii:
                f.write(str(jj)+"\n")

        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')


#扫描后黑名单批量入库接口结果回显给前端
@app.route("/scanafterinsertinterfacebyajax/",methods=['GET'])
def scanafterinsertinterfacebyajax():
    app.logger.warning('扫描后黑名单批量入库接口结果回显给前端')
    global insert_after_data_list_result

    message_json = {
    "insert_after_data_list_result":insert_after_data_list_result
    }
    return jsonify(message_json)



#目录扫描通过配置文件中白名单检索文件接口
@app.route("/dirscanbyconfigwhiteinterface/",methods=['get'])
def dirscanbyconfigwhiteinterface():
    app.logger.warning('目录扫描通过配置文件中白名单检索文件接口')
    user = session.get('username')
    if str(user) == usernameconfig:
        white_result_list = []
        for i in dirscanwhite:
            result = os.popen('bash /TIP/flask_cnvd/shellscript/filterdirsearchdata.sh dirscan_white'+' '+i+'').read()
            white_result_list.append(result)

        #将white_result_list列表写入到dirsearchtarget.txt文件中
        f = open(file='/TIP/flask_cnvd/file_txt/dirsearchtarget.txt',mode='w')
        for j in white_result_list:
            f.write(str(j))

        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')


#----------------------------------------dirsearch目录扫描模块------------------------------------------------#


#----------------------------------------Nuclei扫描模块-------------------------------------------------------#
#nuclei扫描结果文件预览
@app.route("/nucleifileshowinterface/")
def nucleifileshowinterface():
    app.logger.warning('nuclei扫描结果文件预览')
    user = session.get('username')
    if str(user) == usernameconfig:
        lines = []
        with open('/TIP/flask_cnvd/file_txt/nucleiresult.txt', 'r') as f:
            for line in f:
                lines.append(line.strip())
        #文件结果优化展示
        liness = []
        for line1 in lines:
            line2 = line1.replace("[0m]","     ")
            line3 = line2.replace("[[92m","    ")
            line4 = line3.replace("[[94m","    ")
            line5 = line4.replace("[[34m","    ")
            line6 = line5.replace("[[96m","    ")
            line7 = line6.replace("[0m,","     ")
            
            liness.append(line7)
        return '<br>'.join(liness)
    else:
        return render_template('login.html')
    
#Nuclei模板文件查看
@app.route("/templatenucleishowinterface/",methods=['post'])
def templatenucleishowinterface():
    app.logger.warning('Nuclei模板文件查看')
    user = session.get('username')
    oper_nucleu_value_name = request.form['oper_nucleu_value_name']
    
    if str(user) == usernameconfig:
        nuclei_result = os.popen('bash /TIP/flask_cnvd/shellscript/nuclei_program.sh templatenuclei'+''+' '+oper_nucleu_value_name).read()
        nuclei_result_lines = nuclei_result.splitlines()
        nuclei_result_list = []
        global nuclei_result_list_1
        nuclei_result_list_1 = nuclei_result_list
        for i in nuclei_result_lines:
            nuclei_result_list.append(i)
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')


#Nuclei模板文件查看回显给前端
@app.route("/templatenucleishowbyajaxinterface/",methods=['GET'])
def templatenucleishowbyajaxinterface():
    app.logger.warning('Nuclei模板文件查看回显给前端')
    user = session.get('username')
    if str(user) == usernameconfig:
        global nuclei_result_list_1
        message_json = {
        "nuclei_result_list_1":nuclei_result_list_1,
        "nuclei_length":"模板数量: "+str(len(nuclei_result_list_1))
        }
        return jsonify(message_json)
    
    else:
        return render_template('login.html')


#Nuclei启动接口
@app.route("/startnucleiinterface/",methods=['POST'])
def startnucleiinterface():
    app.logger.warning('Nuclei启动接口')
    user = session.get('username')
    nucleu_value_name = request.form['nucleu_value_name']
    if str(user) == usernameconfig:
        os.popen('bash /TIP/flask_cnvd/shellscript/nuclei_program.sh startnuclei'+''+' '+nucleu_value_name)

        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')


#关闭nuclei进程
@app.route("/stopnucleiprocessinterface/")
def stopnucleiprocessinterface():
    app.logger.warning('关闭nuclei进程')
    user = session.get('username')
    if str(user) == usernameconfig:

        os.popen('bash /TIP/flask_cnvd/shellscript/killscan.sh killnuclei')
        return render_template('dirsearchscan.html')

    else:
        return render_template('login.html')
#----------------------------------------Nuclei扫描模块-------------------------------------------------------#


#----------------------------------------vulmap漏洞扫描模块------------------------------------------------#
#vulmap漏洞扫描指令下发接口
@app.route("/vulmapscaninterface/",methods=['post'])
def vulmapscaninterface():
    app.logger.warning('vulmap漏洞扫描指令下发接口')
    user = session.get('username')
    component_value = request.form['component_value']
    timeout_value = request.form['timeout_value']
    delaytime_value = request.form['delaytime_value']
    thread_value = request.form['thread_value']
    if str(user) == usernameconfig:

        os.popen('bash /TIP/flask_cnvd/shellscript/vulmapscan.sh'+' '+component_value+' '+timeout_value+' '+delaytime_value+' '+thread_value)
        return render_template('dirsearchscan.html')

    else:
        return render_template('login.html')


#vulmap扫描报告下载
@app.route("/vulmapscanreportdown/")
def vulmapscanreportdown():
    app.logger.warning('vulmap扫描报告下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/file_txt/vulmapscanresult.txt',directory ='/TIP/flask_cnvd/file_txt',filename="vulmapscanresult.txt",as_attachment=True)
    else:
        return render_template('login.html')


#vulmap漏洞扫描清空缓存
@app.route("/vulmapscanclearcacheinterface/")
def vulmapscanclearcacheinterface():
    app.logger.warning('vulmap漏洞扫描清空缓存')
    user = session.get('username')
    if str(user) == usernameconfig:

        os.popen('rm -rf /TIP/flask_cnvd/file_txt/vulmapscanresult_tmp.txt')
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/vulmapscanresult.txt')
        return render_template('dirsearchscan.html')

    else:
        return render_template('login.html')


#目录漏洞扫描目标清空
@app.route("/cleardirvulmaptarget/")
def cleardirvulmaptarget():
    app.logger.warning('目录漏洞扫描目标清空')
    user = session.get('username')
    if str(user) == usernameconfig:

        os.popen('rm -rf /TIP/flask_cnvd/file_txt/dirsearchtarget.txt')
        os.popen('touch /TIP/flask_cnvd/file_txt/dirsearchtarget.txt')
        os.popen('rm -rf /TIP/flask_cnvd/dirsearch/dirsearchfilepath/*')
        os.popen('rm -rf /TIP/flask_cnvd/dirsearch/dirsearch.log')
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_1.txt')
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_2.txt')
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/dirsearchtarge_tmp_3.txt')
        return render_template('dirsearchscan.html')

    else:
        return render_template('login.html')



#后台kill vulmap扫描进程
@app.route("/killvulmapscanprocess/")
def killvulmapscanprocess():
    app.logger.warning('后台kill vulmap扫描进程')
    user = session.get('username')
    if str(user) == usernameconfig:

        os.popen('bash /TIP/flask_cnvd/shellscript/killscan.sh killvulmap')
        return render_template('dirsearchscan.html')

    else:
        return render_template('login.html')


#vulmap漏洞扫描数据过滤接口
@app.route("/filtervulmapinterface/",methods=['post'])
def filtervulmapinterface():
    app.logger.warning('vulmap漏洞扫描数据过滤接口')
    user = session.get('username')

    vulmapvalue = request.form['vulmapvalue']
    vulmapvalue1 = request.form['vulmapvalue1']
    if str(user) == usernameconfig:
        
        os.popen('bash /TIP/flask_cnvd/shellscript/filtervulmapdata.sh'+''+' '+vulmapvalue+''+' '+vulmapvalue1)
        return render_template('dirsearchscan.html')
    else:
        return render_template('login.html')



#vulmap扫描过滤报告下载
@app.route("/vulmapscanreportfilterdown/")
def vulmapscanreportfilterdown():
    app.logger.warning('vulmap扫描过滤报告下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/file_txt/vulmapscanfilterresult.txt',directory ='/TIP/flask_cnvd/file_txt',filename="vulmapscanfilterresult.txt",as_attachment=True)
    else:
        return render_template('login.html')



#vulmap漏洞数量展示
@app.route("/vulmapcountshowinterface/")
def vulmapcountshowinterface():
    app.logger.warning('vulmap漏洞数量展示')
    user = session.get('username')

    if str(user) == usernameconfig:
        activemq = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapactivemqcount').read()
        flink = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapflinkcount').read()
        shiro = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapshirocount').read()
        solr = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapsolrcount').read()
        struts2 = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapstruts2count').read()
        tomcat = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmaptomcatcount').read()
        unomi = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapunomicount').read()
        drupal = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapdrupalcount').read()
        elasticsearch = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapelasticsearchcount').read()
        fastjson = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapfastjsoncount').read()
        jenkins = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapjenkinscount').read()
        laravel = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmaplaravelcount').read()
        nexus = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapnexuscount').read()
        weblogic = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapweblogiccount').read()
        jboss = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapjbosscount').read()
        spring = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapspringcount').read()
        thinkphp = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapthinkphpcount').read()
        druid = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapdruidcount').read()
        exchange = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapexchangecount').read()
        nodejs = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapnodejscount').read()
        saltstack = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapsaltstackcount').read()
        vmware = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapvmwarecount').read()
        bigip = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapbigipcount').read()
        ofbiz = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapofbizcount').read()
        coremail = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapcoremailcount').read()
        ecology = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapecologycount').read()
        eyou = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapeyoucount').read()
        qianxin = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapqianxincount').read()
        ruijie = os.popen('bash /TIP/flask_cnvd/shellscript/num_count.sh vulmapruijiecount').read()
        message_json = {
        "activemq":"activemq: "+activemq,
        "flink":"flink: "+flink,
        "shiro":"shiro: "+shiro,
        "solr":"solr: "+solr,
        "struts2":"struts2: "+struts2,
        "tomcat":"tomcat: "+tomcat,
        "unomi":"unomi: "+unomi,
        "drupal":"drupal: "+drupal,
        "elasticsearch":"elasticsearch: "+elasticsearch,
        "fastjson":"fastjson: "+fastjson,
        "jenkins":"jenkins: "+jenkins,
        "laravel":"laravel: "+laravel,
        "nexus":"nexus: "+nexus,
        "weblogic":"weblogic: "+weblogic,
        "jboss":"jboss: "+jboss,
        "spring":"spring: "+spring,
        "thinkphp":"thinkphp: "+thinkphp,
        "druid":"druid: "+druid,
        "exchange":"exchange: "+exchange,
        "nodejs":"nodejs: "+nodejs,
        "saltstack":"saltstack: "+saltstack,
        "vmware":"vmware: "+vmware,
        "bigip":"bigip: "+bigip,
        "ofbiz":"ofbiz: "+ofbiz,
        "coremail":"coremail: "+coremail,
        "ecology":"ecology: "+ecology,
        "eyou":"eyou: "+eyou,
        "qianxin":"qianxin: "+qianxin,
        "ruijie":"ruijie: "+ruijie

        }
        return jsonify(message_json)
    else:
        return render_template('login.html')



#vulmap漏洞前端展示
@app.route("/vulmapvulndisplayinterface/")
def vulmapvulndisplayinterface():
    app.logger.warning('vulmap漏洞前端展示')
    user = session.get('username')

    if str(user) == usernameconfig:
        #定义列表用于存储过滤后的漏洞
        vuln_list = []
        vuln_file = open("/TIP/flask_cnvd/file_txt/vulmapscanfilterresult.txt",encoding='utf-8')
        for line in vuln_file.readlines():
            vuln_list.append(line)
        message_json = {
            "eventName":vuln_list
        }
        return jsonify(message_json)
    else:
        return render_template('login.html')


#----------------------------------------vulmap漏洞扫描模块------------------------------------------------#





#----------------------------------------主机存活探测扫描模块------------------------------------------------#
#跳转到存活主机探测界面
@app.route("/ipsurvive/")
def ipsurvive():
    app.logger.warning('跳转到存活主机探测页面')
    user = session.get('username')
    if str(user) == usernameconfig:
        os.popen('rm -rf /TIP/flask_cnvd/ipupload/*')
        os.popen('rm -rf /TIP/flask_cnvd/samplesurvive/survive.txt')
        os.popen('rm -rf /TIP/flask_cnvd/samplesurvive/surviveresult.txt')
        os.popen('rm -rf /TIP/flask_cnvd/samplesurvive/survivequchong.txt')
        return render_template('ipsurvive.html')
    else:
        return render_template('login.html')


#批量探测存活主机
@app.route("/ipsurvivefunction/",methods=['POST'])
def ipsurvivefunction():
    app.logger.warning('批量探测存活主机')

    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER4'])  # 拼接成合法文件夹地址
    if not os.path.exists(file_dir):
    #文件夹不存在就创建
        os.makedirs(file_dir)  
    #从表单的file字段获取文件，file为该表单的name值
    f = request.files['file']  
    fname = f.filename
    f.save(os.path.join(file_dir, fname))  # 保存文件到upload目录
    os.popen('mv /TIP/flask_cnvd/ipupload/* /TIP/flask_cnvd/samplesurvive/survive.txt')
    os.popen('bash /TIP/flask_cnvd/shellscript/quchong.sh')
    os.popen('bash /TIP/flask_cnvd/shellscript/ipsurvive.sh')
    result_list = []
    ip_file = open("/TIP/flask_cnvd/samplesurvive/surviveresult.txt",encoding='utf-8')
    ip_num = os.popen('bash /TIP/flask_cnvd/shellscript/ipnum.sh').read()
    ip_num_1 = os.popen('bash /TIP/flask_cnvd/shellscript/ipnum_1.sh').read()
    totalsize_1 = os.popen('du -sh /TIP/flask_cnvd/samplesurvive/survive.txt').read()
    totalsize = totalsize_1.replace("/TIP/flask_cnvd/samplesurvive/survive.txt","")
    quchongsize_1 = os.popen('du -sh /TIP/flask_cnvd/samplesurvive/surviveresult.txt').read()
    quchongsize = quchongsize_1.replace("/TIP/flask_cnvd/samplesurvive/surviveresult.txt","")
    for line in ip_file.readlines():
        result_list.append(line)
    return render_template('ipsurvive.html',data=result_list,data1=ip_num,data2=ip_num_1,data3=totalsize,data4=quchongsize)


#存活主机列表文件下载功能
@app.route("/filedownload/")
def filedownload():
    app.logger.warning('存活主机文件下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/samplesurvive/surviveresult.txt',directory ='/TIP/flask_cnvd/samplesurvive',filename="surviveresult.txt",as_attachment=True)
    else:
        return render_template('login.html')
#----------------------------------------主机存活探测扫描模块------------------------------------------------#




#----------------------------------------字典生成模块------------------------------------------------#
#跳转到字典生成界面
@app.route("/dicgenerate/")
def dicgenerate():
    
    app.logger.warning('跳转到字典生成界面')
    user = session.get('username')
    
    if str(user) == usernameconfig:
        try:
            return render_template('dictionary.html')
        except:
            pass

    else:
        return render_template('login.html')


#字典生成功能
@app.route("/dicgeneratefunc/",methods=['post'])
def dicgeneratefunc():
    app.logger.warning('字典生成功能实现')
    start = request.form['start']
    end = request.form['end']
    namestr = request.form['namestr']
    oper = request.form['oper']
    try:
        if oper == str(1):
            os.popen('bash /TIP/flask_cnvd/shellscript/crunch.sh moren'+''+' '+start+''+' '+end+''+' '+namestr+'')
            result_list = "任务已下发,请稍等..."
            return render_template('dictionary.html',data=result_list)
        elif oper == str(2):
            os.popen('bash /TIP/flask_cnvd/shellscript/crunch.sh zidingyi'+''+' '+start+''+' '+end+''+' '+namestr+'')
            result_list = "任务已下发,请稍等..."
            return render_template('dictionary.html',data=result_list)
        else:
            result = "功能开发中......"
            return render_template('dictionary.html',data=result)
    except:
        pass



#字典文件下载
@app.route("/diccdownload/",methods=['post'])
def diccdownload():
    app.logger.warning('字典文件下载')
    user = session.get('username')
    if str(user) == usernameconfig:
        return send_from_directory(path = '/TIP/flask_cnvd/file_txt/dicc.txt',directory ='/TIP/flask_cnvd/file_txt',filename="dicc.txt",as_attachment=True)
    else:
        return render_template('login.html')
#----------------------------------------字典生成模块------------------------------------------------#





#----------------------------------------DNS解析模块------------------------------------------------#
#跳转到DNS解析记录页面
@app.route("/dns/")
def dns():
    app.logger.warning('跳转到DNS解析记录页面')
    user = session.get('username')
    if str(user) == usernameconfig:
        return render_template('dns.html')
    else:
        return render_template('login.html')


#DNS解析记录功能实现
@app.route("/dnsrelas/",methods=['post'])
def dnsrelas():
    
    app.logger.warning('DNS解析记录功能实现')
    domain1=request.form['domain']
    domain = domain1.replace("www.","")
    oper = request.form['oper']
    dataa = "为查询到域名"+domain+"相关的DNS解析记录!!!"
    try:
        if oper == str(1):
            A_out = os.popen('nslookup -q=a'+' '+domain).read()
            A_out_1 = "域名:"+domain+"的A记录如下----->"+A_out
            return render_template('dns.html',data=str(A_out_1),data2=str(domain))
        elif oper == str(2):
            CAA_out = os.popen('nslookup -q=caa'+' '+domain).read()
            CAA_out_1 = "域名:"+domain+"的CAA记录如下----->"+CAA_out
            return render_template('dns.html',data=str(CAA_out_1),data2=str(domain))
        elif oper == str(3):
            NS_out = os.popen('nslookup -q=ns'+' '+domain).read()
            NS_out_1 = "域名:"+domain+"的NS记录如下----->"+NS_out
            return render_template('dns.html',data=str(NS_out_1),data2=str(domain))
        elif oper == str(4):
            CNAME_out = os.popen('nslookup -q=cname'+' '+domain).read()
            CNAME_out_1 = "域名:"+domain+"的CNAME记录如下----->"+CNAME_out
            return render_template('dns.html',data=str(CNAME_out_1),data2=str(domain))
        elif oper == str(5):
            TXT_out =  os.popen('nslookup -q=txt'+' '+domain).read()
            TXT_out_1 = "域名:"+domain+"的TXT记录如下----->"+TXT_out
            return render_template('dns.html',data=str(TXT_out_1),data2=str(domain))
        elif oper == str(6):
            MX_out = os.popen('nslookup -q=mx'+' '+domain).read()
            MX_out_1 = "域名:"+domain+"的MX记录如下----->"+MX_out
            return render_template('dns.html',data=str(MX_out_1),data2=str(domain))
        elif oper == str(7):
            AAAA_out = os.popen('nslookup -q=aaaa'+' '+domain).read()
            AAAA_out_1 = "域名:"+domain+"的AAAA记录如下----->"+AAAA_out
            return render_template('dns.html',data=str(AAAA_out_1),data2=str(domain))
        else:
            return render_template('dns.html',data=dataa,data2=str(domain))
    except:
        return render_template('dns.html',data=dataa,data2=str(domain))
#----------------------------------------DNS解析模块------------------------------------------------#





#----------------------------------------书签栏模块------------------------------------------------#
#跳转到超链接界面
@app.route("/bookmarks/")
def bookmarks():
    app.logger.warning('跳转到超链接界面')
    user = session.get('username')
    datainfo="数据库未开启,请联系管理员!!!"
    if str(user) == usernameconfig:
        try:
            now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
            ip = request.remote_addr
            locate_1 = os.popen('bash /TIP/flask_cnvd/shellscript/location.sh'+''+' '+ip+'').read()
            locate_11 = locate_1.replace("地址","")
            locate = locate_11.replace(":","")
            now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
            #存入MySQL数据库
            db= pymysql.connect(host=dict['ip'],user=dict['username'],  
            password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
            now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
            cur = db.cursor()
            #IP和IP属地存库
            sql_insert = "insert into ip_table(ip,locate,nowdate,user) values('%s','%s','%s','%s')" %(ip,locate,now,user)
            cur.execute(sql_insert)
            #刷新浏览器一次数据库num_count字段+1
            #sql = "UPDATE count_table SET num_count = num_count + 1 where id = 1"
            #cur.execute(sql)
            db.commit()
            db.rollback()

            #访问次数
            sql_select="SELECT num_count from count_table"
            cur.execute(sql_select)
            num_data = cur.fetchall()
            
            #标题栏CDN识别
            sql_CDN="SELECT url1,name,id,level FROM book_table where logo = 1 ORDER BY level DESC"
            cur.execute(sql_CDN)
            sql_CDN_data=cur.fetchall()


            #标题栏子域名
            sql_domain="SELECT url1,name,id,level FROM book_table where logo = 2 ORDER BY level DESC"
            cur.execute(sql_domain)
            sql_domain_data=cur.fetchall()

            #标题栏指纹识别
            sql_finger="SELECT url1,name,id,level FROM book_table where logo = 3 ORDER BY level DESC"
            cur.execute(sql_finger)
            sql_finger_data=cur.fetchall()

        

            #标题栏网络空间
            sql_space="SELECT url1,name,id,level FROM book_table where logo = 4 ORDER BY level DESC"
            cur.execute(sql_space)
            sql_space_data=cur.fetchall()

            #标题栏综合搜索
            sql_zonghe="SELECT url1,name,id,level FROM book_table where logo = 5 ORDER BY level DESC"
            cur.execute(sql_zonghe)
            sql_zonghe_data=cur.fetchall()

            #标题栏威胁情报
            sql_weixieqingbao="SELECT url1,name,id,level FROM book_table where logo = 6 ORDER BY level DESC"
            cur.execute(sql_weixieqingbao)
            sql_weixieqingbao_data=cur.fetchall()

            #标题栏靶场环境
            sql_bachang="SELECT url1,name,id,level FROM book_table where logo = 7 ORDER BY level DESC"
            cur.execute(sql_bachang)
            sql_bachang_data=cur.fetchall()

            #标题栏解密
            sql_jiemi="SELECT url1,name,id,level FROM book_table where logo = 8 ORDER BY level DESC"
            cur.execute(sql_jiemi)
            sql_jiemi_data=cur.fetchall()

            #标题栏SRC
            sql_src="SELECT url1,name,id,level FROM book_table where logo = 9 ORDER BY level DESC"
            cur.execute(sql_src)
            sql_src_data=cur.fetchall()

            #标题栏技术文章
            sql_wenzhang="SELECT url1,name,id,level FROM book_table where logo = 10 ORDER BY level DESC"
            cur.execute(sql_wenzhang)
            sql_wenzhang_data=cur.fetchall()

            #标题栏溯源
            sql_suyuan="SELECT url1,name,id,level FROM book_table where logo = 11 ORDER BY level DESC"
            cur.execute(sql_suyuan)
            sql_suyuan_data=cur.fetchall()

            return render_template('bookmarks.html',data=now,data1=locate,data2=ip,data3=num_data,data4=sql_CDN_data,
            data5=sql_domain_data,data6=sql_finger_data,data7=sql_space_data,data8=sql_zonghe_data,data9=sql_weixieqingbao_data,
            data10=sql_bachang_data,data11=sql_jiemi_data,data12=sql_src_data,data13=sql_wenzhang_data,data14=sql_suyuan_data)
        except:
            return render_template('error.html',data=datainfo)
    else:
        return render_template('login.html')


#添加书签
@app.route('/addbookmarks/',methods=['POST'])
def addbookmarks():
    
    app.logger.warning('添加书签')
    try:

        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
        cur = db.cursor()
        url=request.form['url']
        urlname=request.form['urlname']
        titleoper=request.form['titleoper']
       
        sql_insertt = "insert into book_table(url1,name,logo,level) values('%s','%s','%s','%s')" %(url,urlname,titleoper,0)
        cur.execute(sql_insertt)
        db.commit()
        db.rollback()
        return redirect("/bookmarks/")
    except:
        pass


#根据ID删除书签
@app.route("/deletebookmarks/",methods=['get'])

def deletebookmarks():
    
    app.logger.warning('通过ID删除书签')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        id = request.args['id']
        sql="delete from book_table where id = '%s' " %(id)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return redirect("/bookmarks/")
    except:
        pass

#书签恢复默认排序
@app.route("/updatebookmarks/",methods=['post'])

def updatebookmarks():
    
    app.logger.warning('书签恢复默认排序')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql = "UPDATE book_table set level = 0"
        cur.execute(sql)
        db.commit()
        db.rollback()
        return redirect("/bookmarks/")
    except:
        pass

#level字段-1
@app.route("/updatebookmarkssubtraction/",methods=['get'])
def updatebookmarkssubtraction():
    
    app.logger.warning('书签排序后退')
    id = request.args['id']
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql = "UPDATE book_table SET level = level - 1 where id = '%s' "%(id)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return redirect("/bookmarks/")
    except:
        pass

#level字段+1
@app.route("/updatebookmarksadd/",methods=['get'])
def updatebookmarksadd():
    
    app.logger.warning('书签排序前进')
    id = request.args['id']
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql = "UPDATE book_table SET level = level + 1 where id = '%s' "%(id)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return redirect("/bookmarks/")
    except:
        pass
#----------------------------------------书签栏模块------------------------------------------------#





 #----------------------------------------IP反查域名模块------------------------------------------------#

#跳转到IP反查域名界面
@app.route("/ipcheckdomain/")
def ipcheckdomain():
    
    app.logger.warning('跳转到IP反查域名界面')
    user = session.get('username')
    if str(user) == usernameconfig:
        return render_template('ipcheckdomain.html')
    else:
        return render_template('login.html')
    


#IP反查域名调用fofa接口和IP138接口
@app.route("/ipcheckdomaindemo/",methods=['post'])
def ipcheckdomaindemo():
    
    app.logger.warning('IP反查域名调用fofa接口和IP138接口')
    oper = request.form['oper']
    ip=request.form['ip']
    dataaa = ["未查询到"+ip+"相关的域名!!!"]
    if oper == str(1):
        try:
            part1=ip.encode('utf-8')
            partbase64=base64.b64encode(part1)
            str1=str(partbase64,'utf-8')
            url = "https://fofa.info/api/v1/search/all?email=weakchicken@qq.com&key="+fofakey+"&size=2000&qbase64="
            hearder={
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            }
            res = requests.get(url+str1,headers=hearder,allow_redirects=False)
            res.encoding='utf-8'
            restext = res.text
            resdic=json.loads(restext)
            resdicresult=resdic['results']
            ip_domain_list = []
            for i in resdicresult:
                ip_domain_list.append(i[0])
            if len(resdicresult) == 0:
                return render_template('ipcheckdomain.html',data="未查询到域名相关信息!",data2=str(ip))
            else:
                return render_template('ipcheckdomain.html',data=ip_domain_list,data2=str(ip))
        except:
            return render_template('ipcheckdomain.html',data=dataaa)
    elif oper == str(2):
        try:
            url="https://site.ip138.com/"
            headers={
            'Cookie':'Hm_lvt_ecdd6f3afaa488ece3938bcdbb89e8da=1615729527; Hm_lvt_d39191a0b09bb1eb023933edaa468cd5=1617883004,1617934903,1618052897,1618228943; Hm_lpvt_d39191a0b09bb1eb023933edaa468cd5=1618567746',
            'Host':'site.ip138.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
        }
            res=requests.get(url+ip,headers=headers,allow_redirects=False)
            res.encoding='utf-8'
            soup=BeautifulSoup(res.text,'html.parser')
            tag2=soup.find('ul',id="list")
            tag2_a = tag2.find_all('a')
            ip138_domain_list = []
            for j in tag2_a:
                ip138_domain_list.append(j.text)
            return render_template('ipcheckdomain.html',data=ip138_domain_list,data2=str(ip))
        except:
            return render_template('ipcheckdomain.html',data=dataaa)
 #----------------------------------------IP反查域名模块------------------------------------------------#



#----------------------------------------shodan扫描模块------------------------------------------------#
#跳转到端口探测界面
@app.route("/portscan/")
def portscan():
    app.logger.warning('跳转到端口探测界面')
    user = session.get('username')
    if str(user) == usernameconfig:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql="SELECT ip FROM ipbasic_table ORDER BY id DESC LIMIT 0,5"
        cur.execute(sql)
        data = cur.fetchall()
        return render_template('port.html',data1=data)
    else:
        return render_template('login.html')


#shodanIP基础信息查询
@app.route("/portscanfunction/",methods=['post'])
def portscanfunction():
    try:
        app.logger.warning('shodanIP基础信息查询')
        oper = request.form['oper']
        ip = request.form['ip']
        if oper == str(2):
            #IP定位
            try:
                data = "未查询到IP"+ip+"相关的端口信息!!!"
                apis = shodan.Shodan(shodankey)
                result=apis.host(ip)
                results1 = apis.search("http.title:\"黑龙江\" ")
                
                dict_list = []
                for i in results1['matches']:
                    dict_list.append(i['http'])
                
                dict_list_result = []
                try:
                    for j in dict_list:
                        dict_list_result.append(j['favicon'])
                except:
                    pass

                try:
                    for k in dict_list_result:
                        print(k['location'])
                except:
                    pass
                resultdata0 = result['ports']
                resultdata1 = str(resultdata0).replace("[","")
                resultdata = str(resultdata1).replace("]","")
                hostname0 = result['hostnames']
                hostname1 = str(hostname0).replace("['","")
                hostname = str(hostname1).replace("']","")
                ASN = result['asn']
                city = result['city']
                ISP = result['isp']
                updatetime = result['last_update']

                db= pymysql.connect(host=dict['ip'],user=dict['username'],  
                password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
                cur = db.cursor()
                sql="SELECT ip FROM ipbasic_table ORDER BY id DESC LIMIT 0,5"
                cur.execute(sql)
                data1 = cur.fetchall()
                return render_template('port.html',data2=str(ip),data3=str(ip),data=str(resultdata),data4=str(hostname),data5=str(ASN),data6=str(city),data7=str(ISP),data8=str(updatetime),data1=data1)
            except:
                return render_template('port.html',data2=str(ip),data3=str(ip),data=str(resultdata),data4=str(hostname),data5=str(ASN),data6=str(city),data7=str(ISP),data8=str(updatetime),data1=data1)
        elif oper == str(1):
            try:
                db= pymysql.connect(host=dict['ip'],user=dict['username'],  
                password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
                cur = db.cursor()
                sql="select distinct ip,port,ASN,city,ISP,updatetime,zhujiname from ipbasic_table where ip = '%s' "%(ip)
                cur.execute(sql)
                data = cur.fetchall()

                sql1="SELECT ip,id FROM ipbasic_table ORDER BY id DESC LIMIT 0,5"
                cur.execute(sql1)
                data1 = cur.fetchall()
                return render_template('port.html',data23=data,data2=str(ip),data1=data1)
            except:
                return render_template('port.html',data23=data,data2=str(ip),data1=data1)

        else:
            return render_template('port.html')
    except:
        pass


#IP基础信息存入数据库
@app.route("/addbasicinformation/",methods=['post'])
def addbasicinformation():
    
    app.logger.warning('IP基础信息存入数据库') 
    try:

        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        ip = request.form['ip']
        port = request.form['port']
        
        asn = request.form['asn']
        city = request.form['city']
        isp = request.form['isp']
        updatetime = request.form['updatetime']
        zhujiname = request.form['zhujiname']
        sql_insert = "insert ignore into ipbasic_table(ip,port,asn,city,isp,updatetime,zhujiname)  values('%s','%s','%s','%s','%s','%s','%s')" %(ip,port,asn,city,isp,updatetime,zhujiname)
        cur.execute(sql_insert)  
        db.commit()
        db.rollback()
        return render_template('port.html')
    except:
        return render_template('error.html')



#根据ID删除shodan最近缓存记录
@app.route("/deleteshodandata/",methods=['get'])
def deleteshodandata():
    app.logger.warning('通过ID删除shodan最近缓存记录')
    try:
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        id = request.args['id']
        sql="delete from ipbasic_table where id = '%s' " %(id)
        cur.execute(sql)
        db.commit()
        db.rollback()
        return redirect("/portscan/")
    except:
        pass
#----------------------------------------shodan扫描模块------------------------------------------------#




#----------------------------------------nmap端口扫描模块------------------------------------------------#
#跳转到nmap端口扫描
@app.route("/nmapportscan/")
def nmapportscan():
    app.logger.warning('跳转到nmap端口扫描界面')
    user = session.get('username')
    if str(user) == usernameconfig:
        nmap_file = open('/TIP/flask_cnvd/file_txt/nmap.txt',encoding='utf-8')
        nmap_list = []
        for line in nmap_file.readlines():
            nmap_list.append(line)
            
        nmap_status_list = os.popen('bash /TIP/flask_cnvd/shellscript/scannerstatus.sh nmapstatus').read()
        
        return render_template('nmapportscan.html',data=nmap_list,data5=nmap_status_list)
    else:
        return render_template('login.html')

#namp扫描端口实现
@app.route("/nmapportscanfun/",methods=['post'])
def nmapportscanfun():
    app.logger.warning('nmap端口扫描实现')
    user = session.get('username')
    ip = request.form['ip']
    operrate = request.form['operrate']
    operport = request.form['operport']
    if str(user) == usernameconfig:
        os.popen('bash /TIP/flask_cnvd/shellscript/nmap.sh'+''+' '+ip+''+' '+operport+''+' '+operrate+'')
        return render_template('nmapportscan.html')
    else:
        return render_template('login.html')



#后台结束nmap扫描器进程
@app.route("/killnmap/",methods=['post'])
def killnmap():
    app.logger.warning('后台结束nmap扫描器进程')
    user = session.get('username')
    if str(user) == usernameconfig:
        os.popen('bash /TIP/flask_cnvd/shellscript/killscan.sh killnmap')
        return render_template('nmapportscan.html')
    else:
        return render_template('login.html')


#删除nmap扫描数据
@app.route("/clearnmapdata/",methods=['post'])
def clearnmapdata():
    app.logger.warning('删除nmap扫描数据')
    user = session.get('username')
    if str(user) == usernameconfig:
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/nmap.txt')
        os.popen('touch /TIP/flask_cnvd/file_txt/nmap.txt')
        return render_template('nmapportscan.html')
    else:
        return render_template('login.html')


#nmap扫描结果同步
@app.route("/copynmapdata/",methods=['post'])
def copynmapdata():
    app.logger.warning('nmap扫描结果同步')
    user = session.get('username')
    if str(user) == usernameconfig:
        os.popen('cp /TIP/flask_cnvd/file_txt/nmap_tmp.txt /TIP/flask_cnvd/file_txt/nmap.txt')
        return render_template('nmapportscan.html')
    else:
        return render_template('login.html')



#过滤nmap扫描结果
@app.route("/filternmapresult/",methods=['get'])
def filternmapresult():
    app.logger.warning('过滤nmap扫描结果')
    user = session.get('username')
    if str(user) == usernameconfig:
        opername = request.args['opername']
        os.popen('bash /TIP/flask_cnvd/shellscript/filternmapdata.sh'+' '+opername)
        return render_template('nmapportscan.html')
    else:
        return render_template('login.html')

#----------------------------------------nmap端口扫描模块------------------------------------------------#




#----------------------------------------监控平台模块------------------------------------------------#
#跳转到ARL资产探测平台
@app.route("/platform/")
def platform():

    app.logger.warning('跳转到ARL资产探测平台')
    user = session.get('username')
    adata1 = arlurl
    adata2 = arluserpass
    gdata1 =  githuburl
    gdata2 = githubpass
    if str(user) == usernameconfig:

        arlresultcount = os.popen('bash /TIP/flask_cnvd/shellscript/githubmonplatform.sh statusarl').read()
        githubresultcount = os.popen('bash /TIP/flask_cnvd/shellscript/githubmonplatform.sh statusgithubplatform').read()
        return render_template('platform.html',adata=arlresultcount,adata1=adata1,adata2=adata2,gdata=githubresultcount,
        gdata1=gdata1,gdata2=gdata2)
    else:
        return render_template('login.html')



#启动ARL资产探测平台
@app.route("/startarlplatforminterface/")
def startarlplatforminterface():
    
    app.logger.warning('启动ARL资产探测平台')
    user = session.get('username')
    
    if str(user) == usernameconfig:

        os.popen('bash /TIP/flask_cnvd/shellscript/githubmonplatform.sh startarl')

        return render_template('platform.html')
    else:
        return render_template('login.html')



#启动github监控平台
@app.route("/startgithubplatforminterface/")
def startgithubplatforminterface():
    
    app.logger.warning('启动github监控平台')
    user = session.get('username')
    
    if str(user) == usernameconfig:

        os.popen('bash /TIP/flask_cnvd/shellscript/githubmonplatform.sh startgithubplatform')

        return render_template('platform.html')
    else:
        return render_template('login.html')



#关闭ARL资产探测平台
@app.route("/stoparlplatforminterface/")
def stoparlplatforminterface():
    
    app.logger.warning('关闭ARL资产探测平台')
    user = session.get('username')
    
    if str(user) == usernameconfig:

        os.popen('bash /TIP/flask_cnvd/shellscript/githubmonplatform.sh stoparl')

        return render_template('platform.html')
    else:
        return render_template('login.html')
    

#关闭github监控平台
@app.route("/stopgithubplatforminterface/")
def stopgithubplatforminterface():
    
    app.logger.warning('关闭github监控平台')
    user = session.get('username')
    
    if str(user) == usernameconfig:

        os.popen('bash /TIP/flask_cnvd/shellscript/githubmonplatform.sh stopgithubplatform')

        return render_template('platform.html')
    else:
        return render_template('login.html')
        
#----------------------------------------监控平台模块------------------------------------------------#




#----------------------------------------邮箱域名速查模块------------------------------------------------#
#跳转到邮箱域名速查界面
@app.route("/domainemail/")
def domainemail():
    
    app.logger.warning('跳转到邮箱域名速查界面')
    user = session.get('username')
    if str(user) == usernameconfig:
        return render_template('email.html')
    else:
        return render_template('login.html')



#邮箱域名功能实现
@app.route("/domainbyemail/",methods=['post'])
def domainbyemail():
    
    app.logger.warning('邮箱域名功能实现')
    domain = request.form['domain']
    domaint = domain.replace("www","")
    list2 = ["未查询到域名关联邮箱泄露信息!"]
    url = "https://api.hunter.io/v2/domain-search?domain="+domaint+"&api_key=d33e05af299d4f2e1426650f915c49c4badd9b07"
    try:
        res = requests.get(url,allow_redirects=False)
        res.encoding = 'utf-8'
        restext = res.text
        resdic = json.loads(restext)
        restextdata = resdic['data']['emails']
        lis = [ i['value']  for i in restextdata ]
        if len(lis) == 0:
            return render_template('email.html',data=list2,data1=domaint)
        else:
            return render_template('email.html',data=lis,data1=domaint)
    except:
        return render_template('email.html',data="接口内部出现错误!",data1=domaint)
#----------------------------------------邮箱域名速查模块------------------------------------------------#




#----------------------------------------ES数据库操作模块------------------------------------------------#
#ES数据库操作
#清空ES库
@app.route("/clearelasticsearch/")
def clearelasticsearch():
    app.logger.warning('清空ES数据库vulnbase索引')
    user = session.get('username')
    if str(user) == usernameconfig:
        ES =[esurl]
        es = Elasticsearch(
            ES,
            http_auth=(esusername, espassword),
            verify_certs=False
        )
        es.indices.delete(index='vulnbase')
        return render_template('index.html')
    else:
        return render_template('login.html')



#MySQL数据库存入ES数据库
@app.route("/addelasticsearch/")
def addelasticsearch():
    
    app.logger.warning('MySQL数据库存入ES数据库')
    user = session.get('username')
    if str(user) == usernameconfig:
        #查询所有数据
        db= pymysql.connect(host=dict['ip'],user=dict['username'],  
        password=dict['password'],db=dict['dbname'],port=dict['portnum']) 
        cur = db.cursor()
        sql="select vulnname,ip,datenow,id from vuln_table order by id desc"
        cur.execute(sql)
        data = cur.fetchall()
        ES =[esurl]
        # 创建elasticsearch客户端
        es = Elasticsearch(
            ES,
            http_auth=(esusername, espassword),
            verify_certs=False
        )
        for row in data:
            message ={
                "id":row[3],
                "vulnname":row[0],
                "ip":row[1],
                "datenow":row[2]
            }
            es.index(index="vulnbase",document=message)
        return render_template('index.html')
    else:
        return render_template('login.html')
#----------------------------------------ES数据库操作模块------------------------------------------------#



#----------------------------------------前端接口提取模块------------------------------------------------#
#跳转到接口提取界面
@app.route("/pagelink/")
def pagelink():
    
    app.logger.warning('跳转到接口提取界面')
    user = session.get('username')
    if str(user) == usernameconfig:
        #js链接前端显示
        link_file = open('/TIP/flask_cnvd/file_txt/pagelink.txt',encoding='utf-8')
        link_list = []
        for linen in link_file.readlines():
            link_list.append(linen)

        #js隐藏链接前端显示
        hidden_link_file = open('/TIP/flask_cnvd/file_txt/hiddenpagelink.txt',encoding='utf-8')
        hidden_link_list = []
        for hiddenlink in hidden_link_file.readlines():
            hidden_link_list.append(hiddenlink)
        
        return render_template('pagelink.html',data=link_list,data1=hidden_link_list)
    else:
        return render_template('login.html')



#js链接爬取接口
@app.route("/pagelinkfun/",methods=['post'])
def pagelinkfun():
    
    app.logger.warning('js链接爬取接口')
    user = session.get('username')
    
    try:
        if str(user) == usernameconfig:
            domain = request.form['domain']
            #接收前端字符串写入到urls.txt文件中
            f = open(file='/TIP/flask_cnvd/file_txt/urls.txt',mode='w')
            f.write(domain)
            f.close()
            
            #调用subjs提取js工具
            subjs_result = os.popen('bash /TIP/flask_cnvd/shellscript/sub_link.sh subjs').read()

            #定义列表sub_result_list用于存放数据
            sub_result_list = []
            #将一个字符串拆分成多行
            lines = subjs_result.splitlines()
            for i in lines:
                sub_result_list.append(i)

            #将列表存放到文件中
            f1 = open(file='/TIP/flask_cnvd/file_txt/pagelink.txt', mode='w')
            for j in sub_result_list:
                f1.write(str(j)+"\n")

            return render_template('pagelink.html')
        else:
            return render_template('login.html')
    except:
        pass



#JS隐藏链接提取接口
@app.route("/hideenpagelinkfun/",methods=['post'])
def hideenpagelinkfun():
    
    app.logger.warning('JS隐藏链接提取接口')
    user = session.get('username')
    
    try:
        if str(user) == usernameconfig:
            jslinkdata = request.form['jslinkdata']
            
            #调用LinkFinder js文件隐藏链接提取工具
            linkfinder = os.popen('bash /TIP/flask_cnvd/shellscript/sub_link.sh linkjs'+' '+jslinkdata).read()
            
            #定义列表用于存放隐藏链接
            hiddenlink_list = []
            lines = linkfinder.splitlines()
            for i in lines:
                hiddenlink_list.append(i)
            #将列表存放到文件中
            f2 = open(file='/TIP/flask_cnvd/file_txt/hiddenpagelink.txt', mode='w')
            for jl in hiddenlink_list:
                f2.write(str(jl)+"\n")

            return render_template('pagelink.html')
        else:
            return render_template('login.html')
    except:
        pass

#清空pagelink.txt和hiddenpagelink.txt
@app.route("/clearhideenpagelinkinterface/",methods=['get'])
def clearhideenpagelinkinterface():
    
    app.logger.warning('清空pagelink.txt和hiddenpagelink.txt')
    user = session.get('username')
    if str(user) == usernameconfig:
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/hiddenpagelink.txt')
        os.popen('rm -rf /TIP/flask_cnvd/file_txt/pagelink.txt')
        os.popen('touch /TIP/flask_cnvd/file_txt/hiddenpagelink.txt')
        os.popen('touch /TIP/flask_cnvd/file_txt/pagelink.txt')
        return render_template('pagelink.html')
    else:
        return render_template('login.html')

#----------------------------------------前端接口提取模块------------------------------------------------#





if __name__ == '__main__':
    handler = logging.FileHandler('/TIP/flask_cnvd/log/info.log', encoding='UTF-8')
    handler.setLevel(logging.DEBUG)
    logging_format = logging.Formatter(
        '%(asctime)s  - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)
    
    #判断是否开启debug模式
    if debugmode == 0:
        app.run(host=linkconfig['ip'],port=linkconfig['port'])
    elif  debugmode == 1:
        
        app.run(host=linkconfig['ip'],port=linkconfig['port'],debug=True)
    else:
        print("修改config文件中的debugmode的值为0或者1")
