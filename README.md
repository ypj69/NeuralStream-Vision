# NeuralStream-Vision - 基于深度学习的智能股票投资分析系统

## 项目简介
NeuralStream-Vision 是一个结合深度学习和大语言模型的智能股票投资分析系统。该系统能够对股票进行技术面和基本面分析，生成专业的投资建议报告，并提供交互式的投资咨询服务。

## 主要功能
- **股票价格预测**：使用CNN-LSTM模型进行股票价格预测
- **技术指标分析**：支持多种技术指标的计算和可视化
- **基本面分析**：提供全面的基本面指标分析
- **智能投资报告**：基于大语言模型生成专业的投资分析报告
- **交互式咨询**：支持用户与系统进行多轮对话，深入分析投资问题

## 技术特点
- 采用CNN-LSTM混合模型进行价格预测
- 集成注意力机制提升模型性能
- 支持多种技术指标和基本面指标
- 使用Streamlit构建友好的Web界面
- 结合大语言模型生成专业投资建议
- 使用思源黑体确保图表中文正确显示

## 安装说明

1. 克隆项目
```bash
git clone https://github.com/ypj69/NeuralStream-Vision.git
cd new_2
```

2. 安装Python依赖
```bash
pip install -r requirements.txt
```

3. 安装系统依赖（Linux环境）
```bash
sudo apt-get update
sudo apt-get install -y fontconfig libfontconfig1 libfontconfig1-dev
```

4. 配置字体
- 确保 `assets` 目录中包含 `SourceHanSansCN-Regular.otf` 字体文件
- 系统会自动加载并配置字体，无需额外设置

5. 配置API密钥
- 在 `bmodel.py` 中配置通义千问API密钥
- 在 `genData.py` 中配置Tushare API密钥
- 在 `StockFundamentals.py` 中配置米筐API密钥

## 使用方法

1. 启动Web应用
```bash
streamlit run app.py
```

2. 在Web界面中：
   - 输入股票代码
   - 选择分析时间范围
   - 选择需要分析的技术指标和基本面指标
   - 点击"预测与分析"按钮获取分析结果
   - 可以继续提问获取更深入的分析

## 项目结构
```
NeuralStream-Vision/
├── app.py                 # Streamlit Web应用主文件
├── bmodel.py              # 大语言模型相关功能
├── genData.py             # 数据获取和预处理
├── new_mian.py           # 深度学习模型主文件
├── StockFundamentals.py  # 基本面分析模块
├── font_config_new.py    # 中文字体配置模块
├── assets/               # 资源文件目录
│   └── SourceHanSansCN-Regular.otf  # 思源黑体字体文件
├── requirements.txt      # Python依赖清单
├── packages.txt         # 系统级依赖清单
└── README.md            # 项目说明文档
```

## 环境要求
- Python 3.8+
- CUDA支持（推荐，用于GPU加速）
- 系统字体支持（fontconfig）
- 思源黑体字体文件

## 云端部署说明
在 Streamlit Community Cloud 上部署时：
1. 确保 `assets` 目录中包含字体文件
2. 系统会自动安装 `requirements.txt` 中的Python依赖
3. 系统会自动安装 `packages.txt` 中的系统依赖
4. 字体配置会自动完成，无需手动干预

## 注意事项
- 使用前请确保已正确配置所有必要的API密钥
- 建议使用GPU进行模型训练和预测
- 请遵守相关API的使用条款和限制
- 如果遇到中文显示问题，请检查字体文件是否正确放置在 `assets` 目录中

## 贡献指南
欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证
MIT License 