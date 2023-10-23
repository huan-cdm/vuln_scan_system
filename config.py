#配置变更，需要重启服务才能生效。
#fofa配置
fofakey = ""
#fofa配置，批量检索查询最多条数
batchfofanum = ""
#批量检索休眠时间
batchfofasleeptime = 
#fofa邮箱配置
fofaemail = ""

#MySQL数据库配置
dict = {
    "ip":"","username":"","password":"","dbname":"","portnum": 3306
}


#shodan配置
shodankey = ""


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
esusername = ""
espassword = ""
esurl = ""


#vulmap漏洞扫描器参数配置,XLSXz转换，sheet名称配置
dir_vul_url = "urls"

#arl资产探测平台登录方式和账号密码
arlurl = ""
arluserpass = ""

#github监控平台登录方式和账号密码
githuburl = ""
githubpass = ""

#配置系统启动是否开启debug模式
# 0:关闭debug模式
# 1:开启debug模式
debugmode=0


#定义目录扫描文件白名单过滤
dirscanwhite = [
    'edu.cn','gov.cn'
]
