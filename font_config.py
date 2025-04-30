import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from pathlib import Path
import matplotlib as mpl

def setup_chinese_font():
    try:
        # 获取字体文件的绝对路径
        current_dir = Path(__file__).parent
        font_path = current_dir / 'assets' / 'SourceHanSansCN-Regular.otf'
        
        # 如果字体文件存在，则注册字体
        if font_path.exists():
            # 添加字体文件
            font_prop = fm.FontProperties(fname=str(font_path))
            
            # 设置全局字体
            plt.rcParams['font.family'] = ['sans-serif']
            plt.rcParams['font.sans-serif'] = ['Source Han Sans CN']
            plt.rcParams['axes.unicode_minus'] = False
            
            # 保存字体属性供后续使用
            setup_chinese_font.font_prop = font_prop
            
            # 创建自定义绘图函数
            def create_figure_with_chinese():
                fig, ax = plt.subplots()
                # 设置标题和标签的字体
                ax.set_title(ax.get_title(), fontproperties=font_prop)
                ax.set_xlabel(ax.get_xlabel(), fontproperties=font_prop)
                ax.set_ylabel(ax.get_ylabel(), fontproperties=font_prop)
                return fig, ax
                
            # 保存绘图函数供后续使用
            setup_chinese_font.create_figure = create_figure_with_chinese
            
            print(f"成功加载中文字体文件: {font_path}")
            return True
        else:
            print(f"错误：字体文件不存在: {font_path}")
            print("请确保字体文件 'SourceHanSansCN-Regular.otf' 位于 assets 目录中")
            return False
            
    except Exception as e:
        print(f"配置字体时出错: {str(e)}")
        return False

# 初始化默认值
setup_chinese_font.font_prop = None
setup_chinese_font.create_figure = plt.subplots

def get_chinese_font():
    """获取中文字体属性"""
    return setup_chinese_font.font_prop

def create_figure():
    """创建支持中文的图形"""
    return setup_chinese_font.create_figure()

if __name__ == "__main__":
    setup_chinese_font() 