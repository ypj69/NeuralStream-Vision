import os
import pandas as pd
import base64
from datetime import datetime
import torch
import requests
import logging
import time
from genData import get_stock_data, preprocess_data, StockDataset
from StockFundamentals import StockFundamentals
from new_mian import main

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("llm_analysis.log"), logging.StreamHandler()]
)

def configure_proxy():
    proxy_server = os.getenv("PROXY_SERVER")
    if proxy_server:
        proxies = {"http": proxy_server, "https": proxy_server}
        logging.info(f"已启用全局代理: {proxy_server}")
        return proxies
    else:
        logging.info("未配置代理")
        return None

def call_qwen_api(api_key, model, messages, temperature=0.3, top_p=0.9, max_tokens=2048, proxies=None, max_retries=5):
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "input": {"messages": messages},
        "parameters": {
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens
        }
    }

    retry_count = 0
    last_exception = None

    while retry_count < max_retries:
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                proxies=proxies,
                timeout=60
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout as e:
            last_exception = e
            retry_count += 1
            wait_time = 2 ** retry_count  # 指数退避
            logging.warning(f"请求超时，正在进行第 {retry_count}/{max_retries} 次重试，等待 {wait_time}秒...")
            time.sleep(wait_time)

        except requests.exceptions.ConnectionError as e:
            last_exception = e
            retry_count += 1
            wait_time = 5  # 固定等待时间
            logging.warning(f"连接错误，正在进行第 {retry_count}/{max_retries} 次重试，等待 {wait_time}秒...")
            time.sleep(wait_time)

        except Exception as e:
            last_exception = e
            logging.error(f"API调用失败: {str(e)}")
            break

    logging.error(f"API调用失败，已达最大重试次数 {max_retries}")
    if last_exception:
        logging.error(f"最后错误信息: {str(last_exception)}")
    return None

def send_to_llm(ts_code, data, fundamental_data, fundamental_names, predictions, actuals,
                start_date, end_date, next_day_pred, latest_close, chart_path=None):
    api_key = 'sk-1fb68d81bbb24766b9f020f118507139'
    if not api_key:
        raise ValueError("请设置通义 API Key")

    proxies = configure_proxy()
    model = "qwen-plus"

    # 处理往前90天的收盘价数据
    last_90_days_close = data['close'].iloc[-90:-1].tolist()
    last_90_days_close_str = ', '.join([f'{val:.2f}' for val in last_90_days_close])

    # 处理所有预测数据
    all_predictions = predictions[-90:-1].tolist()
    all_predictions_str = ', '.join([f'{val:.2f}' for val in all_predictions])

    # 基础数据总结
    data_summary = f"""
【股票基本信息】
股票代码: {ts_code}
分析时段: {start_date} 至 {end_date}
最新交易日: {end_date}
最新收盘价: {latest_close:.2f}
{end_date}往前90天的收盘价数据：{last_90_days_close_str}
预测次日收盘价: {next_day_pred:.2f} ({'+' if next_day_pred > latest_close else ''}{((next_day_pred - latest_close)/latest_close*100):.2f}%)
所有预测数据: {all_predictions_str}

【近期价格走势】
5日波动率: {data['close'].pct_change().std() * 100:.2f}%
5日涨跌幅: {data['close'].pct_change().iloc[-5]:.2f}%
20日波动率: {data['close'].pct_change().rolling(20).std().values[-1] * 100:.2f}%
20日涨跌幅: {data['close'].pct_change().rolling(20).mean().values[-1]:.2f}%
60日波动率: {data['close'].pct_change().rolling(60).std().values[-1] * 100:.2f}%
60日涨跌幅: {data['close'].pct_change().rolling(60).mean().values[-1]:.2f}%
5日均线: {data['close'].rolling(5).mean().values[-1]:.2f}
20日均线: {data['close'].rolling(20).mean().values[-1]:.2f}
60日均线: {data['close'].rolling(60).mean().values[-1]:.2f}

【模型表现评估】
测试集样本数: {len(actuals)}
平均绝对误差(MAE): {abs(predictions - actuals).mean():.2f}
最大单日误差: {abs(predictions - actuals).max():.2f}
"""

    if isinstance(fundamental_data, dict) and fundamental_data:
        data_summary += "\n【基本面指标】"
        for name in fundamental_names:
            if name in fundamental_data and not fundamental_data[name].empty:
                df = fundamental_data[name]
                if name in df.columns:
                    current_val = df[name].iloc[-1]
                    mean_val = df[name].mean()
                    data_summary += f"\n{name}：当前值 = {current_val:.2f}，历史均值 = {mean_val:.2f}"
    elif isinstance(fundamental_data, pd.DataFrame) and not fundamental_data.empty:
        data_summary += "\n【基本面指标】"
        for name in fundamental_names:
            if name in fundamental_data.columns:
                current_val = fundamental_data[name].iloc[-1]
                mean_val = fundamental_data[name].mean()
                data_summary += f"\n{name}：当前值 = {current_val:.2f}，历史均值 = {mean_val:.2f}"

    system_prompt = """你是具有十年经验的金牌证券分析师，请用专业但通俗的中文撰写一份股票投资分析报告，内容包括：
• 技术面与基本面综合分析
• 明确可操作的投资建议
• 风险预警（至少3个具体风险点）
• 仓位管理策略（含止损止盈建议）
• 第二天买卖操作推荐"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": data_summary}
    ]

    if chart_path and os.path.exists(chart_path):
        messages.append({
            "role": "user",
            "content": "（请根据上述数值进行分析）"
        })

    logging.info("正在调用通义千问 API...")
    response_data = call_qwen_api(api_key, model, messages, proxies=proxies)

    if response_data:
        output_text = response_data.get("output", {}).get("text", "")
        if not output_text:
            output_text = response_data.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
        logging.info("API 调用成功")
        print("🔍 通义千问专业分析报告生成完毕\n")
        print(output_text)

        # 保存报告
        report_path = f"{ts_code}_analysis_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# {ts_code} 股票投资分析报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(output_text)
        print(f"\n✅ 报告已保存至: {report_path}")

        # 添加助手的回复到消息记录
        messages.append({"role": "assistant", "content": output_text})
        return output_text, messages

    logging.error("API调用失败，未能生成分析报告")
    return None, []
def continue_conversation(messages, new_user_message):
    api_key = 'sk-1fb68d81bbb24766b9f020f118507139'
    if not api_key:
        raise ValueError("请设置通义 API Key")

    proxies = configure_proxy()
    model = "qwen-plus"

    new_messages = messages + [{"role": "user", "content": new_user_message}]

    logging.info("正在继续与通义千问对话...")
    response_data = call_qwen_api(api_key, model, new_messages, proxies=proxies)

    if response_data:
        output_text = response_data.get("output", {}).get("text", "")
        if not output_text:
            output_text = response_data.get("output", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
        logging.info("继续对话 API 调用成功")
        print("🔍 通义千问继续对话回复完毕\n")
        print(output_text)

        # 添加新的回复到消息记录
        new_messages.append({"role": "assistant", "content": output_text})
        return output_text, new_messages

    logging.error("继续对话 API 调用失败，未能获取回复")
    return None, []

if __name__ == "__main__":
    stock_code = '600589'
    start_date = '20240101'
    end_date = '20250423'
    seq_length = 7

    fundamental_names = [
        "pe_ratio", "pb_ratio", "net_profit_margin", "roa", "roe",
        "market_cap", "dividend_yield", "eps", "debt_to_equity"
    ]

    raw_data = get_stock_data(stock_code, start_date, end_date)
    sf = StockFundamentals()

    fundamental_dict = {}
    fundamental_df = pd.DataFrame()

    for name in fundamental_names:
        df = sf.get_stock_fundamental(start_date, end_date, stock_code, name)
        if df is not None and isinstance(df, pd.DataFrame) and name in df.columns:
            fundamental_dict[name] = df
            if fundamental_df.empty:
                fundamental_df = df.copy()
            else:
                fundamental_df[name] = df[name]

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    results = main(
        ts_code=stock_code,
        factor=False,
        att=True,
        start_date=start_date,
        end_date=end_date,
        seq_length=seq_length,
        device=device
    )

    analysis_result, messages = send_to_llm(
        ts_code=stock_code,
        data=raw_data,
        fundamental_data=fundamental_dict,
        fundamental_names=fundamental_names,
        predictions=results['predictions'],
        actuals=results['actuals'],
        start_date=start_date,
        end_date=end_date,
        next_day_pred=results['next_day_pred'],
        latest_close=results['latest_close'],
        chart_path=results['chart_path']
    )

    if not analysis_result:
        logging.warning("第一次分析失败，尝试使用DataFrame格式重试...")
        analysis_result, messages = send_to_llm(
            ts_code=stock_code,
            data=raw_data,
            fundamental_data=fundamental_df,
            fundamental_names=fundamental_names,
            predictions=results['predictions'],
            actuals=results['actuals'],
            start_date=start_date,
            end_date=end_date,
            next_day_pred=results['next_day_pred'],
            latest_close=results['latest_close'],
            chart_path=results['chart_path']
        )

    # 模拟继续对话
    new_user_message = "请进一步分析风险点的影响程度"
    response_text, new_messages = continue_conversation(messages, new_user_message)