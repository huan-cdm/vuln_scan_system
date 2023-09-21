#!/usr/bin/env python3
from flask import Flask
from flask import  render_template
from flask_bootstrap import Bootstrap
from config import monlinkconfig
import os


app = Flask(__name__,template_folder='./templates')
app.secret_key = "DragonFire"
bootstrap = Bootstrap(app)


@app.route('/index/')
def index():
    try:
        #web服务运行状态
        web_value = os.popen('bash /TIP/flask_cnvd/shellscript/servicecheck.sh web').read()
        web_value_int = int(web_value)
        if web_value_int >= 1:
            web_value_result = "web服务状态："+"ON"
        else:
            web_value_result = "web服务状态："+"OFF"

        #mysql运行状态
        mysql_value = os.popen('bash /TIP/flask_cnvd/shellscript/servicecheck.sh mysql').read()
        mysql_value_int = int(mysql_value)
        if mysql_value_int >= 1:
            mysql_value_result = "mysql服务状态："+"ON"
        else:
            mysql_value_result = "mysql服务状态："+"OFF"
        
        #elasticsearch服务运行状态
        elasticsearch_value = os.popen('bash /TIP/flask_cnvd/shellscript/servicecheck.sh elasticsearch').read()
        elasticsearch_value_int = int(elasticsearch_value)
        if elasticsearch_value_int >= 1:
            elasticsearch_value_result = "elasticsearch服务状态："+"ON"
        else:
            elasticsearch_value_result = "elasticsearch服务状态："+"OFF"

        #目录扫描服务运行状态
        dirsearch_value = os.popen('bash /TIP/flask_cnvd/shellscript/servicecheck.sh dirsearch').read()
        dirsearch_value_int = int(dirsearch_value)
        if dirsearch_value_int > 1:
            dirsearch_value_result = "目录扫描服务状态："+"ON"
        else:
            dirsearch_value_result = "目录扫描服务状态："+"OFF"

        #漏洞扫描服务运行状态
        vulmap_value = os.popen('bash /TIP/flask_cnvd/shellscript/servicecheck.sh vulmap').read()
        vulmap_value_int = int(vulmap_value)
        if vulmap_value_int > 1:
            vulmap_value_result = "漏洞扫描服务状态："+"ON"
        else:
            vulmap_value_result = "漏洞扫描服务状态："+"OFF"

       

        return render_template('servicecheck.html',data01=web_value_result,data02=mysql_value_result,
        data03=elasticsearch_value_result,data04=dirsearch_value_result,data05=vulmap_value_result)
    except:
        pass


if __name__ == '__main__':
    #app.run(host=monlinkconfig['ip'],port=monlinkconfig['ip'],debug=True)
    app.run(host=monlinkconfig['ip'],port=monlinkconfig['port'])
