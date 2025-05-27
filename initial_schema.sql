-- initial_schema.sql
-- 数据库初始结构SQL Server DDL脚本

-- 检查并创建数据库 (如果需要，通常在连接时指定数据库)
-- IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'UHMWPE_DB')
-- BEGIN
--     CREATE DATABASE UHMWPE_DB;
-- END
-- GO

-- USE UHMWPE_DB; -- 切换到目标数据库上下文
-- GO

-- =====================================================================================
-- 表: 角色表 (RolesTable)
-- 描述: 存储系统中的用户角色信息
-- =====================================================================================
IF OBJECT_ID('dbo.角色表', 'U') IS NOT NULL
    DROP TABLE dbo.角色表;
GO

CREATE TABLE dbo.角色表 (
    角色ID INT IDENTITY(1,1) PRIMARY KEY,                      -- 角色唯一标识符，自增
    角色名称 NVARCHAR(50) NOT NULL UNIQUE,                    -- 角色名称 (例如: "管理员", "研究员")
    描述 NVARCHAR(255) NULL,                                -- 角色的详细描述
    创建时间 DATETIME DEFAULT GETDATE() NOT NULL,              -- 记录创建时间，默认为当前时间
    更新时间 DATETIME DEFAULT GETDATE() NOT NULL               -- 记录更新时间，默认为当前时间
);
GO

PRINT 'Table "角色表" created successfully.';
GO

-- 示例数据: 角色表
-- INSERT INTO dbo.角色表 (角色名称, 描述) VALUES
-- (N'管理员', N'系统最高权限管理员'),
-- (N'研究员', N'可以录入和查看数据的研究人员');
-- GO

-- =====================================================================================
-- 表: 用户表 (UsersTable)
-- 描述: 存储系统的用户信息
-- =====================================================================================
IF OBJECT_ID('dbo.用户表', 'U') IS NOT NULL
    DROP TABLE dbo.用户表;
GO

CREATE TABLE dbo.用户表 (
    用户ID INT IDENTITY(1,1) PRIMARY KEY,                      -- 用户唯一标识符，自增
    用户名 NVARCHAR(100) NOT NULL UNIQUE,                     -- 用户登录名，唯一且不为空
    密码哈希 NVARCHAR(255) NOT NULL,                          -- 存储用户密码的哈希值，不为空
    角色ID INT NOT NULL,                                     -- 外键，关联到角色表的角色ID
    全名 NVARCHAR(100) NULL,                                 -- 用户全名
    邮箱 NVARCHAR(100) NULL UNIQUE,                           -- 用户邮箱，唯一
    是否启用 BIT DEFAULT 1 NOT NULL,                           -- 账户是否启用 (1: 是, 0: 否)，默认为1
    创建时间 DATETIME DEFAULT GETDATE() NOT NULL,              -- 记录创建时间，默认为当前时间
    更新时间 DATETIME DEFAULT GETDATE() NOT NULL,              -- 记录更新时间，默认为当前时间

    CONSTRAINT FK_用户表_角色ID FOREIGN KEY (角色ID) REFERENCES dbo.角色表(角色ID) -- 外键约束
);
GO

PRINT 'Table "用户表" created successfully.';
GO

-- =====================================================================================
-- 表: 模块表 (ModulesTable)
-- 描述: 存储系统功能模块信息
-- =====================================================================================
IF OBJECT_ID('dbo.模块表', 'U') IS NOT NULL
    DROP TABLE dbo.模块表;
GO

CREATE TABLE dbo.模块表 (
    模块ID INT IDENTITY(1,1) PRIMARY KEY,                      -- 模块唯一标识符，自增
    模块名称 NVARCHAR(100) NOT NULL UNIQUE,                   -- 模块名称 (例如: "材料管理", "纤维性能")
    模块路由 NVARCHAR(255) NULL,                              -- 模块前端路由 (例如: "/materials", "/fiber-performance")
    父模块ID INT NULL,                                       -- 父模块ID，用于层级结构 (例如导航菜单)
    创建时间 DATETIME DEFAULT GETDATE() NOT NULL,              -- 记录创建时间，默认为当前时间
    更新时间 DATETIME DEFAULT GETDATE() NOT NULL,              -- 记录更新时间，默认为当前时间

    CONSTRAINT FK_模块表_父模块ID FOREIGN KEY (父模块ID) REFERENCES dbo.模块表(模块ID) -- 自引用外键约束
);
GO

PRINT 'Table "模块表" created successfully.';
GO

-- 示例数据: 模块表
-- INSERT INTO dbo.模块表 (模块名称, 模块路由, 父模块ID) VALUES
-- (N'系统管理', N'/system', NULL),
-- (N'用户管理', N'/system/users', (SELECT 模块ID FROM dbo.模块表 WHERE 模块名称 = N'系统管理')),
-- (N'角色管理', N'/system/roles', (SELECT 模块ID FROM dbo.模块表 WHERE 模块名称 = N'系统管理')),
-- (N'材料数据库', N'/database', NULL),
-- (N'纤维数据管理', N'/database/fibers', (SELECT 模块ID FROM dbo.模块表 WHERE 模块名称 = N'材料数据库'));
-- GO

-- =====================================================================================
-- 表: 角色权限表 (RolePermissionsTable)
-- 描述: 存储角色对各个模块的操作权限
-- =====================================================================================
IF OBJECT_ID('dbo.角色权限表', 'U') IS NOT NULL
    DROP TABLE dbo.角色权限表;
GO

CREATE TABLE dbo.角色权限表 (
    角色权限ID INT IDENTITY(1,1) PRIMARY KEY,                  -- 角色权限唯一标识符，自增
    角色ID INT NOT NULL,                                     -- 外键，关联到角色表的角色ID
    模块ID INT NOT NULL,                                     -- 外键，关联到模块表的模块ID
    允许读取 BIT DEFAULT 0 NOT NULL,                           -- 是否允许读取数据 (1: 是, 0: 否)，默认为0
    允许写入 BIT DEFAULT 0 NOT NULL,                           -- 是否允许写入 (创建/更新) 数据 (1: 是, 0: 否)，默认为0
    允许删除 BIT DEFAULT 0 NOT NULL,                           -- 是否允许删除数据 (1: 是, 0: 否)，默认为0
    允许导入 BIT DEFAULT 0 NOT NULL,                           -- 是否允许导入数据 (1: 是, 0: 否)，默认为0
    允许导出 BIT DEFAULT 0 NOT NULL,                           -- 是否允许导出数据 (1: 是, 0: 否)，默认为0
    创建时间 DATETIME DEFAULT GETDATE() NOT NULL,              -- 记录创建时间，默认为当前时间
    更新时间 DATETIME DEFAULT GETDATE() NOT NULL,              -- 记录更新时间，默认为当前时间

    CONSTRAINT FK_角色权限表_角色ID FOREIGN KEY (角色ID) REFERENCES dbo.角色表(角色ID), -- 外键约束
    CONSTRAINT FK_角色权限表_模块ID FOREIGN KEY (模块ID) REFERENCES dbo.模块表(模块ID), -- 外键约束
    CONSTRAINT UQ_角色权限表_角色ID_模块ID UNIQUE (角色ID, 模块ID) -- 唯一约束，确保同一角色对同一模块只有一条权限记录
);
GO

PRINT 'Table "角色权限表" created successfully.';
GO

-- 触发器: 更新用户表和角色表的“更新时间”字段
-- =====================================================================================
-- 触发器: 更新用户表中的更新时间
IF OBJECT_ID('dbo.TRG_用户表_更新时间', 'TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_用户表_更新时间;
GO
CREATE TRIGGER TRG_用户表_更新时间
ON dbo.用户表
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(更新时间) -- 防止递归触发
    BEGIN
        UPDATE dbo.用户表
        SET 更新时间 = GETDATE()
        FROM Inserted i
        WHERE dbo.用户表.用户ID = i.用户ID;
    END
END;
GO

PRINT 'Trigger "TRG_用户表_更新时间" created successfully.';
GO

-- 触发器: 更新角色表中的更新时间
IF OBJECT_ID('dbo.TRG_角色表_更新时间', 'TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_角色表_更新时间;
GO
CREATE TRIGGER TRG_角色表_更新时间
ON dbo.角色表
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(更新时间) -- 防止递归触发
    BEGIN
        UPDATE dbo.角色表
        SET 更新时间 = GETDATE()
        FROM Inserted i
        WHERE dbo.角色表.角色ID = i.角色ID;
    END
END;
GO

PRINT 'Trigger "TRG_角色表_更新时间" created successfully.';
GO

-- 触发器: 更新模块表中的更新时间
IF OBJECT_ID('dbo.TRG_模块表_更新时间', 'TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_模块表_更新时间;
GO
CREATE TRIGGER TRG_模块表_更新时间
ON dbo.模块表
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(更新时间) -- 防止递归触发
    BEGIN
        UPDATE dbo.模块表
        SET 更新时间 = GETDATE()
        FROM Inserted i
        WHERE dbo.模块表.模块ID = i.模块ID;
    END
END;
GO

PRINT 'Trigger "TRG_模块表_更新时间" created successfully.';
GO

-- 触发器: 更新角色权限表中的更新时间
IF OBJECT_ID('dbo.TRG_角色权限表_更新时间', 'TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_角色权限表_更新时间;
GO
CREATE TRIGGER TRG_角色权限表_更新时间
ON dbo.角色权限表
AFTER UPDATE
AS
BEGIN
    IF NOT UPDATE(更新时间) -- 防止递归触发
    BEGIN
        UPDATE dbo.角色权限表
        SET 更新时间 = GETDATE()
        FROM Inserted i
        WHERE dbo.角色权限表.角色权限ID = i.角色权限ID;
    END
END;
GO

PRINT 'Trigger "TRG_角色权限表_更新时间" created successfully.';
GO

PRINT 'Initial database schema DDL script executed successfully.';
GO
