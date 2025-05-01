import base64
import sys

def generate_font_base64(font_path: str) -> str:
    """
    读取字体文件并生成Base64编码
    
    Args:
        font_path: 字体文件路径
    
    Returns:
        str: Base64编码的字体数据
    """
    try:
        with open(font_path, 'rb') as f:
            font_data = f.read()
        return base64.b64encode(font_data).decode('utf-8')
    except Exception as e:
        print(f"错误：无法读取字体文件 - {e}")
        return ""

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使用方法: python generate_font_base64.py <字体文件路径>")
        sys.exit(1)
    
    font_path = sys.argv[1]
    base64_str = generate_font_base64(font_path)
    
    if base64_str:
        # 将Base64字符串写入文件
        output_file = "font_base64.txt"
        with open(output_file, 'w') as f:
            f.write(base64_str)
        print(f"Base64编码已保存到文件: {output_file}") 