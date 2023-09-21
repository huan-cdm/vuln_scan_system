#! /bin/bash
case "${1}" in
    dirsearchscan)
    #python3 /TIP/flask_cnvd/dirsearch/dirsearch.py -l /TIP/flask_cnvd/file_txt/dirsearchtarget.txt -e $2 -r -R $3 -i $4 -w $5 -t $6  --timeout=30000 >> /TIP/flask_cnvd/file_txt/dirsearchfile.txt
    python3 /TIP/flask_cnvd/dirsearch/dirsearch.py -l /TIP/flask_cnvd/file_txt/dirsearchtarget.txt -e $2 -r -R $3 -i $4 -w $5 -t $6 exclude-sizes = 0b,123gb   > /TIP/flask_cnvd/file_txt/dirsearchfile.txt
    ;;
esac