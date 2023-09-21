#! /bin/bash
case "${1}" in
    #提取js文件shell脚本
    subjs)
    sub_result=`/TIP/flask_cnvd/sub_server/subjs -i /TIP/flask_cnvd/file_txt/urls.txt`
    echo "${sub_result}"
    ;;

    #从js文件中提取隐藏的链接shell脚本
    linkjs)
    link_result=`python3 /TIP/flask_cnvd/LinkFinder/linkfinder.py -i $2 -o cli`
    echo "${link_result}"
    ;;
    
esac