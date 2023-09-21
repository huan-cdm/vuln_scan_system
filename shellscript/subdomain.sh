#! /bin/bash
case "${1}" in
    subDomainsBrutescan1)
    python3 /TIP/flask_cnvd/subDomainsBrute/subDomainsBrute.py $2 -t 20 -i -o /TIP/flask_cnvd/file_txt/subdomain.txt > /TIP/flask_cnvd/file_txt/subdomain.txt
    ;;

    subDomainsBrutescan2)
    python3 /TIP/flask_cnvd/subDomainsBrute/subDomainsBrute.py $2 -t 20 -i --full -o /TIP/flask_cnvd/file_txt/subdomain.txt > /TIP/flask_cnvd/file_txt/subdomain.txt
    ;;
    
esac