# app/utils/common_utils.py
# 通用工具函数

def convert_to_float_or_none(value):
    """
    尝试将输入值转换为浮点数。
    如果值为None、空字符串或无法转换，则返回None。
    如果已经是数字（int, float），则直接转换为float。
    :param value: 要转换的值 (可以是字符串, 数字, 或 None)
    :return: 转换后的浮点数或None
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        stripped_value = value.strip()
        if stripped_value == '':
            return None
        try:
            return float(stripped_value)
        except ValueError:
            # 如果字符串不能转换为float，则表示转换失败
            return None # 或者可以抛出异常，取决于业务需求
    # 对于其他类型（如列表、字典等），明确返回None或抛出TypeError
    # raise TypeError(f"Unsupported type for conversion to float: {type(value)}")
    return None

def convert_to_int_or_none(value):
    """
    尝试将输入值转换为整数。
    如果值为None、空字符串或无法转换，则返回None。
    :param value: 要转换的值
    :return: 转换后的整数或None
    """
    if value is None:
        return None
    if isinstance(value, (int, float)): # Also handles float to int conversion
        return int(value)
    if isinstance(value, str):
        stripped_value = value.strip()
        if stripped_value == '':
            return None
        try:
            # First convert to float to handle "123.0" then to int
            return int(float(stripped_value))
        except ValueError:
            return None
    return None

# 可以在这里添加更多通用工具函数，例如：
# - 日期时间格式化
# - 数据验证帮助函数
# - ...
# print("通用工具模块 (common_utils.py) 已加载。")
