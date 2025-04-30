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
- 自动配置中文字体支持，确保图表正确显示中文

## 安装说明

1. 克隆项目
```bash
git clone https://github.com/ypj69/NeuralStream-Vision.git
cd new_2
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置API密钥
- 在 `bmodel.py` 中配置通义千问API密钥
- 在 `genData.py` 中配置Tushare API密钥
- 在 `StockFundamentals.py` 中配置米筐API密钥

4. 中文字体配置
- 系统会自动下载并配置思源黑体（Source Han Sans）
- 首次运行时会自动下载字体文件到 `fonts` 目录
- 如果遇到字体下载问题，可以手动下载思源黑体并放置在 `fonts` 目录下

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
FinRL_LLM/
├── app.py                 # Streamlit Web应用主文件
├── bmodel.py              # 大语言模型相关功能
├── genData.py             # 数据获取和预处理
├── new_mian.py            # 深度学习模型主文件
├── StockFundamentals.py   # 基本面分析模块
├── font_config.py         # 中文字体配置模块
├── fonts/                 # 字体文件目录
├── requirements.txt       # 项目依赖
└── README.md              # 项目说明文档
```

## 注意事项
- 使用前请确保已正确配置所有必要的API密钥
- 建议使用GPU进行模型训练和预测
- 请遵守相关API的使用条款和限制
- 首次运行时需要联网下载中文字体文件
- 如果在云端部署时遇到字体问题，请确保 `fonts` 目录具有写入权限

## 贡献指南
欢迎提交Issue和Pull Request来帮助改进项目。

## 许可证
MIT License 