#!/bin/bash
# 啟動 SQL Server
/opt/mssql/bin/sqlservr &

# 等待 SQL Server 完全啟動
sleep 30

# 運行 SQL 腳本來附加數據庫
/opt/mssql-tools/bin/sqlcmd -S localhost -U SA -P YourStrong!Passw0rd -i /var/opt/mssql/scripts/attach_dbs.sql

# 防止容器退出
wait
