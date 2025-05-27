# app/routes/attachment_routes.py
# 附件管理相关的API路由定义

import os
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from app.services.attachment_service import AttachmentService
from app.services.auth_service import AuthService # 用于获取当前用户ID和角色
from app.utils.decorators import login_required, permission_required # 权限装饰器

# 创建蓝图
attachment_bp = Blueprint('attachment_bp', __name__, url_prefix='/api/attachments')

# 模块名称常量，用于RBAC权限检查
# 这些应该与数据库中模块表（ModulesTable）的记录一致。
# TODO: Consider a shared constants file or enum for module names if they are used in many places.
MODULE_RESIN_SPINNING = "前端树脂与纺丝工艺表" 
# Add other module names here as needed, e.g., MODULE_FIBER_PERFORMANCE = "纤维性能表"

@attachment_bp.route('/upload/resin-spinning/<int:record_id>', methods=['POST'])
@login_required
# 'CanWrite' on the parent module implies permission to add attachments to its records.
# Alternatively, a more granular 'CanUploadToModule' or 'CanAddAttachment' permission could be used.
@permission_required(MODULE_RESIN_SPINNING, 'CanWrite') 
def upload_resin_spinning_attachment(record_id):
    """
    为指定的前端树脂与纺丝工艺参数记录上传附件。
    请求应为 multipart/form-data，包含一个名为 'file' 的文件字段。
    """
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "请求中未找到文件部分。"}), 400
    
    file_storage = request.files['file']
    if file_storage.filename == '':
        return jsonify({"success": False, "message": "未选择任何文件。"}), 400

    current_user_id = AuthService.get_current_user_id()
    if not current_user_id: # Should be caught by @login_required
        return jsonify({"success": False, "message": "无法获取当前用户信息。"}), 401

    success, result, status_code = AttachmentService.upload_attachment(
        file_storage=file_storage,
        parent_record_id=record_id,
        parent_module_name=MODULE_RESIN_SPINNING,
        user_id=current_user_id
    )

    if success:
        return jsonify({"success": True, "message": "附件上传成功。", "attachment": result}), status_code
    else:
        return jsonify({"success": False, "message": result}), status_code


@attachment_bp.route('/resin-spinning/<int:record_id>', methods=['GET'])
@login_required
@permission_required(MODULE_RESIN_SPINNING, 'CanRead')
def list_resin_spinning_attachments(record_id):
    """
    列出指定前端树脂与纺丝工艺参数记录的所有附件。
    """
    try:
        attachments = AttachmentService.get_attachments_for_record(
            parent_record_id=record_id,
            parent_module_name=MODULE_RESIN_SPINNING
        )
        return jsonify({"success": True, "attachments": attachments}), 200
    except Exception as e:
        # Log e
        return jsonify({"success": False, "message": f"获取附件列表时发生错误: {str(e)}"}), 500


@attachment_bp.route('/<int:attachment_id>/download', methods=['GET'])
@login_required
# For downloading, we generally check 'CanRead' on the *parent* module.
# This requires knowing the parent module of the attachment.
# A more complex check might be needed if attachments can be orphaned or if direct attachment permission is desired.
# For now, this endpoint is generic; specific permission might need to be checked in the service or by joining.
# A simpler approach for now: If a user can read the parent record, they can download its attachments.
# The specific module permission decorator is thus not directly applicable here without more info.
# We will assume that if a user has access to the attachment_id, they have permission.
# A better way: check permission against parent_module_name stored in attachment.
def download_attachment(attachment_id):
    """
    下载指定的附件文件。
    """
    attachment = AttachmentService.get_attachment_by_id(attachment_id)
    if not attachment:
        return jsonify({"success": False, "message": "附件未找到。"}), 404

    # Permission check: Can the current user read the parent module?
    # This logic needs to be robust. Example:
    user_has_permission = False
    current_user = AuthService.get_current_user() # Gets the UserModel instance
    if current_user:
        # Dynamically check permission for the attachment's parent module
        from app.services.rbac_service import RbacService # Local import to avoid circular dependency issues at top level
        user_has_permission = RbacService.check_permission(
            user_id=current_user.用户ID, 
            module_name=attachment.parent_module_name, 
            action='CanRead' # Assuming 'CanRead' on parent module allows downloading its attachments
        )

    if not user_has_permission:
         return jsonify({"success": False, "message": "您没有权限下载此附件。"}), 403


    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    if not upload_folder:
        return jsonify({"success": False, "message": "文件存储路径未配置。"}), 500

    try:
        return send_from_directory(
            upload_folder,
            attachment.stored_file_name,
            as_attachment=True, # Triggers download dialog
            download_name=attachment.original_file_name # Sets the filename for the user
        )
    except FileNotFoundError:
        return jsonify({"success": False, "message": "文件在服务器上未找到。"}), 404
    except Exception as e:
        # Log e
        return jsonify({"success": False, "message": f"下载文件时发生错误: {str(e)}"}), 500


@attachment_bp.route('/<int:attachment_id>', methods=['DELETE'])
@login_required
# Similar to download, deletion permission might depend on the parent module or specific 'CanDeleteAttachment' perm.
# For simplicity, if a user has 'CanDelete' on the parent module, they can delete its attachments.
# The service layer also has a basic check (uploader or Admin).
def delete_attachment_route(attachment_id):
    """
    删除指定的附件（包括文件和数据库记录）。
    """
    current_user = AuthService.get_current_user()
    if not current_user:
        return jsonify({"success": False, "message": "无法获取当前用户信息。"}), 401

    attachment = AttachmentService.get_attachment_by_id(attachment_id)
    if not attachment:
        return jsonify({"success": False, "message": "附件未找到。"}), 404

    # Permission check against parent module
    from app.services.rbac_service import RbacService
    can_delete_parent_module_item = RbacService.check_permission(
        user_id=current_user.用户ID,
        module_name=attachment.parent_module_name,
        action='CanDelete' # Assuming 'CanDelete' on parent implies deleting its attachments
    )
    
    # Fallback to service layer's check if not specifically allowed by parent module's CanDelete
    # (e.g., uploader can delete their own attachment even if they can't delete the parent record)
    # The service layer check (is_uploader or is_admin) acts as a final gate.
    if not can_delete_parent_module_item and attachment.uploaded_by_user_id != current_user.用户ID and current_user.role.角色名称 != 'Admin':
         return jsonify({"success": False, "message": "您没有权限删除此附件。"}), 403


    success, message, status_code = AttachmentService.delete_attachment(
        attachment_id=attachment_id, 
        user_id=current_user.用户ID, 
        user_role=current_user.role.角色名称 # Pass role for service-level check
    )

    if success:
        return jsonify({"success": True, "message": message}), status_code
    else:
        return jsonify({"success": False, "message": message}), status_code
