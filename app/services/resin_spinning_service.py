# app/services/resin_spinning_service.py
# "前端树脂与纺丝工艺参数" 模块的服务层

from app import db
from app.models.resin_spinning_model import ResinSpinningProcessModel
from sqlalchemy.exc import IntegrityError
from app.utils.common_utils import convert_to_float_or_none # 假设有一个通用工具转换数据类型

class ResinSpinningService:
    """
    处理前端树脂与纺丝工艺参数相关业务逻辑的服务类。
    """

    @staticmethod
    def create_record(data: dict, user_id: int) -> tuple:
        """
        创建一条新的前端树脂与纺丝工艺参数记录。
        :param data: 包含记录数据的字典。
        :param user_id: 创建记录的用户ID。
        :return: (success: bool, message_or_record: str or ResinSpinningProcessModel, status_code: int)
        """
        required_fields = ['batch_number', 'material_grade'] # 批号和材料牌号是必填项
        for field in required_fields:
            if not data.get(field):
                return False, f"必填字段 '{field}' 缺失。", 400

        # 类型转换 (示例，可以根据需要扩展)
        # 使用一个辅助函数来尝试转换数值类型，避免ValueError
        numerical_fields_specs = {
            'resin_molecular_weight_g_mol': (18, 2), 
            'polydispersity_index_pdi': (10, 3),
            'intrinsic_viscosity_dl_g': (10, 3),
            'melting_point_c': (10, 2),
            'crystallinity_percent': (10, 2),
            'solution_concentration_percent': (10, 2),
            'spinning_temperature_c': (10, 2),
            'coagulation_bath_temperature_c': (10, 2),
            'draw_ratio': (10, 2),
            'heat_treatment_temperature_c': (10, 2)
        }
        
        for field, _ in numerical_fields_specs.items():
            if field in data and data[field] is not None:
                converted_value = convert_to_float_or_none(data[field])
                if converted_value is None and data[field] != '': # Allow empty string to be treated as None, but not invalid numbers
                     return False, f"字段 '{field}' 的值 '{data[field]}' 不是有效的数字。", 400
                data[field] = converted_value


        new_record = ResinSpinningProcessModel(
            batch_number=data.get('batch_number'),
            material_grade=data.get('material_grade'),
            supplier=data.get('supplier'),
            resin_type=data.get('resin_type', 'UHMWPE'), # Default value
            resin_molecular_weight_g_mol=data.get('resin_molecular_weight_g_mol'),
            polydispersity_index_pdi=data.get('polydispersity_index_pdi'),
            intrinsic_viscosity_dl_g=data.get('intrinsic_viscosity_dl_g'),
            melting_point_c=data.get('melting_point_c'),
            crystallinity_percent=data.get('crystallinity_percent'),
            spinning_method=data.get('spinning_method'),
            solvent_system=data.get('solvent_system'),
            solution_concentration_percent=data.get('solution_concentration_percent'),
            spinning_temperature_c=data.get('spinning_temperature_c'),
            spinneret_specifications=data.get('spinneret_specifications'),
            coagulation_bath_composition=data.get('coagulation_bath_composition'),
            coagulation_bath_temperature_c=data.get('coagulation_bath_temperature_c'),
            draw_ratio=data.get('draw_ratio'),
            heat_treatment_temperature_c=data.get('heat_treatment_temperature_c'),
            remarks=data.get('remarks'),
            created_by_user_id=user_id,
            last_modified_by_user_id=user_id
        )

        try:
            new_record.save_to_db()
            return True, new_record.to_dict(include_user_info=True), 201
        except IntegrityError as e:
            db.session.rollback()
            if 'UQ_前端树脂与纺丝工艺表_批号' in str(e.orig): # 检查是否是批号唯一性冲突
                return False, f"批号 '{data.get('batch_number')}' 已存在。", 409 # 409 Conflict
            return False, f"数据库完整性错误: {str(e.orig)}", 500
        except Exception as e:
            db.session.rollback()
            return False, f"创建记录时发生内部错误: {str(e)}", 500

    @staticmethod
    def get_record_by_id(record_id: int) -> tuple:
        """
        根据记录ID获取单个记录。
        :param record_id: 记录的ID。
        :return: (success: bool, message_or_record_dict: str or dict, status_code: int)
        """
        record = ResinSpinningProcessModel.query.get(record_id)
        if record:
            return True, record.to_dict(include_user_info=True), 200
        else:
            return False, f"记录ID {record_id} 未找到。", 404

    @staticmethod
    def get_all_records(page: int = 1, per_page: int = 10, filters: dict = None) -> tuple:
        """
        获取所有记录（带分页和过滤）。
        :param page: 当前页码。
        :param per_page: 每页记录数。
        :param filters: 包含过滤条件的字典 (例如: {'material_grade': '牌号A', 'batch_number': '批号X'})。
        :return: (success: bool, data_or_message: dict or str, status_code: int)
        """
        query = ResinSpinningProcessModel.query

        if filters:
            if 'material_grade' in filters and filters['material_grade']:
                query = query.filter(ResinSpinningProcessModel.material_grade.ilike(f"%{filters['material_grade']}%"))
            if 'batch_number' in filters and filters['batch_number']:
                query = query.filter(ResinSpinningProcessModel.batch_number.ilike(f"%{filters['batch_number']}%"))
            if 'resin_type' in filters and filters['resin_type']:
                query = query.filter(ResinSpinningProcessModel.resin_type.ilike(f"%{filters['resin_type']}%"))
            # 可以根据需要添加更多过滤条件

        query = query.order_by(ResinSpinningProcessModel.created_at.desc()) # 按创建时间降序排序

        try:
            paginated_records = query.paginate(page=page, per_page=per_page, error_out=False)
            records_data = [record.to_dict() for record in paginated_records.items]
            
            return True, {
                'records': records_data,
                'total': paginated_records.total,
                'pages': paginated_records.pages,
                'current_page': paginated_records.page,
                'per_page': paginated_records.per_page,
                'has_next': paginated_records.has_next,
                'has_prev': paginated_records.has_prev
            }, 200
        except Exception as e:
            return False, f"获取记录列表时发生错误: {str(e)}", 500
            
    @staticmethod
    def update_record(record_id: int, data: dict, user_id: int) -> tuple:
        """
        更新指定的记录。
        :param record_id: 要更新的记录ID。
        :param data: 包含更新数据的字典。
        :param user_id: 执行更新操作的用户ID。
        :return: (success: bool, message_or_record_dict: str or dict, status_code: int)
        """
        record = ResinSpinningProcessModel.query.get(record_id)
        if not record:
            return False, f"记录ID {record_id} 未找到。", 404

        # 更新字段，可以根据需要添加更多字段
        # 类型转换 (与 create_record 类似)
        numerical_fields_specs = {
            'resin_molecular_weight_g_mol': (18, 2), 
            'polydispersity_index_pdi': (10, 3),
            # ... (add all other numerical fields from model)
        }
        for field, _ in numerical_fields_specs.items():
            if field in data and data[field] is not None:
                converted_value = convert_to_float_or_none(data[field])
                if converted_value is None and data[field] != '':
                     return False, f"字段 '{field}' 的值 '{data[field]}' 不是有效的数字。", 400
                setattr(record, field, converted_value)
            elif field in data and data[field] is None: # Explicitly setting to None
                 setattr(record, field, None)


        # 更新非数字字段
        for key, value in data.items():
            if key not in numerical_fields_specs and hasattr(record, key) and key not in ['record_id', 'created_by_user_id', 'created_at']:
                setattr(record, key, value)
        
        record.last_modified_by_user_id = user_id
        # record.updated_at is handled by onupdate=func.now() in the model

        try:
            record.save_to_db()
            return True, record.to_dict(include_user_info=True), 200
        except IntegrityError as e:
            db.session.rollback()
            if 'UQ_前端树脂与纺丝工艺表_批号' in str(e.orig) and record.batch_number == data.get('batch_number'): # Check if it's a unique constraint on batch_number
                return False, f"批号 '{data.get('batch_number')}' 已被其他记录使用。", 409
            return False, f"数据库完整性错误: {str(e.orig)}", 500
        except Exception as e:
            db.session.rollback()
            return False, f"更新记录时发生内部错误: {str(e)}", 500

    @staticmethod
    def delete_record(record_id: int) -> tuple:
        """
        删除指定的记录。
        :param record_id: 要删除的记录ID。
        :return: (success: bool, message: str, status_code: int)
        """
        record = ResinSpinningProcessModel.query.get(record_id)
        if not record:
            return False, f"记录ID {record_id} 未找到。", 404
        
        try:
            record.delete_from_db()
            return True, f"记录ID {record_id} 已成功删除。", 200
        except Exception as e:
            db.session.rollback()
            return False, f"删除记录时发生内部错误: {str(e)}", 500

    @staticmethod
    def batch_create_records(records_data: list, user_id: int) -> dict:
        """
        批量创建前端树脂与纺丝工艺参数记录。
        :param records_data: 记录数据列表，每个元素是一个包含行号和记录数据的字典。
                             例如: [{"row_number": 2, "data": {"batch_number": "B001", ...}}, ...]
        :param user_id: 创建记录的用户ID。
        :return: 包含成功、失败计数和错误详情的字典。
        """
        success_count = 0
        failure_count = 0
        errors = []

        required_fields = ['batch_number', 'material_grade'] # 批号和材料牌号是必填项
        numerical_fields_specs = {
            'resin_molecular_weight_g_mol': (18, 2), 
            'polydispersity_index_pdi': (10, 3),
            'intrinsic_viscosity_dl_g': (10, 3),
            'melting_point_c': (10, 2),
            'crystallinity_percent': (10, 2),
            'solution_concentration_percent': (10, 2),
            'spinning_temperature_c': (10, 2),
            'coagulation_bath_temperature_c': (10, 2),
            'draw_ratio': (10, 2),
            'heat_treatment_temperature_c': (10, 2)
        }

        for item in records_data:
            row_number = item.get("row_number", "N/A") # 从传入数据获取行号
            record_data = item.get("data", {})

            # 1. 验证必填字段
            missing_required = [field for field in required_fields if not record_data.get(field)]
            if missing_required:
                failure_count += 1
                errors.append({
                    "row_number": row_number, 
                    "data": record_data, 
                    "error": f"必填字段缺失: {', '.join(missing_required)}"
                })
                continue # 跳过此记录的处理

            # 2. 类型转换和验证
            conversion_error = False
            processed_data = record_data.copy() # 创建副本以存储转换后的值
            for field, _ in numerical_fields_specs.items():
                if field in processed_data and processed_data[field] is not None:
                    original_value = processed_data[field]
                    converted_value = convert_to_float_or_none(original_value)
                    if converted_value is None and str(original_value).strip() != '': 
                        failure_count += 1
                        errors.append({
                            "row_number": row_number,
                            "data": record_data, # 原始数据
                            "error": f"字段 '{field}' 的值 '{original_value}' 不是有效的数字。"
                        })
                        conversion_error = True
                        break 
                    processed_data[field] = converted_value
            
            if conversion_error:
                continue

            # 3. 创建模型实例
            new_record = ResinSpinningProcessModel(
                batch_number=processed_data.get('batch_number'),
                material_grade=processed_data.get('material_grade'),
                supplier=processed_data.get('supplier'),
                resin_type=processed_data.get('resin_type', 'UHMWPE'),
                resin_molecular_weight_g_mol=processed_data.get('resin_molecular_weight_g_mol'),
                polydispersity_index_pdi=processed_data.get('polydispersity_index_pdi'),
                intrinsic_viscosity_dl_g=processed_data.get('intrinsic_viscosity_dl_g'),
                melting_point_c=processed_data.get('melting_point_c'),
                crystallinity_percent=processed_data.get('crystallinity_percent'),
                spinning_method=processed_data.get('spinning_method'),
                solvent_system=processed_data.get('solvent_system'),
                solution_concentration_percent=processed_data.get('solution_concentration_percent'),
                spinning_temperature_c=processed_data.get('spinning_temperature_c'),
                spinneret_specifications=processed_data.get('spinneret_specifications'),
                coagulation_bath_composition=processed_data.get('coagulation_bath_composition'),
                coagulation_bath_temperature_c=processed_data.get('coagulation_bath_temperature_c'),
                draw_ratio=processed_data.get('draw_ratio'),
                heat_treatment_temperature_c=processed_data.get('heat_treatment_temperature_c'),
                remarks=processed_data.get('remarks'),
                created_by_user_id=user_id,
                last_modified_by_user_id=user_id
            )

            # 4. 尝试保存到数据库
            try:
                db.session.add(new_record) # 添加到会话
                db.session.flush() # 将更改刷新到数据库，以便捕获唯一性等错误
                success_count += 1
            except IntegrityError as e:
                db.session.rollback() # 回滚当前记录的添加
                failure_count += 1
                error_message = f"数据库完整性错误: {str(e.orig)}"
                if 'UQ_前端树脂与纺丝工艺表_批号' in str(e.orig).lower():
                    error_message = f"批号 '{processed_data.get('batch_number')}' 已存在。"
                errors.append({"row_number": row_number, "data": record_data, "error": error_message})
            except Exception as e:
                db.session.rollback()
                failure_count += 1
                errors.append({"row_number": row_number, "data": record_data, "error": f"保存时发生未知错误: {str(e)}"})
        
        # 循环结束后，提交所有成功的记录
        if success_count > 0:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                # 这个错误比较严重，可能需要将所有本批次的 success_count 标记为失败
                # 或者至少记录一个全局错误
                # For simplicity here, we'll assume individual flushes caught most issues.
                # A more robust solution might use nested transactions or savepoints.
                return {
                    "success_count": 0, # Or adjust based on how you handle this commit failure
                    "failure_count": success_count + failure_count, 
                    "errors": errors + [{"row_number": "GLOBAL", "data": None, "error": f"最终提交失败: {str(e)}"}]
                }
                
        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "errors": errors
        }

    @staticmethod
    def get_all_records_for_export(filters: dict = None) -> list:
        """
        获取所有匹配过滤条件的记录，用于导出。
        :param filters: 包含过滤条件的字典 (例如: {'material_grade': '牌号A', 'batch_number': '批号X'})。
        :return: ResinSpinningProcessModel 对象列表。
        """
        query = ResinSpinningProcessModel.query

        if filters:
            if 'material_grade' in filters and filters['material_grade']:
                query = query.filter(ResinSpinningProcessModel.material_grade.ilike(f"%{filters['material_grade']}%"))
            if 'batch_number' in filters and filters['batch_number']:
                query = query.filter(ResinSpinningProcessModel.batch_number.ilike(f"%{filters['batch_number']}%"))
            if 'resin_type' in filters and filters['resin_type']:
                query = query.filter(ResinSpinningProcessModel.resin_type.ilike(f"%{filters['resin_type']}%"))
            # Add other filters as needed, matching get_all_records logic
            # Example:
            # if 'start_date' in filters and filters['start_date']:
            #     try:
            #         start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
            #         query = query.filter(func.date(ResinSpinningProcessModel.created_at) >= start_date)
            #     except ValueError:
            #         pass # Or raise a specific error / log it
            # if 'end_date' in filters and filters['end_date']:
            #     try:
            #         end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
            #         query = query.filter(func.date(ResinSpinningProcessModel.created_at) <= end_date)
            #     except ValueError:
            #         pass

        query = query.order_by(ResinSpinningProcessModel.record_id.asc()) # Or any preferred order for export
        
        try:
            return query.all()
        except Exception as e:
            # Log the error, e.g., current_app.logger.error(f"Error fetching records for export: {e}")
            print(f"Error fetching records for export: {e}") # Placeholder for logging
            return []


# app/utils/common_utils.py (假设这个文件存在)
# def convert_to_float_or_none(value):
#     if value is None:
#         return None
#     if isinstance(value, (int, float)):
#         return float(value)
#     if isinstance(value, str):
#         if value.strip() == '':
#             return None
#         try:
#             return float(value.strip())
#         except ValueError:
#             return None # Indicate conversion failure for non-empty invalid string
#     return None # Or raise TypeError for unsupported types
