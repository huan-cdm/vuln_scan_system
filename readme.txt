一、系统部署方法：
1、将项目解压到 /TIP/flask_cnvd；
2、安装python3.8和mysql数据库；
3、安装docker环境；
4、安装arl资产探测和github监控平台；
5、修改/TIP/flask_cnvd/shellscript/githubmonplatform.sh替换自己的CONTAINER ID；
6、修改/TIP/flask_cnvd/config.py替换为自己的配置;
7、不建议通过公网IP直接访问，通过SSH隧道本地访问；
8、项目登录入口：http://127.0.0.1:5008/index/;
9、系统默认口令admin/admin，登录后可进行修改；
10、系统启动文件为 bash /TIP/flask_cnvd/server_back.sh，会提示操作的参数，WebService为server_back.sh的软链接，可将此目录加入环境变量，就可以在任意目录进行启动。

二、系统目录文件：
config.py：系统配置文件；
main.py：系统主要文件，后端接口都在这个文件里面；
server_back.sh：系统启动文件；
file_txt：扫描程序输出的结果都在里面；
templates：前端html文件都在里面；
shellscript：系统用到的shell脚本文件在里面；
batchfofa_start.py和batchsearch_fofa.py：批量调用fofa接口通过IP查绑定的域名信息；
static：系统前端加载用到的静态文件在里面；

三、系统存在的功能：
漏洞管理
用户管理
服务管理
fscan扫描
指纹识别
子域名扫描
未授权扫描
漏洞扫描调用vulmap
js文件隐藏链接提取
主机存活检测
字典生成
DNS解析
书签栏
IP反查域名
shodan扫描
nmap端口扫描
msscan端口扫描
arl资产探测
github资产监控
邮箱域名速查
ES数据库操作
日志管理
天气查看
系统状态查看
