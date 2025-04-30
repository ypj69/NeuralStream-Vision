import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os
import requests
import shutil
import sys
from pathlib import Path

def setup_chinese_font():
    # 使用清华镜像源下载字体
    font_url = "https://mirrors.tuna.tsinghua.edu.cn/adobe-fonts/source-han-sans/SubsetOTF/CN/SourceHanSansCN-Regular.otf"
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "SourceHanSansCN-Regular.otf")
    font_path = Path(font_path)
    
    # 确保fonts目录存在
    font_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 如果字体文件不存在，则下载
    if not font_path.exists():
        try:
            print("正在下载中文字体文件...")
            response = requests.get(font_url, stream=True)
            if response.status_code == 200:
                with open(font_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
                print("字体文件下载完成！")
            else:
                print(f"无法下载字体文件，HTTP状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"下载字体文件时出错: {e}")
            return False

    try:
        # 确保字体文件存在
        if not font_path.exists():
            print(f"错误：字体文件不存在: {font_path}")
            return False

        # 清除字体缓存
        fm._get_font_cache().clear()
        
        # 添加字体文件
        font_files = fm.findSystemFonts(fontpaths=[str(font_path.parent)])
        for font_file in font_files:
            fm.fontManager.addfont(font_file)
        
        # 设置matplotlib的字体
        plt.rcParams['font.family'] = ['sans-serif']
        plt.rcParams['font.sans-serif'] = ['Source Han Sans CN', 'SimHei', 'Arial Unicode MS']
        plt.rcParams['axes.unicode_minus'] = False
        
        # 验证字体是否可用
        font_names = [f.name for f in fm.fontManager.ttflist]
        if 'Source Han Sans CN' not in font_names and 'SimHei' not in font_names:
            print("警告：未能找到中文字体，将尝试使用系统默认字体")
            return False
            
        print("中文字体配置成功！")
        return True
        
    except Exception as e:
        print(f"配置字体时出错: {e}")
        return False

if __name__ == "__main__":
    setup_chinese_font() 