#配置变更，需要重启服务才能生效。
#fofa配置
fofakey = "9741ff706e07eb9251fae1cefce030c8"
#fofa配置，批量检索查询最多条数
batchfofanum = "100"
#批量检索休眠时间
batchfofasleeptime = 2
#fofa邮箱配置
fofaemail = "weakchicken@qq.com"

#MySQL数据库配置
dict = {
    "ip":"127.0.0.1","username":"mysql","password":"zwroot123!@#","dbname":"CNVD","portnum": 3306
}


#shodan配置
shodankey = "5wdqqD7mCbWQdehFqWhk5aKVK0OtwR0Z"


#信息收集平台web访问配置
linkconfig = {
    #设置127.0.0.1通过ssh隧道本地访问，设置0.0.0.0可以外网访问。
    "ip":"127.0.0.1","port":"5008"
   # "ip":"0.0.0.0","port":"5008"
}


monlinkconfig = {
    #设置127.0.0.1通过ssh隧道本地访问，设置0.0.0.0可以外网访问。
    "ip":"0.0.0.0","port":"9999"
    #"ip":"127.0.0.1","port":"9999"
}



#Elasticsearch数据库配置
esusername = "elastic"
espassword = "okoHRTB6pJS3Ltw=XouX"
esurl = "https://121.37.207.248:9200"


#vulmap漏洞扫描器参数配置,XLSXz转换，sheet名称配置
dir_vul_url = "urls"

#arl资产探测平台登录方式和账号密码
arlurl = "https://121.37.207.248:5003/login"
arluserpass = "admin/zwroot123!@#"

#github监控平台登录方式和账号密码
githuburl = "http://121.37.207.248:8001/"
githubpass = "admin/zwroot123!@#"

#配置系统启动是否开启debug模式
# 0:关闭debug模式
# 1:开启debug模式
debugmode=0


#定义目录扫描文件白名单过滤
dirscanwhite = [
    'edu.cn','gov.cn'
]