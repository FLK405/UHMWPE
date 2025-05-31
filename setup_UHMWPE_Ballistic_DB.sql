-- =============================================================================
-- UHMWPE 防弹数据库 MS SQL Server 完整创建脚本
-- 版本: V1
--
-- 说明:
-- 1. 此脚本首先检查名为 UHMWPE_Ballistic_DB 的数据库是否存在。
--    如果不存在，则创建该数据库。
-- 2. 然后，脚本切换到 UHMWPE_Ballistic_DB 数据库上下文。
-- 3. 接着，脚本依次创建所有核心数据表。
-- 4. 所有NVARCHAR字段用于支持中文等Unicode字符。
-- 5. 外键约束已包含在相应的CREATE TABLE语句中。
-- =============================================================================

-- 检查并创建数据库
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'UHMWPE_Ballistic_DB')
BEGIN
    CREATE DATABASE UHMWPE_Ballistic_DB;
    PRINT '数据库 UHMWPE_Ballistic_DB 已创建。';
END
ELSE
BEGIN
    PRINT '数据库 UHMWPE_Ballistic_DB 已存在。';
END
GO

-- 切换到目标数据库上下文
USE UHMWPE_Ballistic_DB;
GO

-- -------- 表创建开始 --------

-- 0. 用户与权限管理模块
PRINT '正在创建表: Roles...';
CREATE TABLE Roles (
    RoleID INT PRIMARY KEY IDENTITY(1,1),
    RoleName NVARCHAR(100) NOT NULL UNIQUE,    -- 角色名称 (如 管理员, 研究员, 普通用户)
    Description NVARCHAR(MAX)
);
GO
PRINT '表 Roles 已创建。';
GO

PRINT '正在创建表: Users...';
CREATE TABLE Users (
    UserID BIGINT PRIMARY KEY IDENTITY(1,1),
    Username NVARCHAR(100) NOT NULL UNIQUE,     -- 用户名
    PasswordHash VARCHAR(MAX) NOT NULL,          -- 存储密码的哈希值
    Email NVARCHAR(255) UNIQUE,
    FullName NVARCHAR(200),
    RoleID INT,                                  -- 用户角色
    IsActive BIT DEFAULT 1,                      -- 账户是否激活
    LastLoginDate DATETIME,
    DateCreated DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (RoleID) REFERENCES Roles(RoleID)
);
GO
PRINT '表 Users 已创建。';
GO
-- (更复杂的权限管理可以添加 Permissions 和 RolePermissions 表)

-- 1. 树脂基本信息表
PRINT '正在创建表: Resins...';
CREATE TABLE Resins (
    ResinID BIGINT PRIMARY KEY IDENTITY(1,1),
    Manufacturer NVARCHAR(200),                           -- 制造商
    Grade NVARCHAR(200) NOT NULL,                         -- 牌号
    BatchNo NVARCHAR(200) UNIQUE NOT NULL,                -- 批号 (应唯一且非空)
    ResinType NVARCHAR(100),                              -- 树脂类型 (如 Epoxy, PE, PU)
    ProductionDate DATETIME,                             -- 生产日期
    Supplier NVARCHAR(200),                              -- 供应商
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX)
);
GO
PRINT '表 Resins 已创建。';
GO

-- 2. 前端树脂特性与纺丝工艺模块
PRINT '正在创建表: PrecursorResin_SpinningProcess...';
-- 此表存储用于制备特定纤维批次的前端树脂特性和主要纺丝工艺参数
CREATE TABLE PrecursorResin_SpinningProcess (
    ProcessID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberBatchNo NVARCHAR(200) NOT NULL UNIQUE,         -- 目标纤维批号 (用于关联到最终纤维)
    ResinID BIGINT,                                      -- 使用的树脂ID (关联到Resins表)
    ResinGrade_Used NVARCHAR(200),                       -- 使用的树脂牌号 (可冗余或从ResinID获取)
    MolecularWeight_Mn_Resin DECIMAL(18,2),              -- 所用树脂数均分子量 (g/mol)
    MolecularWeight_Mw_Resin DECIMAL(18,2),              -- 所用树脂重均分子量 (g/mol)
    PDI_Resin DECIMAL(8,2),                              -- 所用树脂多分散系数 (Mw/Mn)
    Crystallinity_Resin_percent DECIMAL(8,2),            -- 所用树脂结晶度 (%)
    MeltingPoint_Resin_C DECIMAL(8,1),                   -- 所用树脂熔点 (°C)
    SolutionConcentration_percent DECIMAL(8,2),          -- 原液浓度 (%)
    SpinningTemperature_C DECIMAL(8,1),                  -- 纺丝温度 (°C)
    ScrewSpeed_rpm DECIMAL(10,2),                        -- 双螺杆速率 (rpm)
    CoagulationBath_Composition NVARCHAR(200),           -- 凝固浴组成
    CoagulationBathTemperature_C DECIMAL(8,1),           -- 凝固浴温度 (°C)
    DrawingTemperature_C DECIMAL(8,1),                   -- 拉伸温度 (°C)
    TotalDrawingRatio DECIMAL(8,1),                      -- 总拉伸倍数
    SolventRemovalProcess NVARCHAR(MAX),                 -- 溶剂去除工艺
    PostProcessing NVARCHAR(MAX),                        -- 后处理工艺 (如表面改性)
    EntryDate DATETIME DEFAULT GETDATE(),
    Operator NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (ResinID) REFERENCES Resins(ResinID)
);
GO
PRINT '表 PrecursorResin_SpinningProcess 已创建。';
GO

-- 3. 纤维基本信息表
PRINT '正在创建表: Fibers...';
CREATE TABLE Fibers (
    FiberID BIGINT PRIMARY KEY IDENTITY(1,1),
    Manufacturer NVARCHAR(200),
    Grade NVARCHAR(200) NOT NULL,                        -- 牌号 (如 Dyneema SK75)
    BatchNo NVARCHAR(200) UNIQUE NOT NULL,               -- 批号 (应唯一且非空)
    SpinningProcessID BIGINT,                            -- 关联到纺丝工艺ID
    LinearDensity_dtex DECIMAL(10,2),                    -- 纤度 (dtex)
    FilamentDiameter_um DECIMAL(10,2),                   -- 单丝直径 (μm)
    FilamentCount INT,                                   -- 纤维根数
    Source NVARCHAR(200),                                -- 样品来源
    ProductionDate DATETIME,
    ImagePath NVARCHAR(500),                             -- 样品图片路径
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (SpinningProcessID) REFERENCES PrecursorResin_SpinningProcess(ProcessID)
);
GO
PRINT '表 Fibers 已创建。';
GO

-- 4. 纤维性能 - 分子量
PRINT '正在创建表: Fiber_MolecularWeight...';
CREATE TABLE Fiber_MolecularWeight (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    TestTemperature_C INT,
    ViscosityAverage_MW_g_mol BIGINT,                    -- 粘均分子量 (g/mol)
    GPC_Mn_g_mol DECIMAL(18,2),                          -- GPC 数均分子量
    GPC_Mw_g_mol DECIMAL(18,2),                          -- GPC 重均分子量
    GPC_PDI DECIMAL(8,2),                                -- GPC 多分散系数
    ResultChartPath NVARCHAR(500),
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID)
);
GO
PRINT '表 Fiber_MolecularWeight 已创建。';
GO

-- 5. 纤维力学性能 - 拉伸测试
PRINT '正在创建表: Fiber_Tensile_Properties...';
CREATE TABLE Fiber_Tensile_Properties (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    TestStandard NVARCHAR(100),                          -- 测试标准 (如 ASTM D3822)
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    Temperature_C DECIMAL(8,1),
    Humidity_RH DECIMAL(8,1),
    StrainRate_per_min DECIMAL(10,2),                    -- 应变速率 (%/min 或 mm/min)
    GaugeLength_mm DECIMAL(10,1),
    TensileStrength_GPa DECIMAL(10,3),
    TensileStrength_cN_dtex DECIMAL(10,2),
    TensileStrength_CV_percent DECIMAL(8,2),             -- 断裂强度偏差系数 (%)
    YoungsModulus_GPa DECIMAL(10,2),
    YoungsModulus_cN_dtex DECIMAL(10,2),
    YoungsModulus_CV_percent DECIMAL(8,2),               -- 初始模量偏差系数 (%)
    ElongationAtBreak_percent DECIMAL(8,2),
    ElongationAtBreak_CV_percent DECIMAL(8,2),           -- 断裂伸长率偏差系数 (%)
    WorkOfFracture_J DECIMAL(19,2),                      -- 断裂功 (J)
    WorkOfFracture_CV_percent DECIMAL(8,2),              -- 断裂功偏差系数 (%)
    StressStrainCurveData_JSON NVARCHAR(MAX),            -- (JSON格式: [{stress:s1, strain:e1}, ...])
    ResultChartPath NVARCHAR(500),
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID)
);
GO
PRINT '表 Fiber_Tensile_Properties 已创建。';
GO

-- 6. 纤维力学性能 - 蠕变
PRINT '正在创建表: Fiber_Creep_Properties...';
CREATE TABLE Fiber_Creep_Properties (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    TestStandard NVARCHAR(100),                          -- 如 ASTM D2990
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    Temperature_C DECIMAL(8,1),
    Humidity_RH DECIMAL(8,1),
    AppliedLoad_Force_N DECIMAL(10,2),                   -- 强力 (N)
    AppliedStress_MPa DECIMAL(10,2),                     -- 应用应力 (MPa)
    CreepStrain_percent_at_Time_X DECIMAL(8,2),          -- 特定时间点蠕变应变 (%)
    CreepRate_percent_per_hour DECIMAL(10,5),            -- 蠕变速率 (%/h)
    CreepTime_h DECIMAL(10,2),                           -- 蠕变时间 (h)
    CreepRuptureTime_h DECIMAL(10,2),                    -- 蠕变断裂时间 (h)
    ResultChartPath NVARCHAR(500),                       -- 蠕变曲线图
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID)
);
GO
PRINT '表 Fiber_Creep_Properties 已创建。';
GO

-- 7. 纤维力学性能 - 动态拉伸
PRINT '正在创建表: Fiber_DynamicTensile_Properties...';
CREATE TABLE Fiber_DynamicTensile_Properties (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    TestStandard NVARCHAR(100),
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    Temperature_C DECIMAL(8,1),
    Humidity_RH DECIMAL(8,1),
    InitialElasticModulus_GPa DECIMAL(10,2),             -- 初始弹性模量 (GPa)
    FailureStress_MPa DECIMAL(10,2),                     -- 破坏应力 (MPa)
    InstabilityStrain_percent DECIMAL(8,2),              -- 失稳应变 (%)
    ResultChartPath NVARCHAR(500),
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID)
);
GO
PRINT '表 Fiber_DynamicTensile_Properties 已创建。';
GO

-- 8. 纤维热性能 - DSC
PRINT '正在创建表: Fiber_Thermal_DSC...';
CREATE TABLE Fiber_Thermal_DSC (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    TestStandard NVARCHAR(100),                          -- 如 ISO 11357-3
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    SampleMass_mg DECIMAL(10,3),
    CrucibleType NVARCHAR(50),
    TemperatureRange_C NVARCHAR(50),
    HeatingRate_C_min DECIMAL(8,1),
    ProtectiveGas NVARCHAR(50),
    MeltingPeakTemperature_Tm_C DECIMAL(8,1),
    EnthalpyOfFusion_J_g DECIMAL(10,2),
    Crystallinity_percent DECIMAL(8,2),
    ResultChartPath NVARCHAR(500),
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID)
);
GO
PRINT '表 Fiber_Thermal_DSC 已创建。';
GO

-- 9. 纤维热性能 - TGA
PRINT '正在创建表: Fiber_Thermal_TGA...';
CREATE TABLE Fiber_Thermal_TGA (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    TestStandard NVARCHAR(100),                          -- 如 ISO 11358
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    SampleMass_mg DECIMAL(10,3),
    CrucibleType NVARCHAR(50),
    TemperatureRange_C NVARCHAR(50),
    HeatingRate_C_min DECIMAL(8,1),
    ProtectiveGas NVARCHAR(50),
    DecompositionOnset_C DECIMAL(8,1),                   -- 热分解起始温度
    PeakDecompositionTemp_C DECIMAL(8,1),                -- 峰值热分解温度
    Residue_percent DECIMAL(8,2),                        -- 残余质量百分比
    ComponentDescription NVARCHAR(MAX),                  -- 组分含量描述
    ResultChartPath NVARCHAR(500),
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID)
);
GO
PRINT '表 Fiber_Thermal_TGA 已创建。';
GO

-- 10. 纤维热性能 - 热导率
PRINT '正在创建表: Fiber_Thermal_Conductivity...';
CREATE TABLE Fiber_Thermal_Conductivity (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    TestStandard NVARCHAR(100),                          -- 如 ASTM E1530
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    TestTemperature_C DECIMAL(8,1),                      -- 测试温度
    ThermalConductivity_W_mK DECIMAL(10,4),              -- 热导率 (W/mK)
    MeasurementDirection NVARCHAR(50),                   -- 测试方向 (轴向, 径向)
    ResultChartPath NVARCHAR(500),
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID)
);
GO
PRINT '表 Fiber_Thermal_Conductivity 已创建。';
GO

-- 11. 纤维微观结构 - 相结构 (NMR/Raman)
PRINT '正在创建表: Fiber_Microstructure_PhaseStructure...';
CREATE TABLE Fiber_Microstructure_PhaseStructure (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    TestMethod NVARCHAR(50) NOT NULL,                   -- 'NMR' 或 'Raman'
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    -- NMR Specific
    AmorphousPhase_percent_NMR DECIMAL(8,2),             -- 无定形区占比 (NMR)
    IntermediatePhase_percent_NMR DECIMAL(8,2),          -- 中间相占比 (NMR)
    CrystallinePhase_percent_NMR DECIMAL(8,2),           -- 晶相占比 (NMR)
    DefectiveCrystalline_percent_NMR DECIMAL(8,2),       -- 残缺晶相占比 (NMR)
    -- Raman Specific
    Crystallinity_percent_Raman DECIMAL(8,2),            -- 结晶度 (Raman)
    CharacteristicPeaks_Raman NVARCHAR(MAX),             -- 拉曼特征峰信息
    ResultChartPath NVARCHAR(500),
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID)
);
GO
PRINT '表 Fiber_Microstructure_PhaseStructure 已创建。';
GO

-- 12. 纤维微观结构 - 取向与晶体结构 (WAXD/声速模量)
PRINT '正在创建表: Fiber_Microstructure_OrientationCrystallinity...';
CREATE TABLE Fiber_Microstructure_OrientationCrystallinity (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    TestMethod NVARCHAR(50) NOT NULL,                   -- 'WAXD', 'SAXS', 'SonicModulus'
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    -- WAXD/SAXS Specific
    CrystalSize_nm_WAXD DECIMAL(10,2),                   -- 晶粒尺寸 (WAXD)
    OrientationFactor_WAXD DECIMAL(8,3),                 -- 取向因子 (WAXD)
    d_spacing_WAXD NVARCHAR(MAX),                        -- 晶面间距 (WAXD)
    -- Sonic Modulus Specific
    SoundVelocity_mps DECIMAL(10,1),                     -- 声速 (m/s)
    OrientationFactor_Sonic DECIMAL(8,3),                -- 取向因子 (声速法)
    Modulus_Sonic_GPa DECIMAL(10,2),                     -- 模量 (声速法 GPa)
    ResultChartPath NVARCHAR(500),                       -- (衍射图谱, 声速数据图)
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID)
);
GO
PRINT '表 Fiber_Microstructure_OrientationCrystallinity 已创建。';
GO

-- 13. 纤维微观结构 - SEM
PRINT '正在创建表: Fiber_Microstructure_SEM...';
CREATE TABLE Fiber_Microstructure_SEM (
    ImageID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    SampleName_SEM NVARCHAR(100),                        -- 试样名称
    Magnification VARCHAR(50),
    AcceleratingVoltage_kV DECIMAL(8,1),
    ImagePath NVARCHAR(500) NOT NULL,
    MorphologyDescription_SpecialFeatures NVARCHAR(MAX), -- 特殊形貌特征描述
    AnalysisResults NVARCHAR(MAX),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID)
);
GO
PRINT '表 Fiber_Microstructure_SEM 已创建。';
GO

-- 14. 纤维微观结构 - XPS
PRINT '正在创建表: Fiber_Microstructure_XPS...';
CREATE TABLE Fiber_Microstructure_XPS (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    Carbon_at_percent DECIMAL(8,2),                      -- C含量 (at.%)
    Oxygen_at_percent DECIMAL(8,2),                      -- O含量 (at.%)
    Nitrogen_at_percent DECIMAL(8,2),                    -- N含量 (at.%)
    OtherElements_XPS NVARCHAR(MAX),                     -- 其他元素含量
    ChemicalStateInfo_XPS NVARCHAR(MAX),                 -- 化学态信息
    ResultChartPath NVARCHAR(500),                       -- XPS谱图
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID)
);
GO
PRINT '表 Fiber_Microstructure_XPS 已创建。';
GO

-- 15. 树脂力学性能 - 拉伸
PRINT '正在创建表: Resin_Tensile_Properties...';
CREATE TABLE Resin_Tensile_Properties (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    ResinID BIGINT NOT NULL,
    TestStandard NVARCHAR(100),                          -- 如 ASTM D638
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    SpecimenType NVARCHAR(100),
    TestRate_mm_min DECIMAL(10,2),
    Temperature_C DECIMAL(8,1),
    TensileStrength_MPa DECIMAL(10,2),
    TensileStrength_CV_percent DECIMAL(8,2),
    YoungsModulus_MPa DECIMAL(10,2),
    YoungsModulus_CV_percent DECIMAL(8,2),
    ElongationAtBreak_percent DECIMAL(8,2),
    ElongationAtBreak_CV_percent DECIMAL(8,2),
    ResultChartPath NVARCHAR(500),
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (ResinID) REFERENCES Resins(ResinID)
);
GO
PRINT '表 Resin_Tensile_Properties 已创建。';
GO
-- (为树脂的其他力学性能如弯曲、压缩、冲击、硬度以及热性能创建类似表格)

-- 16. 纤维/树脂界面性能
PRINT '正在创建表: FiberResin_Interfacial_Properties...';
CREATE TABLE FiberResin_Interfacial_Properties (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    FiberID BIGINT NOT NULL,
    ResinID BIGINT NOT NULL,
    TestStandard NVARCHAR(100),                          -- 如 ASTM D3359 (附着力), 或特定界面测试方法
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    TestMethod_Detail NVARCHAR(MAX),                     -- 详细测试方法 (如 微滴拉脱, 单纤维拔出)
    ContactAngle_degrees DECIMAL(8,2),                   -- 接触角 (°)
    InterfacialShearStrength_IFSS_MPa DECIMAL(10,2),     -- 界面剪切强度 (MPa)
    BondStrength_MPa DECIMAL(10,2),                      -- 粘结强度 (MPa)
    FailureMode_Interface NVARCHAR(MAX),                 -- 界面失效模式
    ResultChartPath NVARCHAR(500),
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID),
    FOREIGN KEY (ResinID) REFERENCES Resins(ResinID)
);
GO
PRINT '表 FiberResin_Interfacial_Properties 已创建。';
GO

-- 17. 复合材料基本信息
PRINT '正在创建表: Composites...';
CREATE TABLE Composites (
    CompositeID BIGINT PRIMARY KEY IDENTITY(1,1),
    CompositeName NVARCHAR(200) NOT NULL,
    FiberID BIGINT,
    ResinID BIGINT,
    FiberContent_Volume_percent DECIMAL(8,2),
    FiberContent_Weight_percent DECIMAL(8,2),
    ReinforcementStructure NVARCHAR(100),                -- (UD, Woven fabric type)
    ManufacturingProcess_Detail NVARCHAR(MAX),
    CuringCycle_HotPressing_Params NVARCHAR(MAX),        -- (温度, 压力, 时间曲线)
    LayupSequence NVARCHAR(200),
    NumberOfLayers INT,
    Thickness_mm DECIMAL(10,3),
    ArealDensity_gsm DECIMAL(10,2),
    Porosity_percent DECIMAL(8,2),                       -- 孔隙率
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (FiberID) REFERENCES Fibers(FiberID),
    FOREIGN KEY (ResinID) REFERENCES Resins(ResinID)
);
GO
PRINT '表 Composites 已创建。';
GO

-- 18. 复合材料力学性能 - 拉伸
PRINT '正在创建表: Composite_Tensile_Properties...';
CREATE TABLE Composite_Tensile_Properties (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    CompositeID BIGINT NOT NULL,
    TestStandard NVARCHAR(100),                          -- 如 ASTM D3039
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestEquipment NVARCHAR(200),
    SpecimenGeometry_Dimensions NVARCHAR(200),
    LoadingDirection NVARCHAR(50),                       -- (0°, 90°, Warp, Weft)
    TestRate_mm_min DECIMAL(10,2),
    Temperature_C DECIMAL(8,1),
    TensileStrength_MPa DECIMAL(10,2),
    TensileStrength_CV_percent DECIMAL(8,2),
    TensileModulus_GPa DECIMAL(10,2),
    TensileModulus_CV_percent DECIMAL(8,2),
    PoissonRatio DECIMAL(8,3),
    ElongationAtBreak_percent DECIMAL(8,2),
    ElongationAtBreak_CV_percent DECIMAL(8,2),
    StressStrainCurveData_JSON NVARCHAR(MAX),
    FailureMode_Composite_Tensile NVARCHAR(MAX),
    ResultChartPath NVARCHAR(500),
    RawDataPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (CompositeID) REFERENCES Composites(CompositeID)
);
GO
PRINT '表 Composite_Tensile_Properties 已创建。';
GO
-- (为复合材料的压缩、弯曲、层间剪切ILSS、高应变率等性能创建类似表格)
-- 例如: Composite_Compression_Properties, Composite_Bending_Properties, Composite_ILSS_Properties, Composite_HighStrainRate_Properties

-- 19. 终端产品信息
PRINT '正在创建表: EndProducts...';
CREATE TABLE EndProducts (
    ProductID BIGINT PRIMARY KEY IDENTITY(1,1),
    ProductName NVARCHAR(200) NOT NULL,                  -- 产品名称 (如 XX型号防弹衣, YY型号头盔)
    Manufacturer NVARCHAR(200),
    ProductType NVARCHAR(100),                           -- (防弹衣, 防弹头盔, 防弹板)
    ProtectionLevel_Claimed NVARCHAR(100),               -- 宣称防护等级
    StructureDescription_ArealDensity NVARCHAR(MAX),     -- 结构描述、面密度等
    ManufacturingDate DATETIME,
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX)
);
GO
PRINT '表 EndProducts 已创建。';
GO

-- 20. 终端产品防弹性能测试
PRINT '正在创建表: Ballistic_Tests...';
CREATE TABLE Ballistic_Tests (
    TestID BIGINT PRIMARY KEY IDENTITY(1,1),
    ProductID BIGINT NOT NULL,                           -- 关联到EndProducts表
    TestStandard NVARCHAR(100) NOT NULL,
    TestDate DATETIME,
    TestingInstitution NVARCHAR(200),
    TestLocation NVARCHAR(200),
    ProjectileType_FullSpec NVARCHAR(200) NOT NULL,      -- 弹丸类型及详细规格
    ProjectileMass_g DECIMAL(10,2),
    ImpactVelocity_mps DECIMAL(10,1),
    V50_mps DECIMAL(10,1),
    BackingMaterial_Type NVARCHAR(100),                  -- 如 Roma Plastilina No.1
    BackingMaterial_CalibrationInfo NVARCHAR(MAX),       -- 油泥标定信息
    BFS_mm DECIMAL(8,2),
    PenetrationResult NVARCHAR(50) CHECK (PenetrationResult IN ('Complete Penetration', 'Partial Penetration', 'No Penetration', 'Perforation')),
    NumberOfLayersPenetrated INT,                        -- 穿透层数 (针对软质)
    NumberOfShots INT,
    ShotPattern_Placement NVARCHAR(MAX),                 -- 弹着点分布/描述
    AngleOfImpact_degrees DECIMAL(8,1) DEFAULT 0,        -- 着角 (默认0度)
    EnvironmentalConditions_Test NVARCHAR(200),
    FailureAnalysis_Observation NVARCHAR(MAX),
    Photos_Videos_Path NVARCHAR(MAX),                    -- 弹痕照片/视频路径 (可逗号分隔多个)
    TestReportPath NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX),
    FOREIGN KEY (ProductID) REFERENCES EndProducts(ProductID)
);
GO
PRINT '表 Ballistic_Tests 已创建。';
GO

-- 21. 文献与标准表
PRINT '正在创建表: Literature_Standards...';
CREATE TABLE Literature_Standards (
    DocID BIGINT PRIMARY KEY IDENTITY(1,1),
    DocumentType NVARCHAR(50) NOT NULL CHECK (DocumentType IN (N'文献', N'标准', N'测试方法', N'行业规范')),
    Title_StandardNo NVARCHAR(500) NOT NULL,
    Authors_IssuingBody NVARCHAR(500),
    PublicationYear_Date NVARCHAR(50),
    Journal_Publisher_Source NVARCHAR(200),
    Keywords NVARCHAR(MAX),
    Abstract_Scope_Description NVARCHAR(MAX),
    FilePath_URL NVARCHAR(500),
    EntryDate DATETIME DEFAULT GETDATE(),
    AddedBy NVARCHAR(100),
    Remarks NVARCHAR(MAX)
);
GO
PRINT '表 Literature_Standards 已创建。';
GO

-- 22. 系统使用说明/帮助文档
PRINT '正在创建表: SystemHelpDocs...';
CREATE TABLE SystemHelpDocs (
    HelpDocID INT PRIMARY KEY IDENTITY(1,1),
    Topic NVARCHAR(200) NOT NULL UNIQUE,
    Content NVARCHAR(MAX) NOT NULL,
    LastUpdated DATETIME DEFAULT GETDATE(),
    UpdatedBy NVARCHAR(100)
);
GO
PRINT '表 SystemHelpDocs 已创建。';
GO

-- -------- 表创建结束 --------

PRINT '所有核心数据表已成功添加到 UHMWPE_Ballistic_DB 数据库（如果之前不存在）。';
GO
