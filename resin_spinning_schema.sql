-- resin_spinning_schema.sql
-- “前端树脂与纺丝工艺参数”表的 SQL Server DDL 脚本

-- 检查并使用目标数据库 (如果需要，通常在连接时指定)
-- USE UHMWPE_DB;
-- GO

-- =====================================================================================
-- 表: 前端树脂与纺丝工艺表 (FrontendResinAndSpinningProcessParametersTable)
-- 描述: 存储前端树脂材料特性及纺丝工艺相关的详细参数。
-- =====================================================================================
IF OBJECT_ID('dbo.前端树脂与纺丝工艺表', 'U') IS NOT NULL
    DROP TABLE dbo.前端树脂与纺丝工艺表;
GO

CREATE TABLE dbo.前端树脂与纺丝工艺表 (
    记录ID INT IDENTITY(1,1) PRIMARY KEY,                                           -- 记录唯一标识符，自增
    批号 NVARCHAR(100) NOT NULL,                                                   -- 产品或实验批号，唯一且不为空
    材料牌号 NVARCHAR(100) NOT NULL,                                               -- 材料的具体牌号或内部编号
    供应商 NVARCHAR(150) NULL,                                                    -- 原材料供应商名称
    树脂类型 NVARCHAR(100) NULL DEFAULT N'UHMWPE',                                   -- 树脂类型，例如 "UHMWPE"
    树脂分子量_g_mol DECIMAL(18, 2) NULL,                                           -- 树脂的重均或粘均分子量 (单位: g/mol)
    多分散系数_PDI DECIMAL(10, 3) NULL,                                             -- 树脂分子量分布的多分散系数 (Mw/Mn)
    特性粘度_dL_g DECIMAL(10, 3) NULL,                                              -- 树脂的特性粘度 (单位: dL/g)
    熔点_C DECIMAL(10, 2) NULL,                                                     -- 树脂或纤维的熔点 (单位: °C)
    结晶度_percent DECIMAL(10, 2) NULL,                                             -- 材料的结晶度百分比 (单位: %)
    纺丝方法 NVARCHAR(100) NULL,                                                   -- 采用的纺丝方法，例如 "凝胶纺丝", "干法纺丝", "熔融纺丝"
    溶剂体系 NVARCHAR(150) NULL,                                                   -- 纺丝过程中使用的溶剂体系，例如 "十氢萘", "白油"
    原液浓度_percent DECIMAL(10, 2) NULL,                                           -- 纺丝原液的浓度 (单位: %)
    纺丝温度_C DECIMAL(10, 2) NULL,                                                 -- 纺丝过程中的温度 (单位: °C)
    喷丝板规格 NVARCHAR(100) NULL,                                                 -- 喷丝板的关键规格，例如 "孔径 0.5mm, 孔数 200"
    凝固浴组成 NVARCHAR(150) NULL,                                                 -- 凝固浴的化学组成
    凝固浴温度_C DECIMAL(10, 2) NULL,                                               -- 凝固浴的温度 (单位: °C)
    拉伸倍数 DECIMAL(10, 2) NULL,                                                   -- 纤维的总拉伸倍数或各阶段拉伸倍数
    热处理温度_C DECIMAL(10, 2) NULL,                                               -- 纤维的热处理或退火温度 (单位: °C)
    备注 NVARCHAR(MAX) NULL,                                                      -- 其他备注信息或特殊工艺说明
    创建用户ID INT NULL,                                                          -- 创建此记录的用户ID，外键关联到用户表
    最后修改用户ID INT NULL,                                                      -- 最后修改此记录的用户ID，外键关联到用户表
    记录创建时间 DATETIME NOT NULL DEFAULT GETDATE(),                               -- 记录的创建时间戳，默认为当前时间
    记录更新时间 DATETIME NOT NULL DEFAULT GETDATE(),                               -- 记录的最后更新时间戳，默认为当前时间

    -- 约束定义
    CONSTRAINT UQ_前端树脂与纺丝工艺表_批号 UNIQUE (批号),                           -- 批号应唯一
    CONSTRAINT FK_前端树脂工艺表_创建用户ID FOREIGN KEY (创建用户ID) REFERENCES dbo.用户表(用户ID) ON DELETE SET NULL, -- 外键约束，用户删除时置空
    CONSTRAINT FK_前端树脂工艺表_最后修改用户ID FOREIGN KEY (最后修改用户ID) REFERENCES dbo.用户表(用户ID) ON DELETE SET NULL -- 外键约束，用户删除时置空
);
GO

PRINT 'Table "前端树脂与纺丝工艺表" created successfully.';
GO

-- 添加表和列的中文注释 (SQL Server扩展属性)
-- 表注释
EXEC sp_addextendedproperty 
    @name = N'MS_Description', @value = N'存储前端树脂材料特性及纺丝工艺相关的详细参数。',
    @level0type = N'SCHEMA', @level0name = N'dbo',
    @level1type = N'TABLE', @level1name = N'前端树脂与纺丝工艺表';
GO

-- 列注释
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'记录唯一标识符，自增', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'记录ID';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'产品或实验批号，唯一且不为空', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'批号';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'材料的具体牌号或内部编号', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'材料牌号';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'原材料供应商名称', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'供应商';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'树脂类型，例如 "UHMWPE"', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'树脂类型';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'树脂的重均或粘均分子量 (单位: g/mol)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'树脂分子量_g_mol';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'树脂分子量分布的多分散系数 (Mw/Mn)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'多分散系数_PDI';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'树脂的特性粘度 (单位: dL/g)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'特性粘度_dL_g';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'树脂或纤维的熔点 (单位: °C)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'熔点_C';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'材料的结晶度百分比 (单位: %)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'结晶度_percent';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'采用的纺丝方法，例如 "凝胶纺丝", "干法纺丝", "熔融纺丝"', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'纺丝方法';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'纺丝过程中使用的溶剂体系，例如 "十氢萘", "白油"', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'溶剂体系';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'纺丝原液的浓度 (单位: %)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'原液浓度_percent';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'纺丝过程中的温度 (单位: °C)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'纺丝温度_C';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'喷丝板的关键规格，例如 "孔径 0.5mm, 孔数 200"', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'喷丝板规格';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'凝固浴的化学组成', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'凝固浴组成';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'凝固浴的温度 (单位: °C)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'凝固浴温度_C';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'纤维的总拉伸倍数或各阶段拉伸倍数', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'拉伸倍数';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'纤维的热处理或退火温度 (单位: °C)', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'热处理温度_C';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'其他备注信息或特殊工艺说明', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'备注';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'创建此记录的用户ID，外键关联到用户表', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'创建用户ID';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'最后修改此记录的用户ID，外键关联到用户表', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'最后修改用户ID';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'记录的创建时间戳，默认为当前时间', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'记录创建时间';
EXEC sp_addextendedproperty @name=N'MS_Description', @value=N'记录的最后更新时间戳，默认为当前时间，并在更新时自动更新', @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'前端树脂与纺丝工艺表', @level2type=N'COLUMN',@level2name=N'记录更新时间';
GO

-- =====================================================================================
-- 触发器: TRG_前端树脂与纺丝工艺表_更新时间
-- 描述: 当表中的记录被更新时，自动将“记录更新时间”字段更新为当前时间。
-- =====================================================================================
IF OBJECT_ID('dbo.TRG_前端树脂与纺丝工艺表_更新时间', 'TR') IS NOT NULL
    DROP TRIGGER dbo.TRG_前端树脂与纺丝工艺表_更新时间;
GO

CREATE TRIGGER TRG_前端树脂与纺丝工艺表_更新时间
ON dbo.前端树脂与纺丝工艺表
AFTER UPDATE
AS
BEGIN
    -- 确保触发器不会因不必要的更新而触发自身，或在没有实际行更改时触发
    IF NOT UPDATE(记录更新时间) AND @@ROWCOUNT > 0
    BEGIN
        UPDATE T
        SET 记录更新时间 = GETDATE()
        FROM dbo.前端树脂与纺丝工艺表 AS T
        INNER JOIN Inserted AS I ON T.记录ID = I.记录ID;
    END
END;
GO

PRINT 'Trigger "TRG_前端树脂与纺丝工艺表_更新时间" created successfully.';
GO

PRINT 'DDL script for "前端树脂与纺丝工艺表" executed successfully.';
GO
