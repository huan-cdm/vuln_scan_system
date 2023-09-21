#! /bin/bash
case "${1}" in
    moren)
    /usr/bin/crunch $2 $3 $4 > /TIP/flask_cnvd/file_txt/dicc.txt
    ;;

    zidingyi)
    /usr/bin/crunch $2 $3 -t $4 > /TIP/flask_cnvd/file_txt/dicc.txt
    ;;

esac