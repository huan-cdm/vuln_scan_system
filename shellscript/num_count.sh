#! /bin/bash
case "${1}" in
    #vulmap漏洞扫描漏洞数量
    vulmapcount)
    vulmapcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "名称" |  wc -l`
    echo "${vulmapcount_value}"
	;;
    #vulmap漏洞数量-activemq
    vulmapactivemqcount)
    vulmapactivemqcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "activemq" |  wc -l`
    echo "${vulmapactivemqcount_value}"
	;;

    #vulmap漏洞数量-flink
    vulmapflinkcount)
    vulmapflinkcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "flink" |  wc -l`
    echo "${vulmapflinkcount_value}"
    ;;

    #vulmap漏洞数量-shiro
    vulmapshirocount)
    vulmapshirocount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "shiro" |  wc -l`
    echo "${vulmapshirocount_value}"
    ;;

    #vulmap漏洞数量-solr
    vulmapsolrcount)
    vulmapsolrcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "solr" |  wc -l`
    echo "${vulmapsolrcount_value}"
    ;;

    #vulmap漏洞数量-struts2
    vulmapstruts2count)
    vulmapstruts2count_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "struts2" |  wc -l`
    echo "${vulmapstruts2count_value}"
    ;;

    #vulmap漏洞数量-tomcat
    vulmaptomcatcount)
    vulmaptomcatcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "tomcat" |  wc -l`
    echo "${vulmaptomcatcount_value}"
    ;;

    #vulmap漏洞数量-unomi
    vulmapunomicount)
    vulmapunomicount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "unomi" |  wc -l`
    echo "${vulmapunomicount_value}"
    ;;

    #vulmap漏洞数量-drupal
    vulmapdrupalcount)
    vulmapdrupalcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "drupal" |  wc -l`
    echo "${vulmapdrupalcount_value}"
    ;;

    #vulmap漏洞数量-elasticsearch
    vulmapelasticsearchcount)
    vulmapelasticsearchcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "elasticsearch" |  wc -l`
    echo "${vulmapelasticsearchcount_value}"
    ;;


    #vulmap漏洞数量-fastjson
    vulmapfastjsoncount)
    vulmapfastjsoncount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "fastjson" |  wc -l`
    echo "${vulmapfastjsoncount_value}"
    ;;

    #vulmap漏洞数量-jenkins
    vulmapjenkinscount)
    vulmapjenkinscount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "jenkins" |  wc -l`
    echo "${vulmapjenkinscount_value}"
    ;;

    #vulmap漏洞数量-laravel
    vulmaplaravelcount)
    vulmaplaravelcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "laravel" |  wc -l`
    echo "${vulmaplaravelcount_value}"
    ;;

    #vulmap漏洞数量-nexus
    vulmapnexuscount)
    vulmapnexuscount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "nexus" |  wc -l`
    echo "${vulmapnexuscount_value}"
    ;;

    #vulmap漏洞数量-weblogic
    vulmapweblogiccount)
    vulmapweblogiccount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "weblogic" |  wc -l`
    echo "${vulmapweblogiccount_value}"
    ;;

    #vulmap漏洞数量-jboss
    vulmapjbosscount)
    vulmapjbosscount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "jboss" |  wc -l`
    echo "${vulmapjbosscount_value}"
    ;;

    #vulmap漏洞数量-spring
    vulmapspringcount)
    vulmapspringcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "spring" |  wc -l`
    echo "${vulmapspringcount_value}"
    ;;

    #vulmap漏洞数量-thinkphp
    vulmapthinkphpcount)
    vulmapthinkphpcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "thinkphp" |  wc -l`
    echo "${vulmapthinkphpcount_value}"
    ;;

    #vulmap漏洞数量-druid
    vulmapdruidcount)
    vulmapdruidcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "druid" |  wc -l`
    echo "${vulmapdruidcount_value}"
    ;;

    #vulmap漏洞数量-exchange
    vulmapexchangecount)
    vulmapexchangecount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "名称:exchange" |  wc -l`
    echo "${vulmapexchangecount_value}"
    ;;


    #vulmap漏洞数量-nodejs
    vulmapnodejscount)
    vulmapnodejscount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "nodejs" |  wc -l`
    echo "${vulmapnodejscount_value}"
    ;;


    #vulmap漏洞数量-saltstack
    vulmapsaltstackcount)
    vulmapsaltstackcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "saltstack" |  wc -l`
    echo "${vulmapsaltstackcount_value}"
    ;;


    #vulmap漏洞数量-vmware
    vulmapvmwarecount)
    vulmapvmwarecount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "vmware" |  wc -l`
    echo "${vulmapvmwarecount_value}"
    ;;


    #vulmap漏洞数量-bigip
    vulmapbigipcount)
    vulmapbigipcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "bigip" |  wc -l`
    echo "${vulmapbigipcount_value}"
    ;;

    #vulmap漏洞数量-ofbiz
    vulmapofbizcount)
    vulmapofbizcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "ofbiz" |  wc -l`
    echo "${vulmapofbizcount_value}"
    ;;

    #vulmap漏洞数量-coremail
    vulmapcoremailcount)
    vulmapcoremailcount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "coremail" |  wc -l`
    echo "${vulmapcoremailcount_value}"
    ;;

    #vulmap漏洞数量-ecology
    vulmapecologycount)
    vulmapecologycount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "ecology" |  wc -l`
    echo "${vulmapecologycount_value}"
    ;;

    #vulmap漏洞数量-eyou
    vulmapeyoucount)
    vulmapeyoucount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "eyou" |  wc -l`
    echo "${vulmapeyoucount_value}"
    ;;

    #vulmap漏洞数量-qianxin
    vulmapqianxincount)
    vulmapqianxincount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "名称:qianxin" |  wc -l`
    echo "${vulmapqianxincount_value}"
    ;;

    #vulmap漏洞数量-ruijie
    vulmapruijiecount)
    vulmapruijiecount_value=`cat /TIP/flask_cnvd/file_txt/vulmapscanresult.txt | grep -i "ruijie" |  wc -l`
    echo "${vulmapruijiecount_value}"
    ;;

    #目录扫描原始数量/reports目录下
    dirsearchscancount)
    dirsearchscancount_value=`cat /TIP/flask_cnvd/dirsearch/reports/*/BATCH.txt | wc -l`
    #数量减2才是正确数量
    direserach_value=$[${dirsearchscancount_value}-2]
    echo "${direserach_value}"
    ;;

    #目录扫描原始数据同步后的结果
    dirsearchscancountcopy)
    dirsearchscancountcopy_value_tmp=`cat /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt  | wc -l`
    #数量减2才是正确数量
    dirsearchscancountcopy_value=$[${dirsearchscancountcopy_value_tmp}-2]
    echo "${dirsearchscancountcopy_value}"
    ;;
    
    #目录扫描同步后的结果
    dirsearchsyncresult)
    dirsearchsyncresult_value=`cat /TIP/flask_cnvd/file_txt/dirsearchfileresult.txt  | wc -l`
    echo "${dirsearchsyncresult_value}"
    ;;
esac