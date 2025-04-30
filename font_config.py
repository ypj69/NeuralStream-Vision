import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os
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
            'Noto Sans CJK SC',  # Linux/Chrome OS的思源黑体
            'Noto Sans SC',  # Linux/Chrome OS的思源黑体
            'Arial Unicode MS',  # 通用Unicode字体
            'DejaVu Sans'  # Linux通用字体
        ]
        plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

        # 验证字体配置
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        print("可用的字体:", available_fonts)  # 打印可用字体列表，帮助调试
        
        # 创建测试图形
        fig, ax = plt.subplots()
        ax.set_title('测试中文')
        plt.close(fig)
        
        return True
        
    except Exception as e:
        print(f"配置字体时出错: {str(e)}")
        return False

if __name__ == "__main__":
    setup_chinese_font() 