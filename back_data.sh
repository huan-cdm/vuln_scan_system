#!/bin/bash
rm -rf /root/codebackup/back_data_file/*.sql
rm -rf /root/codebackup/mysql-*.tar.gz
# 数据库信息
DB_USER="xxxx"
DB_PASS="xxxx"
DB_NAME="xxxx"

# 导出文件保存路径和文件名前缀
BACKUP_DIR="/root/codebackup/back_data_file/"

# 导出所有表
TABLES=$(mysql -u${DB_USER} -p${DB_PASS} -N ${DB_NAME} -e 'show tables')

# 逐个导出备份
for t in $TABLES; do
	BACKUP_FILENAME="${t}.sql"
	mysqldump -u${DB_USER} -p${DB_PASS} ${DB_NAME} $t > ${BACKUP_DIR}${BACKUP_FILENAME}
	echo "备份成功：${BACKUP_DIR}${BACKUP_FILENAME}"
done
nohup tar -czvf /root/codebackup/mysql-`date +%Y%m%d`.tar.gz  /root/codebackup/back_data_file/ 1>/dev/null 2>&1 &
echo "数据库备份完成"
