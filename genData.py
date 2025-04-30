import tushare as ts
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler

# 设置你的token
ts.set_token('6fd1045bfea4efe3513040d14cc42fc1c22bc629f7c978b37537508d')

# 初始化pro接口
pro = ts.pro_api()

# 将6位数字股票代码转换为带后缀的 ts_code
def format_ts_code(code):
    code = str(code).zfill(6)
    if code.startswith(('60', '68', '66')):
        return f"{code}.SH"
    else:
        return f"{code}.SZ"

# 获取股票日线数据
def get_stock_data(code, start_date, end_date):
    ts_code = format_ts_code(code)
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
    df = df.sort_values(by='trade_date')
    return df

# 计算相对强弱指标（RSI）
def rsi(close_prices, period):
    deltas = np.diff(close_prices)
    seed = deltas[:period + 1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down
    rsi = np.zeros_like(close_prices)
    rsi[:period] = 100. - 100. / (1. + rs)

    for i in range(period, len(close_prices)):
        delta = deltas[i - 1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)
    return rsi

# 计算威廉指标（W%R）
def williams_r(high_prices, low_prices, close_prices, period):
    hh = high_prices.rolling(window=period).max()
    ll = low_prices.rolling(window=period).min()
    wr = -100 * (hh - close_prices) / (hh - ll)
    return wr

# 计算简易波动指标（EMV）
def emv(high_prices, low_prices, volumes, period):
    m = (high_prices + low_prices) / 2
    dm = m - m.shift(1)
    br = (high_prices - low_prices) / volumes
    emv = dm / br
    emv_sma = emv.rolling(window=period).mean()
    return emv_sma

# 计算简单移动平均线（SMA）
def sma(close_prices, period):
    return close_prices.rolling(window=period).mean()

# 计算OBV能量潮
def obv(close_prices, volumes):
    obv = [0]
    for i in range(1, len(close_prices)):
        if close_prices[i] > close_prices[i - 1]:
            obv.append(obv[-1] + volumes[i])
        elif close_prices[i] < close_prices[i - 1]:
            obv.append(obv[-1] - volumes[i])
        else:
            obv.append(obv[-1])
    return pd.Series(obv, index=close_prices.index)

# 计算成交量变化率
def volume_change_rate(volumes):
    return pd.Series(volumes).pct_change().fillna(0)

# 计算成交额变化率
def amount_change_rate(amounts):
    return pd.Series(amounts).pct_change().fillna(0)

# 计算成交量移动平均
def volume_ma(volumes, period):
    return pd.Series(volumes).rolling(window=period).mean().fillna(0)

# 计算成交额移动平均
def amount_ma(amounts, period):
    return pd.Series(amounts).rolling(window=period).mean().fillna(0)

# 计算价格差分特征
def price_diff_features(data):
    # 一阶差分
    data['price_diff1'] = data['close'].diff()
    # 二阶差分
    data['price_diff2'] = data['price_diff1'].diff()
    # 收盘价变化率
    data['close_pct_change'] = data['close'].pct_change()
    # 价格动量
    data['momentum'] = data['close'] - data['close'].shift(5)
    return data

# 数据处理
def preprocess_data(data, seq_length, has_factor):
    if has_factor:
        # 计算技术指标
        data['rsi'] = rsi(data['close'], seq_length)
        data['williams_r'] = williams_r(data['high'], data['low'], data['close'], seq_length)
        data['emv'] = emv(data['high'], data['low'], data['vol'], seq_length)
        data['sma'] = sma(data['close'], seq_length)
        data['obv'] = obv(data['close'], data['vol'])
        data['vol_change'] = volume_change_rate(data['vol'])
        data['amount_change'] = amount_change_rate(data['amount'])
        data['vol_ma5'] = volume_ma(data['vol'], 5)
        data['vol_ma10'] = volume_ma(data['vol'], 10)
        data['amount_ma5'] = amount_ma(data['amount'], 5)
        data['amount_ma10'] = amount_ma(data['amount'], 10)
        data = price_diff_features(data)

    # 去除包含NaN的行
    data = data.dropna()

    scaler = MinMaxScaler()
    if has_factor:
        selected_features = [
            'rsi', 'williams_r', 'emv', 'sma', 'obv',
            'vol_change', 'amount_change', 'vol_ma5', 'vol_ma10', 'amount_ma5', 'amount_ma10',
            'price_diff1', 'price_diff2', 'close_pct_change', 'momentum'
        ]
    else:
        selected_features = ['open', 'high', 'low', 'close', 'pre_close', 'change', 'pct_chg', 'vol', 'amount']

    print("\n使用的特征:", selected_features)
    data = scaler.fit_transform(data[selected_features])

    X = []
    y = []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length])
        y.append(data[i+seq_length, 3])  # 选择收盘价作为目标值
    X = np.array(X)
    X = np.expand_dims(X, axis=1)
    y = np.array(y)
    return X, y, scaler

# 自定义数据集类
class StockDataset(Dataset):
    def __init__(self, X, y, device='cuda'):
        self.X = torch.tensor(X, dtype=torch.float32).to(device)
        self.y = torch.tensor(y, dtype=torch.float32).to(device)
    def __len__(self):
        return len(self.X)
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]