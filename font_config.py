import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os
import requests
import shutil
import sys
from pathlib import Path

def setup_chinese_font():
    try:
        # 设置matplotlib的字体
        plt.rcParams['font.family'] = ['sans-serif']
        # 尝试多个常用中文字体
        plt.rcParams['font.sans-serif'] = [
            'SimHei',  # Windows的中文黑体
            'Heiti TC',  # macOS的黑体
            'Heiti SC',  # macOS的黑体
            'Microsoft YaHei',  # 微软雅黑
            'WenQuanYi Micro Hei',  # Linux的文泉驿微米黑
            'Arial Unicode MS',  # 通用Unicode字体
            'DejaVu Sans'  # Linux通用字体
        ]
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
        
        # 验证字体是否可用
        fig, ax = plt.subplots()
        ax.set_title('测试中文')
        plt.close(fig)
        
        return True
        
    except Exception as e:
        print(f"配置字体时出错: {e}")
        return False

if __name__ == "__main__":
    setup_chinese_font() 