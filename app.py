import streamlit as st
import pandas as pd
import torch
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# 添加中文字体支持
plt.rcParams['font.sans-serif'] = ['DejaVu Sans']  # 使用 DejaVu Sans 字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
from genData import get_stock_data, preprocess_data, StockDataset, rsi, williams_r, emv, sma, obv, volume_change_rate, amount_change_rate, volume_ma, amount_ma, price_diff_features
from StockFundamentals import StockFundamentals
from new_mian import main
from bmodel import send_to_llm, continue_conversation  # 新增 continue_conversation 函数
import seaborn as sns

# 配置 Streamlit 页面
st.set_page_config(page_title="在线智能投资顾问", layout="wide")

# ---------------- 左侧参数栏 ----------------
st.sidebar.title("参数设置")

# 股票代码输入
stock_code = st.sidebar.text_input("请输入6位股票代码：", "002702")

# 日期选择，开始日期从2000年开始，结束日期为今天
start_date = st.sidebar.date_input("选择开始日期：", datetime(2024, 1, 1), min_value=datetime(2000, 1, 1), max_value=datetime.now())
end_date = st.sidebar.date_input("选择结束日期：", datetime(2025, 4, 25), min_value=datetime(2000, 1, 1), max_value=datetime.now())

# 基本面指标多选
fundamental_options = [
    "pe_ratio", "pb_ratio", "net_profit_margin", "roa", "roe",
    "market_cap", "dividend_yield", "eps", "debt_to_equity",
    "current_ratio", "quick_ratio", "total_assets", "total_liabilities",
    "total_revenue", "net_profit", "operating_income", "gross_profit_margin"
]
selected_fundamentals = st.sidebar.multiselect(
    "选择基本面指标（可多选）：",
    options=fundamental_options,
    default=["pe_ratio"]
)

# 序列长度选择
seq_length = st.sidebar.slider("选择序列长度（天数）", min_value=3, max_value=30, value=7)

# 是否使用技术指标复选框
use_technical_indicators = st.sidebar.checkbox("使用技术指标进行预测", value=True)

# 技术指标多选
tech_indicator_options = [
    'rsi', 'williams_r', 'emv', 'sma', 'obv',
    'vol_change', 'amount_change', 'vol_ma5', 'vol_ma10', 'amount_ma5', 'amount_ma10',
    'price_diff1', 'price_diff2', 'close_pct_change', 'momentum'
]
selected_tech_indicators = st.sidebar.multiselect(
    "选择技术指标（可多选）：",
    options=tech_indicator_options,
    default=['rsi']
)

# 查询按钮
query_button = st.sidebar.button("预测与分析")
# 基本面数据可视化按钮
fundamental_visualize_button = st.sidebar.button("基本面数据查询与可视化")
# 技术指标可视化按钮
tech_indicator_visualize_button = st.sidebar.button("技术指标查询与可视化")
# 新增：查询收盘价按钮
close_price_query_button = st.sidebar.button("收盘价查询与可视化")

# 继续对话输入框移到左侧
st.sidebar.subheader("投资咨询")
new_user_message = st.sidebar.text_input("根据投资报告请输入新的问题：")
send_button = st.sidebar.button("提问")

# 具体功能总结
st.sidebar.markdown("### 具体功能总结")
st.sidebar.markdown("- **预测与分析**：输入股票代码、日期范围等参数，进行股票价格预测，并调用大模型生成分析报告。")
st.sidebar.markdown("- **可视化基本面数据**：根据所选基本面指标，可视化展示股票的基本面数据。")
st.sidebar.markdown("- **可视化技术指标**：根据所选技术指标，可视化展示股票的技术指标与收盘价。")
st.sidebar.markdown("- **继续对话**：在已生成分析报告的基础上，输入新问题与大模型继续对话。")

# 初始化会话状态
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'first_input_data' not in st.session_state:
    st.session_state.first_input_data = None

# ---------------- 主界面显示 ----------------
st.title("📈 股票预测分析与投资报告")

if query_button:
    with st.spinner("加载数据与预测中，请稍候..."):
        try:
            # 获取股票数据
            raw_data = get_stock_data(stock_code, start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'))
            if raw_data is None or raw_data.empty:
                st.warning("未能获取股票数据，请检查股票代码或日期范围。")
                st.stop()

            # 获取基本面数据
            sf = StockFundamentals()
            fundamental_data = {}
            for name in selected_fundamentals:
                df = sf.get_stock_fundamental(start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'), stock_code, name)
                if df is not None and isinstance(df, pd.DataFrame) and name in df.columns:
                    fundamental_data[name] = df.reset_index()  # 确保有日期索引
                else:
                    st.warning(f"未能获取有效的基本面指标: {name}")

            # 模型预测
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            results = main(
                ts_code=stock_code,
                factor=use_technical_indicators,  # 传递是否使用技术指标的选择
                att=True,
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d'),
                seq_length=seq_length,
                device=device
            )

            # 展示股票数据
            st.subheader(f"【{stock_code}】 股票数据")
            st.dataframe(raw_data.tail(20))

            # 展示基本面数据
            st.subheader(f"【{stock_code}】 基本面数据")
            if fundamental_data:
                for name, data in fundamental_data.items():
                    st.markdown(f"#### {name}")
                    st.dataframe(data)
            else:
                st.info("未选择或未获取到任何基本面指标数据。")

            # 展示预测结果
            st.subheader(f"【{stock_code}】 股票预测结果")
            if 'next_day_pred' in results and 'latest_close' in results:
                st.write(f"预测次日收盘价: **{results['next_day_pred']:.2f}** 元")
                st.write(f"最新收盘价: **{results['latest_close']:.2f}** 元")
            else:
                st.warning("未能获取预测结果，请检查模型或数据。")

            # 绘制预测图表
            st.subheader(f"【{stock_code}】 预测图表")
            if 'chart_path' in results and results['chart_path'] and os.path.exists(results['chart_path']):
                st.image(results['chart_path'])
            else:
                st.warning("预测图表未能生成，请检查路径或生成过程。")

            # 调用大模型分析
            st.subheader("大模型分析报告")
            try:
                # 准备预测数据
                predictions = results.get('predictions')
                actuals = results.get('actuals')
                next_day_pred = results.get('next_day_pred')
                latest_close = results.get('latest_close')
                chart_path = results.get('chart_path')

                analysis_result, messages = send_to_llm(
                    ts_code=stock_code,
                    data=raw_data,
                    fundamental_data=fundamental_data,
                    fundamental_names=selected_fundamentals,
                    predictions=predictions,
                    actuals=actuals,
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d'),
                    next_day_pred=next_day_pred,
                    latest_close=latest_close,
                    chart_path=chart_path
                )

                st.session_state.messages = messages
                st.session_state.analysis_result = analysis_result
                st.session_state.first_input_data = messages[1]['content']  # 保存第一次输入的数据

                if analysis_result:
                    st.markdown(analysis_result)
                else:
                    st.warning("未能生成大模型分析报告，请检查API调用或数据。")
            except Exception as e:
                st.error(f"调用大模型分析时出错: {e}")

        except Exception as e:
            st.error(f"发生错误: {e}")

if fundamental_visualize_button:
    st.subheader(f"【{stock_code}】 基本面数据可视化")
    # 获取基本面数据
    sf = StockFundamentals()
    fundamental_data = {}
    for name in selected_fundamentals:
        df = sf.get_stock_fundamental(start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'), stock_code, name)
        if df is not None and isinstance(df, pd.DataFrame) and name in df.columns:
            fundamental_data[name] = df.reset_index()  # 确保有日期索引
        else:
            st.warning(f"未能获取有效的基本面指标: {name}")

    if fundamental_data:
        for name, data in fundamental_data.items():
            st.markdown(f"#### {name}")
            st.dataframe(data)
            fig, ax = plt.subplots(figsize=(15, 7))
            data['date'] = pd.to_datetime(data['date'])
            ax.plot(data['date'], data[name], label=name)
            ax.set_xlabel('日期')
            ax.set_ylabel(name)
            ax.set_title(f'{stock_code} {name} 走势')
            ax.legend()

            # 计算时间间隔
            time_delta = (end_date - start_date).days
            if time_delta > 3 * 365:
                ax.xaxis.set_major_locator(mdates.YearLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            elif 365 < time_delta <= 3 * 365:
                ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            elif 30 < time_delta <= 365:
                ax.xaxis.set_major_locator(mdates.MonthLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            elif 7 < time_delta <= 30:
                ax.xaxis.set_major_locator(mdates.WeekdayLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            else:
                ax.xaxis.set_major_locator(mdates.DayLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

            plt.xticks(rotation=45)
            st.pyplot(fig)
    else:
        st.info("未选择或未获取到任何基本面指标数据。")

if tech_indicator_visualize_button:
    st.subheader(f"【{stock_code}】 技术指标与收盘价可视化")
    # 获取股票数据
    raw_data = get_stock_data(stock_code, start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'))
    if raw_data is None or raw_data.empty:
        st.warning("未能获取股票数据，请检查股票代码或日期范围。")
    else:
        raw_data['trade_date'] = pd.to_datetime(raw_data['trade_date'])
        for indicator in selected_tech_indicators:
            fig, ax1 = plt.subplots(figsize=(15, 7))
            ax2 = ax1.twinx()

            # 绘制收盘价
            ax1.plot(raw_data['trade_date'], raw_data['close'], label='收盘价', color='blue')
            ax1.set_xlabel('日期')
            ax1.set_ylabel('收盘价 (元)', color='blue')

            # 计算并绘制所选技术指标
            if indicator == 'rsi':
                values = rsi(raw_data['close'], seq_length)
            elif indicator == 'williams_r':
                values = williams_r(raw_data['high'], raw_data['low'], raw_data['close'], seq_length)
            elif indicator == 'emv':
                values = emv(raw_data['high'], raw_data['low'], raw_data['vol'], seq_length)
            elif indicator == 'sma':
                values = sma(raw_data['close'], seq_length)
            elif indicator == 'obv':
                values = obv(raw_data['close'], raw_data['vol'])
            elif indicator == 'vol_change':
                values = volume_change_rate(raw_data['vol'])
            elif indicator == 'amount_change':
                values = amount_change_rate(raw_data['amount'])
            elif indicator == 'vol_ma5':
                values = volume_ma(raw_data['vol'], 5)
            elif indicator == 'vol_ma10':
                values = volume_ma(raw_data['vol'], 10)
            elif indicator == 'amount_ma5':
                values = amount_ma(raw_data['amount'], 5)
            elif indicator == 'amount_ma10':
                values = amount_ma(raw_data['amount'], 10)
            elif indicator in ['price_diff1', 'price_diff2', 'close_pct_change', 'momentum']:
                data_with_features = price_diff_features(raw_data.copy())
                values = data_with_features[indicator]

            ax2.plot(raw_data['trade_date'], values, label=indicator, color='red')
            ax2.set_ylabel(indicator, color='red')

            lines, labels = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines + lines2, labels + labels2, loc='upper left')

            plt.title(f'{stock_code} 收盘价与 {indicator} 技术指标')
            plt.xticks(rotation=45)
            st.pyplot(fig)

if close_price_query_button:
    st.subheader(f"【{stock_code}】 收盘价查询与可视化")
    # 获取股票数据
    raw_data = get_stock_data(stock_code, start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d'))
    if raw_data is None or raw_data.empty:
        st.warning("未能获取股票数据，请检查股票代码或日期范围。")
    else:
        raw_data['trade_date'] = pd.to_datetime(raw_data['trade_date'])
        # 展示收盘价数据
        st.markdown("#### 收盘价数据")
        st.dataframe(raw_data[['trade_date', 'close']])
        # 可视化收盘价
        fig, ax = plt.subplots(figsize=(15, 7))
        ax.plot(raw_data['trade_date'], raw_data['close'], label='收盘价', color='blue')
        ax.set_xlabel('日期')
        ax.set_ylabel('收盘价 (元)')
        ax.set_title(f'{stock_code} 收盘价走势')
        ax.legend()

        # 计算时间间隔
        time_delta = (end_date - start_date).days
        if time_delta > 3 * 365:
            ax.xaxis.set_major_locator(mdates.YearLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        elif 365 < time_delta <= 3 * 365:
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        elif 30 < time_delta <= 365:
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        elif 7 < time_delta <= 30:
            ax.xaxis.set_major_locator(mdates.WeekdayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        plt.xticks(rotation=45)
        st.pyplot(fig)

if send_button and st.session_state.messages:
    with st.spinner("正在生成对话，请稍候..."):
        response_text, new_messages = continue_conversation(st.session_state.messages, new_user_message)
    if response_text:
        st.session_state.messages = new_messages

        # 显示对话历史
        st.subheader("对话记录")
        for i, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                if i > 1:  # 第一次分析报告不显示对话历史
                    st.markdown(f'<p style="color:red; font-size:20px;">用户: {message["content"]}</p>', unsafe_allow_html=True)
            elif message["role"] == "assistant":
                st.markdown(f'助手: {message["content"]}')