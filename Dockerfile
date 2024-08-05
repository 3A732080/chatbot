# 使用 Azure SQL Edge 基礎映像
FROM mcr.microsoft.com/azure-sql-edge

# 創建數據庫文件夾
# RUN mkdir -p /var/opt/mssql/data

# 複製本地的 .mdf 和 .ldf 文件到容器中
COPY ./sql_data/data/*.mdf /var/opt/mssql/data/
COPY ./sql_data/data/*.ldf /var/opt/mssql/data/

# 複製初始化 SQL 腳本到容器中
COPY attach_dbs.sql /var/opt/mssql/scripts/attach_dbs.sql

# 設置初始化 Shell 腳本為入口點
COPY init-db.sh /var/opt/mssql/scripts/init-db.sh



ENTRYPOINT [ "/var/opt/mssql/scripts/init-db.sh" ]

# CMD 指令啟動 SQL Server
CMD [ "/opt/mssql/bin/sqlservr" ]
