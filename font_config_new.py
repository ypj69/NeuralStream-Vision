import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform
from pathlib import Path

class ChineseFontManager:
    _instance = None
    _font_prop = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ChineseFontManager()
        return cls._instance
    
    def __init__(self):
        if ChineseFontManager._instance is not None:
            raise Exception("这是一个单例类，请使用 get_instance() 方法获取实例")
        ChineseFontManager._instance = self
    
    @staticmethod
    def get_font_path():
        """
        获取思源黑体文件的路径
        返回值：字体文件的完整路径
        """
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            font_path = os.path.join(current_dir, 'assets', 'SourceHanSansCN-Regular.otf')
            
            if not os.path.exists(font_path):
                # 尝试在系统字体目录中查找
                system_font_dirs = []
                if platform.system() == 'Windows':
                    system_font_dirs = [os.path.join(os.environ['WINDIR'], 'Fonts')]
                elif platform.system() == 'Linux':
                    system_font_dirs = [
                        '/usr/share/fonts',
                        '/usr/local/share/fonts',
                        str(Path.home() / '.fonts'),
                        str(Path.home() / '.local/share/fonts')
                    ]
                elif platform.system() == 'Darwin':  # macOS
                    system_font_dirs = [
                        '/System/Library/Fonts',
                        '/Library/Fonts',
                        str(Path.home() / 'Library/Fonts')
                    ]
                
                # 在系统字体目录中查找思源黑体
                for font_dir in system_font_dirs:
                    if os.path.exists(font_dir):
                        for root, _, files in os.walk(font_dir):
                            for file in files:
                                if ('SourceHanSans' in file or '思源黑体' in file) and file.endswith(('.ttf', '.otf')):
                                    return os.path.join(root, file)
            
            return font_path
            
        except Exception as e:
            print(f"查找字体文件时出错: {str(e)}")
            return None
    
    def setup_chinese_font(self):
        """
        设置matplotlib的中文字体
        返回值：bool，表示是否成功设置字体
        """
        try:
            # 获取字体文件路径
            font_path = self.get_font_path()
            if not font_path or not os.path.exists(font_path):
                print(f"找不到字体文件: {font_path}")
                # 尝试使用系统默认中文字体
                if platform.system() == 'Windows':
                    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
                elif platform.system() == 'Linux':
                    plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei']
                elif platform.system() == 'Darwin':  # macOS
                    plt.rcParams['font.sans-serif'] = ['PingFang SC']
                else:
                    return False
            else:
                # 添加字体文件
                self._font_prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = ['sans-serif']
                plt.rcParams['font.sans-serif'] = [self._font_prop.get_name()]
            
            plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
            return True
            
        except Exception as e:
            print(f"设置中文字体时出错: {str(e)}")
            return False
    
    @property
    def font_prop(self):
        """获取字体属性"""
        return self._font_prop

def setup_chinese_font():
    """
    设置中文字体的便捷函数
    返回值：bool，表示是否成功设置字体
    """
    return ChineseFontManager.get_instance().setup_chinese_font()

def get_chinese_font():
    """
    获取中文字体属性的便捷函数
    返回值：FontProperties对象
    """
    return ChineseFontManager.get_instance().font_prop

if __name__ == "__main__":
    setup_chinese_font() 