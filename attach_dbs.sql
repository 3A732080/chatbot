-- attach_db.sql
USE [master];
GO
CREATE DATABASE [19_answer] ON 
(FILENAME = N'/var/opt/mssql/data/19_answer.mdf'), 
(FILENAME = N'/var/opt/mssql/data/19_answer_log.ldf') 
FOR ATTACH;
GO
