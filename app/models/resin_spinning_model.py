# app/models/resin_spinning_model.py
# “前端树脂与纺丝工艺参数” 表的 SQLAlchemy 模型定义

from app import db # 从 app 包导入 SQLAlchemy 实例
from sqlalchemy import func # 导入 func 用于数据库函数
# from app.models.user_model import UserModel # UserModel 会在关系中通过字符串引用

class ResinSpinningProcessModel(db.Model):
    """
    前端树脂与纺丝工艺表 (FrontendResinAndSpinningProcessParametersTable) 的 SQLAlchemy 模型。
    存储前端树脂材料特性及纺丝工艺相关的详细参数。
    """
    __tablename__ = '前端树脂与纺丝工艺表' # 指定表名，与 DDL 脚本一致

    # 使用英文属性名，映射到DDL中的中文列名
    record_id = db.Column("记录ID", db.Integer, primary_key=True, autoincrement=True, comment='记录唯一标识符，自增')
    batch_number = db.Column("批号", db.String(100), unique=True, nullable=False, comment='产品或实验批号，唯一且不为空')
    material_grade = db.Column("材料牌号", db.String(100), nullable=False, comment='材料的具体牌号或内部编号')
    supplier = db.Column("供应商", db.String(150), nullable=True, comment='原材料供应商名称')
    resin_type = db.Column("树脂类型", db.String(100), nullable=True, default='UHMWPE', comment='树脂类型，例如 "UHMWPE"')
    resin_molecular_weight_g_mol = db.Column("树脂分子量_g_mol", db.Numeric(18, 2), nullable=True, comment='树脂的重均或粘均分子量 (单位: g/mol)')
    polydispersity_index_pdi = db.Column("多分散系数_PDI", db.Numeric(10, 3), nullable=True, comment='树脂分子量分布的多分散系数 (Mw/Mn)')
    intrinsic_viscosity_dl_g = db.Column("特性粘度_dL_g", db.Numeric(10, 3), nullable=True, comment='树脂的特性粘度 (单位: dL/g)')
    melting_point_c = db.Column("熔点_C", db.Numeric(10, 2), nullable=True, comment='树脂或纤维的熔点 (单位: °C)')
    crystallinity_percent = db.Column("结晶度_percent", db.Numeric(10, 2), nullable=True, comment='材料的结晶度百分比 (单位: %)')
    spinning_method = db.Column("纺丝方法", db.String(100), nullable=True, comment='采用的纺丝方法')
    solvent_system = db.Column("溶剂体系", db.String(150), nullable=True, comment='纺丝过程中使用的溶剂体系')
    solution_concentration_percent = db.Column("原液浓度_percent", db.Numeric(10, 2), nullable=True, comment='纺丝原液的浓度 (单位: %)')
    spinning_temperature_c = db.Column("纺丝温度_C", db.Numeric(10, 2), nullable=True, comment='纺丝过程中的温度 (单位: °C)')
    spinneret_specifications = db.Column("喷丝板规格", db.String(100), nullable=True, comment='喷丝板的关键规格')
    coagulation_bath_composition = db.Column("凝固浴组成", db.String(150), nullable=True, comment='凝固浴的化学组成')
    coagulation_bath_temperature_c = db.Column("凝固浴温度_C", db.Numeric(10, 2), nullable=True, comment='凝固浴的温度 (单位: °C)')
    draw_ratio = db.Column("拉伸倍数", db.Numeric(10, 2), nullable=True, comment='纤维的总拉伸倍数或各阶段拉伸倍数')
    heat_treatment_temperature_c = db.Column("热处理温度_C", db.Numeric(10, 2), nullable=True, comment='纤维的热处理或退火温度 (单位: °C)')
    remarks = db.Column("备注", db.Text, nullable=True, comment='其他备注信息或特殊工艺说明') # NVARCHAR(MAX) maps to Text
    
    created_by_user_id = db.Column("创建用户ID", db.Integer, db.ForeignKey('用户表.用户ID'), nullable=True, comment='创建此记录的用户ID')
    last_modified_by_user_id = db.Column("最后修改用户ID", db.Integer, db.ForeignKey('用户表.用户ID'), nullable=True, comment='最后修改此记录的用户ID')
    
    created_at = db.Column("记录创建时间", db.DateTime, nullable=False, server_default=func.now(), comment='记录的创建时间戳')
    updated_at = db.Column("记录更新时间", db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment='记录的最后更新时间戳')

    # Relationships
    # Assuming UserModel has '用户ID' as its primary key mapped to an attribute like '用户ID' or 'user_id'
    # If UserModel uses english attribute 'user_id' for '用户ID', then principaljoin should reflect that.
    # For simplicity, we assume '用户表.用户ID' is the correct reference string for ForeignKey.
    # The backref names should be unique.
    creator = db.relationship('UserModel', foreign_keys=[created_by_user_id], backref=db.backref('resin_spinning_created_records', lazy='dynamic'))
    last_modifier = db.relationship('UserModel', foreign_keys=[last_modified_by_user_id], backref=db.backref('resin_spinning_modified_records', lazy='dynamic'))

    def __repr__(self):
        return f"<ResinSpinningProcessModel 记录ID={self.record_id}, 批号='{self.batch_number}'>"

    def to_dict(self, include_user_info=False):
        """
        将模型对象转换为字典，方便JSON序列化。
        :param include_user_info: 是否包含创建者和修改者用户信息
        :return: dict
        """
        data = {
            'record_id': self.record_id,
            'batch_number': self.batch_number,
            'material_grade': self.material_grade,
            'supplier': self.supplier,
            'resin_type': self.resin_type,
            'resin_molecular_weight_g_mol': float(self.resin_molecular_weight_g_mol) if self.resin_molecular_weight_g_mol else None,
            'polydispersity_index_pdi': float(self.polydispersity_index_pdi) if self.polydispersity_index_pdi else None,
            'intrinsic_viscosity_dl_g': float(self.intrinsic_viscosity_dl_g) if self.intrinsic_viscosity_dl_g else None,
            'melting_point_c': float(self.melting_point_c) if self.melting_point_c else None,
            'crystallinity_percent': float(self.crystallinity_percent) if self.crystallinity_percent else None,
            'spinning_method': self.spinning_method,
            'solvent_system': self.solvent_system,
            'solution_concentration_percent': float(self.solution_concentration_percent) if self.solution_concentration_percent else None,
            'spinning_temperature_c': float(self.spinning_temperature_c) if self.spinning_temperature_c else None,
            'spinneret_specifications': self.spinneret_specifications,
            'coagulation_bath_composition': self.coagulation_bath_composition,
            'coagulation_bath_temperature_c': float(self.coagulation_bath_temperature_c) if self.coagulation_bath_temperature_c else None,
            'draw_ratio': float(self.draw_ratio) if self.draw_ratio else None,
            'heat_treatment_temperature_c': float(self.heat_treatment_temperature_c) if self.heat_treatment_temperature_c else None,
            'remarks': self.remarks,
            'created_by_user_id': self.created_by_user_id,
            'last_modified_by_user_id': self.last_modified_by_user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_user_info:
            if self.creator:
                data['creator_username'] = self.creator.用户名 # Assuming UserModel has '用户名'
            if self.last_modifier:
                data['last_modifier_username'] = self.last_modifier.用户名
        return data

    @classmethod
    def find_by_batch_number(cls, batch_number: str):
        """根据批号查找记录"""
        return cls.query.filter_by(batch_number=batch_number).first()

    def save_to_db(self):
        """保存到数据库"""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """从数据库删除"""
        db.session.delete(self)
        db.session.commit()
