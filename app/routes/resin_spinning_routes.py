# app/routes/resin_spinning_routes.py
# "前端树脂与纺丝工艺参数" 模块的API路由定义

from flask import Blueprint, request, jsonify
from app.services.resin_spinning_service import ResinSpinningService
from app.services.auth_service import AuthService # 用于获取当前用户ID
from app.utils.decorators import login_required, permission_required # 权限装饰器

# 创建蓝图
# 注意：模块名称 "前端树脂与纺丝工艺表" 用于权限检查，必须与数据库中模块表（ModulesTable）的记录一致。
MODULE_NAME_FOR_RBAC = "前端树脂与纺丝工艺表" 

resin_spinning_bp = Blueprint(
    'resin_spinning_bp', 
    __name__, 
    url_prefix='/api/resin-spinning' # 使用 /api 前缀以区分前端路由
)

@resin_spinning_bp.route('/', methods=['POST'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanWrite')
def create_resin_spinning_record():
    """
    创建一条新的前端树脂与纺丝工艺参数记录。
    请求体应为JSON格式，包含记录的各个字段。
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请求体不能为空且必须是JSON格式。"}), 400

    current_user_id = AuthService.get_current_user_id()
    if not current_user_id: # 理论上 @login_required 会处理，但双重检查无害
        return jsonify({"success": False, "message": "无法获取当前用户信息，请重新登录。"}), 401
        
    success, result, status_code = ResinSpinningService.create_record(data=data, user_id=current_user_id)

    if success:
        return jsonify({"success": True, "message": "记录创建成功。", "record": result}), status_code
    else:
        return jsonify({"success": False, "message": result}), status_code

@resin_spinning_bp.route('/<int:record_id>', methods=['GET'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanRead')
def get_resin_spinning_record(record_id):
    """
    根据记录ID获取单个前端树脂与纺丝工艺参数记录。
    """
    success, result, status_code = ResinSpinningService.get_record_by_id(record_id)
    
    if success:
        return jsonify({"success": True, "record": result}), status_code
    else:
        return jsonify({"success": False, "message": result}), status_code

@resin_spinning_bp.route('/', methods=['GET'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanRead')
def get_all_resin_spinning_records():
    """
    获取前端树脂与纺丝工艺参数记录列表（支持分页和过滤）。
    查询参数:
        - page (int, optional): 页码，默认为1。
        - per_page (int, optional): 每页记录数，默认为10。
        - material_grade (str, optional): 按材料牌号过滤 (模糊匹配)。
        - batch_number (str, optional): 按批号过滤 (模糊匹配)。
        - resin_type (str, optional): 按树脂类型过滤 (模糊匹配)。
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    filters = {
        'material_grade': request.args.get('material_grade', type=str),
        'batch_number': request.args.get('batch_number', type=str),
        'resin_type': request.args.get('resin_type', type=str)
        # 可以从 request.args 添加更多过滤参数
    }
    # 清除值为None的过滤器，以避免传递它们
    filters = {k: v for k, v in filters.items() if v is not None}

    success, result, status_code = ResinSpinningService.get_all_records(page=page, per_page=per_page, filters=filters)

    if success:
        return jsonify({"success": True, **result}), status_code # result 包含 records, total, pages 等
    else:
        return jsonify({"success": False, "message": result}), status_code

@resin_spinning_bp.route('/<int:record_id>', methods=['PUT'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanWrite')
def update_resin_spinning_record(record_id):
    """
    更新指定ID的前端树脂与纺丝工艺参数记录。
    请求体应为JSON格式，包含要更新的字段。
    """
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "请求体不能为空且必须是JSON格式。"}), 400

    current_user_id = AuthService.get_current_user_id()
    if not current_user_id:
        return jsonify({"success": False, "message": "无法获取当前用户信息，请重新登录。"}), 401

    success, result, status_code = ResinSpinningService.update_record(
        record_id=record_id, 
        data=data, 
        user_id=current_user_id
    )

    if success:
        return jsonify({"success": True, "message": "记录更新成功。", "record": result}), status_code
    else:
        return jsonify({"success": False, "message": result}), status_code

@resin_spinning_bp.route('/<int:record_id>', methods=['DELETE'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanDelete')
def delete_resin_spinning_record(record_id):
    """
    删除指定ID的前端树脂与纺丝工艺参数记录。
    """
    current_user_id = AuthService.get_current_user_id() # 虽然服务层目前没用，但记录操作者可能有用
    if not current_user_id:
        return jsonify({"success": False, "message": "无法获取当前用户信息，请重新登录。"}), 401
        
    success, message, status_code = ResinSpinningService.delete_record(record_id)

    if success:
        return jsonify({"success": True, "message": message}), status_code
    else:
        return jsonify({"success": False, "message": message}), status_code

# 可以在蓝图级别添加错误处理器，处理例如 RBAC 权限不足的通用情况等
# @resin_spinning_bp.errorhandler(Exception)
# def handle_resin_spinning_errors(e):
#     # Log e
#     return jsonify({"success": False, "message": "树脂纺丝模块发生内部错误。"}), 500

# --- Batch Import Endpoint ---
import pandas as pd
from werkzeug.utils import secure_filename # For secure file handling (optional but good practice)
import os

# Define allowed extensions for file upload for basic security
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

import io # For in-memory file handling
from flask import Response # For sending file response

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@resin_spinning_bp.route('/batch-import', methods=['POST'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanImport')
def batch_import_resin_spinning_records():
    """
    从Excel文件批量导入前端树脂与纺丝工艺参数记录。
    请求应为 multipart/form-data，包含一个名为 'file' 的文件字段。
    """
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "请求中未找到文件部分。"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "未选择任何文件。"}), 400

    if file and allowed_file(file.filename):
        # filename = secure_filename(file.filename) # Good practice, though not strictly needed if only reading stream
        
        current_user_id = AuthService.get_current_user_id()
        if not current_user_id:
             return jsonify({"success": False, "message": "无法获取当前用户信息，请重新登录。"}), 401

        try:
            # Read Excel file into a pandas DataFrame
            # The file stream (file) is directly passed to read_excel
            df = pd.read_excel(file, engine='openpyxl')
            
            # Convert DataFrame to list of dictionaries
            # Important: Ensure Excel column names match expected keys or map them here.
            # For now, assume direct mapping.
            # Example mapping if Excel columns are different:
            # column_mapping = {
            #     'Excel批号': 'batch_number',
            #     'Excel材料牌号': 'material_grade',
            #     # ... other mappings ...
            # }
            # df.rename(columns=column_mapping, inplace=True)
            
            # Add row numbers for error reporting
            records_to_process = []
            for index, row in df.iterrows():
                records_to_process.append({
                    "row_number": index + 2, # Excel rows are typically 1-indexed, headers are row 1
                    "data": row.to_dict()
                })

        except Exception as e:
            return jsonify({"success": False, "message": f"文件解析失败: {str(e)}"}), 400
        
        if not records_to_process:
             return jsonify({"success": False, "message": "Excel文件中没有找到可处理的数据行。"}), 400

        result = ResinSpinningService.batch_create_records(records_data=records_to_process, user_id=current_user_id)

        if result["failure_count"] > 0:
            # Partial success or complete failure
            return jsonify({
                "success": False, # Indicate that not all records were successful
                "message": "批量导入完成，但存在部分错误。",
                "details": result
            }), 207 # Multi-Status
        else:
            # All records imported successfully
            return jsonify({
                "success": True,
                "message": f"成功导入 {result['success_count']} 条记录。",
                "details": result
            }), 201 # Created (or 200 OK if preferred for batch operations)
            
    else:
        return jsonify({"success": False, "message": "文件类型不允许。请上传 .xlsx 或 .xls 文件。"}), 400

# --- Export to Excel Endpoint ---
@resin_spinning_bp.route('/export', methods=['GET'])
@login_required
@permission_required(MODULE_NAME_FOR_RBAC, 'CanExport')
def export_resin_spinning_records():
    """
    导出前端树脂与纺丝工艺参数记录到Excel文件。
    支持通过查询参数进行过滤。
    """
    # Extract filters from query parameters (similar to get_all_resin_spinning_records)
    filters = {
        'material_grade': request.args.get('material_grade', type=str),
        'batch_number': request.args.get('batch_number', type=str),
        'resin_type': request.args.get('resin_type', type=str)
        # Add other filters as needed
    }
    filters = {k: v for k, v in filters.items() if v is not None}

    try:
        records = ResinSpinningService.get_all_records_for_export(filters=filters)

        if not records:
            return jsonify({"success": False, "message": "没有找到可导出的数据。"}), 404

        # Convert SQLAlchemy objects to dictionaries, then to DataFrame
        # Using the to_dict() method from the model, but selecting/ordering columns as per template
        
        # Define headers in Chinese as they should appear in Excel (matching template)
        # This order also dictates column order in Excel.
        excel_headers_map = {
            "批号": "batch_number",
            "材料牌号": "material_grade",
            "供应商": "supplier",
            "树脂类型": "resin_type",
            "树脂分子量_g_mol": "resin_molecular_weight_g_mol",
            "多分散系数_PDI": "polydispersity_index_pdi",
            "特性粘度_dL_g": "intrinsic_viscosity_dl_g",
            "熔点_C": "melting_point_c",
            "结晶度_percent": "crystallinity_percent",
            "纺丝方法": "spinning_method",
            "溶剂体系": "solvent_system",
            "原液浓度_percent": "solution_concentration_percent",
            "纺丝温度_C": "spinning_temperature_c",
            "喷丝板规格": "spinneret_specifications",
            "凝固浴组成": "coagulation_bath_composition",
            "凝固浴温度_C": "coagulation_bath_temperature_c",
            "拉伸倍数": "draw_ratio",
            "热处理温度_C": "heat_treatment_temperature_c",
            "备注": "remarks",
            "创建用户ID": "created_by_user_id", # Or map to username if preferred for export
            "最后修改用户ID": "last_modified_by_user_id", # Or map to username
            "记录创建时间": "created_at",
            "记录更新时间": "updated_at"
        }

        data_for_df = []
        for record_model in records:
            record_dict = record_model.to_dict(include_user_info=False) # Get dict from model
            ordered_row = {}
            for ch_header, en_attr in excel_headers_map.items():
                value = record_dict.get(en_attr)
                # Format datetime objects if they are not already strings
                if en_attr in ["created_at", "updated_at"] and value and not isinstance(value, str):
                     ordered_row[ch_header] = value.strftime('%Y-%m-%d %H:%M:%S') if value else None
                else:
                    ordered_row[ch_header] = value
            data_for_df.append(ordered_row)
            
        df = pd.DataFrame(data_for_df, columns=list(excel_headers_map.keys()))

        # Create an in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='树脂纺丝工艺参数')
        
        output.seek(0) # Reset buffer's position to the beginning

        return Response(
            output.getvalue(),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": "attachment;filename=前端树脂与纺丝工艺参数.xlsx",
                "Access-Control-Expose-Headers": "Content-Disposition" # Important for frontend to access filename
            }
        )

    except Exception as e:
        # Log the error: current_app.logger.error(f"导出Excel失败: {e}")
        print(f"导出Excel失败: {e}") # Placeholder
        return jsonify({"success": False, "message": f"导出Excel失败: {str(e)}"}), 500
