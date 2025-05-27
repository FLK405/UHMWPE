# app/services/attachment_service.py
# 附件管理相关的服务层逻辑

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app # To access app.config['UPLOAD_FOLDER']
from app import db
from app.models.attachment_model import AttachmentModel
# from app.models.user_model import UserModel # For type hinting if needed

class AttachmentService:
    """
    处理附件上传、下载、查询和删除等业务逻辑的服务类。
    """

    @staticmethod
    def upload_attachment(file_storage, parent_record_id: int, parent_module_name: str, user_id: int) -> tuple:
        """
        处理文件上传，保存文件并创建附件记录。
        :param file_storage: Werkzeug FileStorage object from request.files.
        :param parent_record_id: 关联的父记录ID.
        :param parent_module_name: 关联的父记录模块名称.
        :param user_id: 上传用户ID.
        :return: (success: bool, message_or_attachment_dict: str or dict, status_code: int)
        """
        if not file_storage:
            return False, "未提供文件。", 400
        if not parent_record_id or not parent_module_name:
            return False, "必须提供关联记录ID和模块名称。", 400

        original_filename = secure_filename(file_storage.filename)
        file_extension = os.path.splitext(original_filename)[1].lower()
        
        # Generate a unique filename to prevent collisions and for security
        stored_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        if not upload_folder:
            # current_app.logger.error("UPLOAD_FOLDER 未配置。") # Requires app context for logger
            print("UPLOAD_FOLDER 未配置。") # Fallback logging
            return False, "文件上传路径未配置。", 500
        
        # Ensure upload folder exists (though it should be created at app start)
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path_on_server = os.path.join(upload_folder, stored_filename)

        try:
            file_storage.save(file_path_on_server)
            file_size = os.path.getsize(file_path_on_server)

            attachment = AttachmentModel(
                parent_record_id=parent_record_id,
                parent_module_name=parent_module_name,
                original_file_name=original_filename,
                stored_file_name=stored_filename,
                file_path=stored_filename, # Store relative path (filename only if in UPLOAD_FOLDER root)
                file_type=file_storage.mimetype,
                file_size_bytes=file_size,
                uploaded_by_user_id=user_id
            )
            attachment.save_to_db()
            return True, attachment.to_dict(include_uploader_info=True), 201

        except Exception as e:
            # current_app.logger.error(f"文件上传失败: {e}")
            print(f"文件上传失败: {e}") # Fallback logging
            # Attempt to clean up if file was saved but DB entry failed
            if os.path.exists(file_path_on_server):
                try:
                    os.remove(file_path_on_server)
                except Exception as cleanup_e:
                    # current_app.logger.error(f"清理上传失败的文件时出错: {cleanup_e}")
                    print(f"清理上传失败的文件时出错: {cleanup_e}")
            return False, f"文件上传处理失败: {str(e)}", 500

    @staticmethod
    def get_attachments_for_record(parent_record_id: int, parent_module_name: str) -> list:
        """
        获取指定记录的所有附件信息。
        :param parent_record_id: 父记录ID.
        :param parent_module_name: 父记录模块名.
        :return: AttachmentModel 字典列表.
        """
        attachments = AttachmentModel.query.filter_by(
            parent_record_id=parent_record_id,
            parent_module_name=parent_module_name
        ).order_by(AttachmentModel.upload_timestamp.desc()).all()
        
        return [att.to_dict(include_uploader_info=True) for att in attachments]

    @staticmethod
    def get_attachment_by_id(attachment_id: int) -> AttachmentModel | None:
        """
        根据附件ID获取单个附件记录。
        :param attachment_id: 附件ID.
        :return: AttachmentModel 实例或 None.
        """
        return AttachmentModel.query.get(attachment_id)

    @staticmethod
    def delete_attachment(attachment_id: int, user_id: int, user_role: str) -> tuple: # Added user_id and role for permission check
        """
        删除附件记录和对应的文件。
        :param attachment_id: 要删除的附件ID.
        :param user_id: 当前操作用户ID.
        :param user_role: 当前操作用户角色 (e.g., "Admin").
        :return: (success: bool, message: str, status_code: int)
        """
        attachment = AttachmentModel.query.get(attachment_id)
        if not attachment:
            return False, f"附件ID {attachment_id} 未找到。", 404

        # 权限检查: 只有上传者或管理员可以删除 (简单示例)
        # A more robust RBAC check might involve checking specific 'CanDeleteAttachment' permission on the parent module.
        # For now, we'll allow uploader or 'Admin' role.
        if attachment.uploaded_by_user_id != user_id and user_role != 'Admin':
             return False, "您没有权限删除此附件。", 403


        upload_folder = current_app.config.get('UPLOAD_FOLDER')
        if not upload_folder:
            # current_app.logger.error("UPLOAD_FOLDER 未配置，无法删除文件。")
            print("UPLOAD_FOLDER 未配置，无法删除文件。")
            return False, "文件存储路径未配置，无法完成删除。", 500

        file_path_on_server = os.path.join(upload_folder, attachment.stored_file_name)

        try:
            # 1. 从数据库删除记录
            attachment.delete_from_db() # This commits the session
            
            # 2. 从文件系统删除文件
            if os.path.exists(file_path_on_server):
                os.remove(file_path_on_server)
            else:
                # current_app.logger.warning(f"附件文件 {file_path_on_server} 在文件系统中未找到，但数据库记录已删除。")
                print(f"警告: 附件文件 {file_path_on_server} 在文件系统中未找到，但数据库记录已删除。")

            return True, f"附件ID {attachment_id} 已成功删除。", 200

        except Exception as e:
            # current_app.logger.error(f"删除附件时发生错误: {e}")
            print(f"删除附件时发生错误: {e}")
            # If DB delete succeeded but file deletion failed, the DB change is already committed.
            # A more robust system might re-queue file deletion or log for manual cleanup.
            # For now, if delete_from_db() failed, it would have rolled back.
            # If os.remove() fails after successful DB commit, that's an orphaned file scenario.
            # For simplicity, we don't explicitly rollback DB here if file delete fails, as DB part was successful.
            return False, f"删除附件时发生内部错误: {str(e)}", 500
