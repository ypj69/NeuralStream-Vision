import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import os
import requests
import shutil

def setup_chinese_font():
    # 字体文件的URL（使用开源的思源黑体）
    font_url = "https://github.com/adobe-fonts/source-han-sans/raw/release/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf"
    font_path = os.path.join(os.path.dirname(__file__), "fonts", "SourceHanSansSC-Regular.otf")
    
    # 如果字体文件不存在，则下载
    if not os.path.exists(font_path):
        os.makedirs(os.path.dirname(font_path), exist_ok=True)
        try:
            response = requests.get(font_url, stream=True)
            if response.status_code == 200:
                with open(font_path, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)
            else:
                print("无法下载字体文件")
                return False
        except Exception as e:
            print(f"下载字体文件时出错: {e}")
            return False
    
    # 添加字体文件
    font_manager = fm.FontManager()
    font_manager.addfont(font_path)
    
    # 设置matplotlib的字体
    plt.rcParams['font.family'] = ['sans-serif']
    plt.rcParams['font.sans-serif'] = ['Source Han Sans SC']
    plt.rcParams['axes.unicode_minus'] = False
    
    return True 