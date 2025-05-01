import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import platform

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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, 'assets', 'SourceHanSansCN-Regular.otf')
    
    def setup_chinese_font(self):
        """
        设置matplotlib的中文字体
        返回值：bool，表示是否成功设置字体
        """
        try:
            # 获取字体文件路径
            font_path = self.get_font_path()
            if not os.path.exists(font_path):
                print(f"找不到字体文件: {font_path}")
                return False
                
            # 添加字体文件
            self._font_prop = fm.FontProperties(fname=font_path)
            
            # 设置matplotlib的字体
            plt.rcParams['font.family'] = ['sans-serif']
            if platform.system() == 'Windows':
                plt.rcParams['font.sans-serif'] = [self._font_prop.get_name()]
            else:
                plt.rcParams['font.sans-serif'] = [self._font_prop.get_name(), 'DejaVu Sans']
                
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