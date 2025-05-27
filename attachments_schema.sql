-- attachments_schema.sql
-- “附件表” (AttachmentsTable) 的 SQL Server DDL 脚本

-- 检查并使用目标数据库 (如果需要)
-- USE UHMWPE_DB;
-- GO

-- =====================================================================================
-- 表: 附件表 (AttachmentsTable)
-- 描述: 存储与各个模块记录关联的附件文件信息。
-- =====================================================================================
IF OBJECT_ID('dbo.附件表', 'U') IS NOT NULL
    DROP TABLE dbo.附件表;
GO

CREATE TABLE dbo.附件表 (
    附件ID INT IDENTITY(1,1) PRIMARY KEY,                                   -- 附件唯一标识符，自增
    关联记录ID INT NOT NULL,                                                -- 关联的父记录ID (例如，某个树脂纺丝工艺记录的ID)
    关联模块名称 NVARCHAR(100) NOT NULL,                                     -- 关联的父记录所在的模块名称 (例如，"前端树脂与纺丝工艺表")
    原始文件名 NVARCHAR(255) NOT NULL,                                       -- 用户上传时的原始文件名
    存储文件名 NVARCHAR(255) NOT NULL UNIQUE,                                 -- 服务器上存储的唯一文件名 (例如，UUID + 扩展名)
    文件路径 NVARCHAR(500) NULL,                                             -- 文件在服务器上的相对存储路径 (相对于配置的UPLOAD_FOLDER)
    文件类型 NVARCHAR(100) NULL,                                             -- 文件的MIME类型 (例如，"image/jpeg", "application/pdf")
    文件大小_字节 BIGINT NULL,                                                -- 文件大小，单位为字节
    上传用户ID INT NULL,                                                      -- 上传此附件的用户ID
    上传时间 DATETIME NOT NULL DEFAULT GETDATE(),                             -- 文件上传时间戳

    -- 外键约束
    CONSTRAINT FK_附件表_上传用户ID FOREIGN KEY (上传用户ID) REFERENCES dbo.用户表(用户ID) ON DELETE SET NULL -- 如果用户被删除，附件记录中的用户ID置为NULL
);
GO

PRINT 'Table "附件表" created successfully.';
GO

-- 创建索引以优化查询
CREATE INDEX IX_附件表_关联记录和模块 
ON dbo.附件表 (关联记录ID, 关联模块名称);
GO

PRINT 'Index "IX_附件表_关联记录和模块" created successfully.';
GO

-- 添加表和列的中文注释 (SQL Server扩展属性)
EXEC sp_addextendedproperty 
    @name = N'MS_Description', @value = N'存储与各个模块记录关联的附件文件信息。',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'附件表';
GO

EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'附件唯一标识符，自增', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'附件表', @level2type=N'COLUMN',@level2name=N'附件ID';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'关联的父记录ID (例如，某个树脂纺丝工艺记录的ID)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'附件表', @level2type=N'COLUMN',@level2name=N'关联记录ID';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'关联的父记录所在的模块名称 (例如，"前端树脂与纺丝工艺表")', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'附件表', @level2type=N'COLUMN',@level2name=N'关联模块名称';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'用户上传时的原始文件名', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'附件表', @level2type=N'COLUMN',@level2name=N'原始文件名';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'服务器上存储的唯一文件名 (例如，UUID + 扩展名)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'附件表', @level2type=N'COLUMN',@level2name=N'存储文件名';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'文件在服务器上的相对存储路径 (相对于配置的UPLOAD_FOLDER)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'附件表', @level2type=N'COLUMN',@level2name=N'文件路径';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'文件的MIME类型 (例如，"image/jpeg", "application/pdf")', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'附件表', @level2type=N'COLUMN',@level2name=N'文件类型';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'文件大小，单位为字节', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'附件表', @level2type=N'COLUMN',@level2name=N'文件大小_字节';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'上传此附件的用户ID', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'附件表', @level2type=N'COLUMN',@level2name=N'上传用户ID';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'文件上传时间戳', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'附件表', @level2type=N'COLUMN',@level2name=N'上传时间';
GO

PRINT 'DDL script for "附件表" executed successfully.';
GO
