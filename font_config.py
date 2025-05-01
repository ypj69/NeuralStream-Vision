import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import base64
import tempfile
import os
import atexit
import logging
from typing import Optional

# 这里使用精简版的思源黑体SC Regular的Base64编码
# 注意：这个编码字符串通常很长，这里用占位符表示
NOTO_SANS_SC_BASE64 = """
[在此处放置精简版思源黑体的Base64编码，建议只包含常用字符的子集]
"""

_temp_font_file: Optional[str] = None

def _cleanup_temp_font():
    """清理临时字体文件"""
    global _temp_font_file
    if _temp_font_file and os.path.exists(_temp_font_file):
        try:
            os.remove(_temp_font_file)
            _temp_font_file = None
        except Exception as e:
            logging.warning(f"清理临时字体文件失败: {e}")

def setup_chinese_font() -> bool:
    """
    设置中文字体
    
    Returns:
        bool: 字体设置是否成功
    """
    global _temp_font_file
    
    try:
        # 解码字体数据
        font_data = base64.b64decode(NOTO_SANS_SC_BASE64)
        
        # 创建临时字体文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ttf") as tmp_font:
            tmp_font.write(font_data)
            _temp_font_file = tmp_font.name
        
        # 注册清理函数
        atexit.register(_cleanup_temp_font)
        
        # 动态添加字体
        fm.fontManager.addfont(_temp_font_file)
        font_name = fm.FontProperties(fname=_temp_font_file).get_name()
        
        # 设置matplotlib的字体
        plt.rcParams['font.family'] = font_name
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        
        return True
        
    except Exception as e:
        logging.error(f"设置中文字体失败: {e}")
        _cleanup_temp_font()
        return False

# 在模块卸载时清理临时文件
atexit.register(_cleanup_temp_font)

def get_chinese_font():
    """获取中文字体属性"""
    return setup_chinese_font.font_prop

def create_figure():
    """创建支持中文的图形"""
    return setup_chinese_font.create_figure()

if __name__ == "__main__":
    setup_chinese_font() 