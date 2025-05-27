# app/models/attachment_model.py
# “附件表” (AttachmentsTable) 的 SQLAlchemy 模型定义

from app import db # 从 app 包导入 SQLAlchemy 实例
from sqlalchemy import func # 导入 func 用于数据库函数
# from app.models.user_model import UserModel # UserModel 会在关系中通过字符串引用

class AttachmentModel(db.Model):
    """
    附件表 (AttachmentsTable) 的 SQLAlchemy 模型。
    存储与各个模块记录关联的附件文件信息。
    """
    __tablename__ = '附件表'

    attachment_id = db.Column("附件ID", db.Integer, primary_key=True, autoincrement=True, comment='附件唯一标识符，自增')
    parent_record_id = db.Column("关联记录ID", db.Integer, nullable=False, index=True, comment='关联的父记录ID')
    parent_module_name = db.Column("关联模块名称", db.String(100), nullable=False, index=True, comment='关联的父记录所在的模块名称')
    original_file_name = db.Column("原始文件名", db.String(255), nullable=False, comment='用户上传时的原始文件名')
    stored_file_name = db.Column("存储文件名", db.String(255), nullable=False, unique=True, comment='服务器上存储的唯一文件名')
    file_path = db.Column("文件路径", db.String(500), nullable=True, comment='文件在服务器上的相对存储路径')
    file_type = db.Column("文件类型", db.String(100), nullable=True, comment='文件的MIME类型')
    file_size_bytes = db.Column("文件大小_字节", db.BigInteger, nullable=True, comment='文件大小，单位为字节')
    
    uploaded_by_user_id = db.Column("上传用户ID", db.Integer, db.ForeignKey('用户表.用户ID', name='FK_附件表_上传用户ID_用户表'), nullable=True, comment='上传此附件的用户ID')
    # Note: Naming the FK constraint explicitly (e.g., name='FK_附件表_上传用户ID_用户表') can be good practice for some DB migration tools.
    
    upload_timestamp = db.Column("上传时间", db.DateTime, nullable=False, server_default=func.now(), comment='文件上传时间戳')

    # Relationship to UserModel
    uploader = db.relationship('UserModel', foreign_keys=[uploaded_by_user_id], backref=db.backref('uploaded_attachments', lazy='dynamic'))

    def __repr__(self):
        return f"<AttachmentModel 附件ID={self.attachment_id}, 文件名='{self.original_file_name}', 模块='{self.parent_module_name}', 父记录ID={self.parent_record_id}>"

    def to_dict(self, include_uploader_info=False):
        """
        将模型对象转换为字典，方便JSON序列化。
        :param include_uploader_info: 是否包含上传者用户信息
        :return: dict
        """
        data = {
            'attachment_id': self.attachment_id,
            'parent_record_id': self.parent_record_id,
            'parent_module_name': self.parent_module_name,
            'original_file_name': self.original_file_name,
            'stored_file_name': self.stored_file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size_bytes': self.file_size_bytes,
            'uploaded_by_user_id': self.uploaded_by_user_id,
            'upload_timestamp': self.upload_timestamp.isoformat() if self.upload_timestamp else None,
        }
        if include_uploader_info and self.uploader:
            data['uploader_username'] = self.uploader.用户名 # Assuming UserModel has '用户名'
        return data

    def save_to_db(self):
        """保存到数据库"""
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """从数据库删除"""
        # Note: Actual file deletion from filesystem should be handled in the service layer.
        db.session.delete(self)
        db.session.commit()
