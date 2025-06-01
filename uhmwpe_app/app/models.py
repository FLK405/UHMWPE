from . import db
from sqlalchemy.sql import func
from sqlalchemy import Text, Numeric, DateTime

# Placeholder for actual models based on setup_UHMWPE_Ballistic_DB.sql

class User(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    FirstName = db.Column(db.String(50))
    LastName = db.Column(db.String(50))
    RoleID = db.Column(db.Integer, db.ForeignKey('Roles.RoleID'))
    IsActive = db.Column(db.Boolean, default=True)
    LastLoginDate = db.Column(DateTime)
    DateCreated = db.Column(DateTime, default=func.now())
    DateModified = db.Column(DateTime, default=func.now(), onupdate=func.now())

    role = db.relationship('Role', back_populates='users')

    def __repr__(self):
        return f'<User {self.Username}>'

class Role(db.Model):
    __tablename__ = 'Roles'
    RoleID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    RoleName = db.Column(db.String(50), unique=True, nullable=False)
    Description = db.Column(db.String(255))

    users = db.relationship('User', back_populates='role')

    def __repr__(self):
        return f'<Role {self.RoleName}>'

# Example Material Table (will need to be updated with actual schema)
class Material(db.Model):
    __tablename__ = 'Materials' # Assuming a table name
    MaterialID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    MaterialName = db.Column(db.String(100), nullable=False)
    Description = db.Column(Text)
    Density = db.Column(Numeric(10, 4)) # Example: 10 total digits, 4 after decimal
    TensileStrength = db.Column(Numeric(10, 4))
    YoungModulus = db.Column(Numeric(10, 4))
    DateAdded = db.Column(DateTime, default=func.now())
    AddedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))

    adder = db.relationship('User')

    def __repr__(self):
        return f'<Material {self.MaterialName}>'

# We need the actual content of setup_UHMWPE_Ballistic_DB.sql to create the correct models.
# For now, these are illustrative.
# For NVARCHAR(MAX) or VARCHAR(MAX) -> use Text
# For DATETIME -> use DateTime
# For DECIMAL -> use Numeric
# For relationships and foreign keys, use db.ForeignKey and db.relationship

# Based on the provided SQL schema, the following models would be created.
# I will assume the SQL schema is similar to the one used in a previous related project.

class Literature_Standard(db.Model):
    __tablename__ = 'Literature_Standard'
    DocumentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    DocumentType = db.Column(db.String(50), nullable=False) # e.g., 'Standard', 'Paper', 'Book', 'Report'
    Title_StandardNo = db.Column(db.String(255), nullable=False)
    Authors_IssuingBody = db.Column(db.String(500))
    PublicationYear = db.Column(db.Integer)
    Journal_Publisher = db.Column(db.String(255))
    Volume_Issue_Pages = db.Column(db.String(100))
    DOI_ISBN_URL = db.Column(db.String(255))
    Abstract_Scope = db.Column(Text)
    Keywords = db.Column(db.String(255))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())
    AddedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))

    uploader = db.relationship('User')

class Resins(db.Model):
    __tablename__ = 'Resins'
    ResinID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ResinName = db.Column(db.String(100), nullable=False, unique=True)
    Manufacturer = db.Column(db.String(100))
    ProductionDate = db.Column(DateTime)
    IntrinsicViscosity = db.Column(Numeric(10, 4)) # dL/g
    MolecularWeight_Mn = db.Column(Numeric(15, 2)) # g/mol
    MolecularWeight_Mw = db.Column(Numeric(15, 2)) # g/mol
    MolecularWeight_Mz = db.Column(Numeric(15, 2)) # g/mol
    PolydispersityIndex = db.Column(Numeric(10, 4)) # Mw/Mn
    ComonomerType = db.Column(db.String(50))
    ComonomerContent = db.Column(Numeric(10, 4)) # %
    AdditiveType = db.Column(db.String(50))
    AdditiveContent = db.Column(Numeric(10, 4)) # %
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())
    AddedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))

    uploader = db.relationship('User')
    spinning_processes = db.relationship('PrecursorResin_SpinningProcess', back_populates='resin')
    tensile_properties = db.relationship('Resin_Tensile_Properties', back_populates='resin', cascade="all, delete-orphan")
    interfacial_properties = db.relationship('FiberResin_Interfacial_Properties', back_populates='resin')
    composites = db.relationship('Composites', back_populates='resin')


class PrecursorResin_SpinningProcess(db.Model):
    __tablename__ = 'PrecursorResin_SpinningProcess'
    SpinningProcessID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ProcessName = db.Column(db.String(100), nullable=False, unique=True)
    ResinID = db.Column(db.Integer, db.ForeignKey('Resins.ResinID'), nullable=False)
    Solvent = db.Column(db.String(100))
    ResinConcentration = db.Column(Numeric(10, 4)) # wt%
    SpinningTemperature = db.Column(Numeric(10, 2)) # °C
    SpinneretDiameter = db.Column(Numeric(10, 4)) # mm
    AirGapDistance = db.Column(Numeric(10, 2)) # mm
    CoagulationBathComposition = db.Column(db.String(255))
    CoagulationBathTemperature = db.Column(Numeric(10, 2)) # °C
    DrawingStages = db.Column(db.Integer)
    TotalDrawRatio = db.Column(Numeric(10, 2))
    PostProcessingDetails = db.Column(Text) # e.g., heat treatment, surface modification
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())
    AddedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))

    resin = db.relationship('Resins', back_populates='spinning_processes')
    uploader = db.relationship('User')
    fibers = db.relationship('Fibers', back_populates='spinning_process')


class Fibers(db.Model):
    __tablename__ = 'Fibers'
    FiberID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberName = db.Column(db.String(100), nullable=False, unique=True)
    SpinningProcessID = db.Column(db.Integer, db.ForeignKey('PrecursorResin_SpinningProcess.SpinningProcessID'), nullable=False)
    LinearDensity = db.Column(Numeric(10, 4)) # denier or dtex
    Diameter = db.Column(Numeric(10, 4)) # µm
    ProductionDate = db.Column(DateTime)
    Manufacturer_ResearchGroup = db.Column(db.String(100))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())
    AddedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))

    spinning_process = db.relationship('PrecursorResin_SpinningProcess', back_populates='fibers')
    uploader = db.relationship('User')

    # Relationships to property tables
    molecular_weights = db.relationship('Fiber_MolecularWeight', back_populates='fiber', cascade="all, delete-orphan")
    tensile_properties = db.relationship('Fiber_Tensile_Properties', back_populates='fiber', cascade="all, delete-orphan")
    creep_properties = db.relationship('Fiber_Creep_Properties', back_populates='fiber', cascade="all, delete-orphan")
    dynamic_tensile_properties = db.relationship('Fiber_DynamicTensile_Properties', back_populates='fiber', cascade="all, delete-orphan")
    thermal_dsc = db.relationship('Fiber_Thermal_DSC', back_populates='fiber', cascade="all, delete-orphan")
    thermal_tga = db.relationship('Fiber_Thermal_TGA', back_populates='fiber', cascade="all, delete-orphan")
    thermal_conductivity = db.relationship('Fiber_Thermal_Conductivity', back_populates='fiber', cascade="all, delete-orphan")
    microstructure_phase = db.relationship('Fiber_Microstructure_PhaseStructure', back_populates='fiber', cascade="all, delete-orphan")
    microstructure_orientation = db.relationship('Fiber_Microstructure_OrientationCrystallinity', back_populates='fiber', cascade="all, delete-orphan")
    microstructure_sem = db.relationship('Fiber_Microstructure_SEM', back_populates='fiber', cascade="all, delete-orphan")
    microstructure_xps = db.relationship('Fiber_Microstructure_XPS', back_populates='fiber', cascade="all, delete-orphan")
    interfacial_properties = db.relationship('FiberResin_Interfacial_Properties', back_populates='fiber')
    composites = db.relationship('Composites', back_populates='fiber')


# --- Fiber Property Tables ---
class Fiber_MolecularWeight(db.Model):
    __tablename__ = 'Fiber_MolecularWeight'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    TestMethod = db.Column(db.String(100)) # e.g., GPC, Viscometry
    TestConditions = db.Column(Text)
    IntrinsicViscosity = db.Column(Numeric(10, 4)) # dL/g
    MolecularWeight_Mn = db.Column(Numeric(15, 2)) # g/mol
    MolecularWeight_Mw = db.Column(Numeric(15, 2)) # g/mol
    MolecularWeight_Mz = db.Column(Numeric(15, 2)) # g/mol
    PolydispersityIndex = db.Column(Numeric(10, 4)) # Mw/Mn
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='molecular_weights')
    tester = db.relationship('User')


class Fiber_Tensile_Properties(db.Model):
    __tablename__ = 'Fiber_Tensile_Properties'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    TestMethod_Standard = db.Column(db.String(100)) # e.g., ASTM D3822
    TestTemperature = db.Column(Numeric(10, 2)) # °C
    StrainRate = db.Column(Numeric(10, 4)) # /min or /s
    GaugeLength = db.Column(Numeric(10, 2)) # mm
    TensileStrength = db.Column(Numeric(10, 3)) # GPa or MPa or cN/dtex
    TensileModulus = db.Column(Numeric(10, 3)) # GPa or cN/dtex
    ElongationAtBreak = db.Column(Numeric(10, 2)) # %
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='tensile_properties')
    tester = db.relationship('User')


class Fiber_Creep_Properties(db.Model):
    __tablename__ = 'Fiber_Creep_Properties'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    TestMethod_Standard = db.Column(db.String(100))
    TestTemperature = db.Column(Numeric(10, 2)) # °C
    AppliedStress = db.Column(Numeric(10, 3)) # MPa or GPa
    TestDuration = db.Column(Numeric(10, 2)) # hours
    CreepStrain = db.Column(Numeric(10, 4)) # %
    CreepRate = db.Column(Numeric(10, 6)) # %/hour or similar
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='creep_properties')
    tester = db.relationship('User')


class Fiber_DynamicTensile_Properties(db.Model): # (e.g., SHPB, impact)
    __tablename__ = 'Fiber_DynamicTensile_Properties'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    TestMethod_Equipment = db.Column(db.String(100)) # e.g., SHPB, Instron High Rate
    StrainRate = db.Column(Numeric(10, 0)) # /s (typically high)
    TestTemperature = db.Column(Numeric(10, 2)) # °C
    DynamicTensileStrength = db.Column(Numeric(10, 3)) # GPa or MPa
    DynamicTensileModulus = db.Column(Numeric(10, 3)) # GPa
    ElongationAtBreak_Dynamic = db.Column(Numeric(10, 2)) # %
    EnergyAbsorption = db.Column(Numeric(10, 2)) # J/g or J/m
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='dynamic_tensile_properties')
    tester = db.relationship('User')


class Fiber_Thermal_DSC(db.Model): # Differential Scanning Calorimetry
    __tablename__ = 'Fiber_Thermal_DSC'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    TestMethod_Standard = db.Column(db.String(100))
    HeatingRate = db.Column(Numeric(10, 2)) # °C/min
    Atmosphere = db.Column(db.String(50)) # e.g., Nitrogen, Air
    MeltingTemperature_Tm = db.Column(Numeric(10, 2)) # °C
    EnthalpyOfFusion = db.Column(Numeric(10, 2)) # J/g
    CrystallizationTemperature_Tc = db.Column(Numeric(10, 2)) # °C (on cooling)
    EnthalpyOfCrystallization = db.Column(Numeric(10, 2)) # J/g (on cooling)
    GlassTransitionTemperature_Tg = db.Column(Numeric(10, 2)) # °C
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text) # Store raw data path or key points
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='thermal_dsc')
    tester = db.relationship('User')


class Fiber_Thermal_TGA(db.Model): # Thermogravimetric Analysis
    __tablename__ = 'Fiber_Thermal_TGA'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    TestMethod_Standard = db.Column(db.String(100))
    HeatingRate = db.Column(Numeric(10, 2)) # °C/min
    Atmosphere = db.Column(db.String(50)) # e.g., Nitrogen, Air
    DecompositionOnsetTemperature = db.Column(Numeric(10, 2)) # °C (e.g., 5% weight loss)
    TemperatureAtMaxDecompositionRate = db.Column(Numeric(10, 2)) # °C
    ResidueAtTargetTemperature = db.Column(Numeric(10, 2)) # % (e.g., at 800°C)
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text) # Store raw data path or key points
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='thermal_tga')
    tester = db.relationship('User')


class Fiber_Thermal_Conductivity(db.Model):
    __tablename__ = 'Fiber_Thermal_Conductivity'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    TestMethod = db.Column(db.String(100)) # e.g., Laser Flash, Hot Disk
    TestTemperature = db.Column(Numeric(10, 2)) # °C
    ThermalConductivity = db.Column(Numeric(10, 4)) # W/(m·K)
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='thermal_conductivity')
    tester = db.relationship('User')


class Fiber_Microstructure_PhaseStructure(db.Model): # (e.g., WAXS, SAXS for crystal structure, phase content)
    __tablename__ = 'Fiber_Microstructure_PhaseStructure'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    TestMethod = db.Column(db.String(100)) # e.g., WAXS, SAXS, Raman
    CrystalSystem = db.Column(db.String(50)) # e.g., Orthorhombic, Monoclinic
    LatticeParameters = db.Column(db.String(100)) # a, b, c, alpha, beta, gamma
    PercentCrystallinity = db.Column(Numeric(10, 2)) # %
    CrystalSize_Lc = db.Column(Numeric(10, 2)) # nm
    LongPeriod_Lp = db.Column(Numeric(10, 2)) # nm (from SAXS)
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text) # Store raw data path or key parameters
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='microstructure_phase')
    tester = db.relationship('User')


class Fiber_Microstructure_OrientationCrystallinity(db.Model): # (e.g., WAXS pole figures, birefringence)
    __tablename__ = 'Fiber_Microstructure_OrientationCrystallinity'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    TestMethod = db.Column(db.String(100)) # e.g., WAXS Pole Figure, Birefringence, FTIR Dichroism
    OrientationParameter_fc = db.Column(Numeric(10, 4)) # Herman's orientation factor
    Birefringence = db.Column(Numeric(10, 4))
    DichroicRatio = db.Column(Numeric(10, 2))
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='microstructure_orientation')
    tester = db.relationship('User')


class Fiber_Microstructure_SEM(db.Model): # Scanning Electron Microscopy
    __tablename__ = 'Fiber_Microstructure_SEM'
    ImageID = db.Column(db.Integer, primary_key=True, autoincrement=True) # Changed from TestID to ImageID as it's image focused
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    MicroscopyEquipment = db.Column(db.String(100))
    Magnification = db.Column(db.String(50)) # e.g., 5000x, can be text if varied
    AcceleratingVoltage = db.Column(Numeric(10, 2)) # kV
    ImagePath = db.Column(db.String(500), nullable=False) # Path to stored image
    Observations = db.Column(Text) # Description of morphology, defects, etc.
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='microstructure_sem')
    tester = db.relationship('User')


class Fiber_Microstructure_XPS(db.Model): # X-ray Photoelectron Spectroscopy
    __tablename__ = 'Fiber_Microstructure_XPS'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    Equipment = db.Column(db.String(100))
    XraySource = db.Column(db.String(50)) # e.g., Al K-alpha
    SurveyScanInfo = db.Column(Text) # e.g., pass energy, elements detected
    HighResScanInfo_C1s = db.Column(Text) # Deconvolution details for C1s
    HighResScanInfo_O1s = db.Column(Text) # Deconvolution details for O1s
    AtomicConcentration_C = db.Column(Numeric(10, 2)) # %
    AtomicConcentration_O = db.Column(Numeric(10, 2)) # %
    AtomicConcentration_N = db.Column(Numeric(10, 2)) # % (if applicable)
    OtherElementsDetected = db.Column(db.String(255))
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='microstructure_xps')
    tester = db.relationship('User')


# --- Resin Property Tables ---
class Resin_Tensile_Properties(db.Model): # For bulk resin samples
    __tablename__ = 'Resin_Tensile_Properties'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ResinID = db.Column(db.Integer, db.ForeignKey('Resins.ResinID'), nullable=False)
    SamplePreparation = db.Column(Text) # e.g., injection molded, compression molded
    TestMethod_Standard = db.Column(db.String(100)) # e.g., ASTM D638
    TestTemperature = db.Column(Numeric(10, 2)) # °C
    StrainRate = db.Column(Numeric(10, 4)) # /min or /s
    TensileStrength = db.Column(Numeric(10, 3)) # MPa
    TensileModulus = db.Column(Numeric(10, 3)) # GPa or MPa
    ElongationAtBreak = db.Column(Numeric(10, 2)) # %
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())

    resin = db.relationship('Resins', back_populates='tensile_properties')
    tester = db.relationship('User')


# --- Interface Property Tables ---
class FiberResin_Interfacial_Properties(db.Model):
    __tablename__ = 'FiberResin_Interfacial_Properties'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    ResinID = db.Column(db.Integer, db.ForeignKey('Resins.ResinID'), nullable=False) # Matrix resin used
    TestMethod = db.Column(db.String(100)) # e.g., Microbond, Pull-out, Fragmentation
    TestTemperature = db.Column(Numeric(10, 2)) # °C
    InterfacialShearStrength_IFSS = db.Column(Numeric(10, 3)) # MPa
    FailureMode = db.Column(db.String(255)) # e.g., adhesive, cohesive, fiber pull-out
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())

    fiber = db.relationship('Fibers', back_populates='interfacial_properties')
    resin = db.relationship('Resins', back_populates='interfacial_properties')
    tester = db.relationship('User')


# --- Composite Tables ---
class Composites(db.Model):
    __tablename__ = 'Composites'
    CompositeID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CompositeName = db.Column(db.String(100), nullable=False, unique=True)
    FiberID = db.Column(db.Integer, db.ForeignKey('Fibers.FiberID'), nullable=False)
    ResinID = db.Column(db.Integer, db.ForeignKey('Resins.ResinID'), nullable=False) # Matrix resin
    ManufacturingProcess = db.Column(db.String(100)) # e.g., Filament Winding, Compression Molding, Autoclave
    FiberVolumeFraction = db.Column(Numeric(10, 4)) # % or fraction
    VoidContent = db.Column(Numeric(10, 4)) # %
    PlyStackingSequence = db.Column(db.String(100)) # e.g., [0/90]s, UD
    CuringCycleDetails = db.Column(Text) # Temp, pressure, time
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())
    AddedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))

    fiber = db.relationship('Fibers', back_populates='composites')
    resin = db.relationship('Resins', back_populates='composites')
    uploader = db.relationship('User')
    tensile_properties = db.relationship('Composite_Tensile_Properties', back_populates='composite', cascade="all, delete-orphan")
    # Add other composite property relationships here, e.g., flexural, impact, ballistic


class Composite_Tensile_Properties(db.Model):
    __tablename__ = 'Composite_Tensile_Properties'
    TestID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CompositeID = db.Column(db.Integer, db.ForeignKey('Composites.CompositeID'), nullable=False)
    TestMethod_Standard = db.Column(db.String(100)) # e.g., ASTM D3039
    TestDirection = db.Column(db.String(50)) # e.g., 0-degree, 90-degree, In-plane shear
    TestTemperature = db.Column(Numeric(10, 2)) # °C
    StrainRate = db.Column(Numeric(10, 4)) # /min or /s
    TensileStrength = db.Column(Numeric(10, 3)) # MPa
    TensileModulus = db.Column(Numeric(10, 3)) # GPa
    PoissonRatio = db.Column(Numeric(10, 3)) # e.g., v12
    ElongationAtBreak = db.Column(Numeric(10, 2)) # %
    FailureMode = db.Column(Text)
    TestDate = db.Column(DateTime)
    PerformedByUserID = db.Column(db.Integer, db.ForeignKey('Users.UserID'))
    Notes = db.Column(Text)
    DateAdded = db.Column(DateTime, default=func.now())

    composite = db.relationship('Composites', back_populates='tensile_properties')
    tester = db.relationship('User')


# Add other tables as per the full SQL schema:
# - Images (if there's a dedicated table for SEM/Optical images, beyond just a path)
# - BallisticPerformance (main table for ballistic tests)
# - ProjectileDetails (linked to BallisticPerformance)
# - TargetDetails (linked to BallisticPerformance)
# - TestSetup (linked to BallisticPerformance)
# - ImpactConditions (linked to BallisticPerformance)
# - PerformanceMetrics (linked to BallisticPerformance)
# - FailureAnalysis (linked to BallisticPerformance)
# - SimulationData (if FEM/simulations are part of the DB)
# - etc.

# For now, the above covers a good range of material science data.
# The actual `setup_UHMWPE_Ballistic_DB.sql` would be needed for 100% accuracy.
