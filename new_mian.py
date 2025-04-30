import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
import pandas as pd
from sklearn.metrics import mean_squared_error
from torch.utils.data import Dataset, DataLoader
from torch.optim.lr_scheduler import ReduceLROnPlateau
from genData import get_stock_data, preprocess_data, StockDataset, rsi, williams_r, emv, sma, obv
import random
import matplotlib.pyplot as plt
import matplotlib as mpl
from StockFundamentals import StockFundamentals

print("程序开始运行...")

# 设置随机种子
seed = 42
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)

# 检查是否有可用的GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f'使用设备: {device}')

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False    # 用来正常显示负号

class CNN_LSTM(nn.Module):
    def __init__(self, input_size, seq_length, use_att):
        super(CNN_LSTM, self).__init__()
        # CNN部分
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=(3, 3), padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool2d(kernel_size=(2, 2))
        
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(3, 3), padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool2d(kernel_size=(2, 2))
        
        self.use_att = use_att

        # 计算CNN输出的特征维度
        self.fc_input_dim = self._get_conv_output_dim(input_size, seq_length)

        # LSTM部分
        self.lstm1 = nn.LSTM(input_size=self.fc_input_dim, hidden_size=256, num_layers=2, batch_first=True, bidirectional=True)
        self.lstm2 = nn.LSTM(input_size=512, hidden_size=256, num_layers=2, batch_first=True, bidirectional=True)

        # 定义自注意力机制的线性层
        self.query = nn.Linear(512, 512)
        self.key = nn.Linear(512, 512)
        self.value = nn.Linear(512, 512)
        self.softmax = nn.Softmax(dim=-1)

        # Dropout层
        self.dropout = nn.Dropout(0.3)

        # 全连接层
        self.fc1 = nn.Linear(512, 256)
        self.fc2 = nn.Linear(256, 64)
        self.fc3 = nn.Linear(64, 1)
        
        # 激活函数
        self.leaky_relu = nn.LeakyReLU(0.1)

    def _get_conv_output_dim(self, input_size, seq_length):
        x = torch.randn(1, 1, seq_length, input_size)
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu2(x)
        x = self.pool2(x)
        return x.view(1, -1).size(1)

    def forward(self, x):
        # CNN部分
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.pool1(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu2(x)
        x = self.pool2(x)

        # 展平特征
        x = x.view(x.size(0), 1, -1)

        # 双向LSTM部分
        lstm_out1, _ = self.lstm1(x)
        lstm_out2, _ = self.lstm2(lstm_out1)
        
        # 残差连接
        lstm_out = lstm_out1 + lstm_out2

        if self.use_att:
            # 多头注意力机制
            Q = self.query(lstm_out)
            K = self.key(lstm_out)
            V = self.value(lstm_out)
            
            # 计算注意力得分
            attn_scores = torch.matmul(Q, K.transpose(-2, -1)) / torch.sqrt(torch.tensor(512, dtype=torch.float32))
            attn_weights = self.softmax(attn_scores)
            attn_output = torch.matmul(attn_weights, V)
            
            # 残差连接
            x = lstm_out + attn_output
            x = torch.mean(x, dim=1)
        else:
            x = lstm_out[:, -1, :]

        # 多层全连接
        x = self.dropout(x)
        x = self.fc1(x)
        x = self.leaky_relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        x = self.leaky_relu(x)
        x = self.fc3(x)
        
        return x


# 训练模型
def train_model(model, train_loader, criterion, optimizer, epochs, scheduler):
    model.train()
    best_loss = float('inf')
    patience = 5
    counter = 0
    for epoch in range(epochs):
        running_loss = 0.0
        for inputs, labels in train_loader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs.squeeze(), labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        epoch_loss = running_loss / len(train_loader)
        print(f'Epoch {epoch + 1}/{epochs}, Loss: {epoch_loss}')

        # 调整学习率
        scheduler.step(epoch_loss)

        # 早停策略
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            counter = 0
        else:
            counter += 1
            if counter >= patience:
                print("Early stopping!")
                break


# 测试模型
def test_model(model, test_loader, scaler, input_size):
    model.eval()
    predictions = []
    actuals = []
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            predictions.extend(outputs.squeeze().cpu().tolist())  # 确保输出是1D
            actuals.extend(labels.squeeze().cpu().tolist())        # 确保标签是1D

    # 转换为一维数组
    predictions = np.array(predictions).flatten()  # 改为flatten()
    actuals = np.array(actuals).flatten()          # 改为flatten()

    # 反归一化（保持原有逻辑）
    close_range = scaler.data_range_[3]
    close_min = scaler.data_min_[3]
    predictions = predictions * close_range + close_min
    actuals = actuals * close_range + close_min

    # 计算MSE
    mse = mean_squared_error(actuals, predictions)
    print(f"测试集的MSE: {mse}")

    return predictions, actuals


def plot_predictions(predictions, actuals, title='股票价格预测对比', save_path=None):
    plt.figure(figsize=(15, 7))
    x = range(len(actuals))
    plt.plot(x, actuals, label='实际值', color='blue', linewidth=2)
    plt.plot(x, predictions, label='预测值', color='red', linestyle='--', linewidth=2)
    
    plt.title(title, fontsize=15, pad=15)
    plt.xlabel('测试集样本索引', fontsize=12)
    plt.ylabel('股票价格 (元)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图表已保存至: {save_path}")
    plt.close()


def plot_tech_indicators(data, seq_length, has_factor, save_path=None):
    if has_factor:
        plt.figure(figsize=(15, 10))
        
        # 绘制收盘价
        plt.subplot(2, 1, 1)
        plt.plot(data['close'], label='收盘价', color='blue')
        plt.title('收盘价与技术指标', fontsize=15)
        plt.ylabel('价格', fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # 绘制技术指标
        plt.subplot(2, 1, 2)
        data['rsi'] = rsi(data['close'], seq_length)
        data['williams_r'] = williams_r(data['high'], data['low'], data['close'], seq_length)
        data['emv'] = emv(data['high'], data['low'], data['vol'], seq_length)
        data['sma'] = sma(data['close'], seq_length)
        data['obv'] = obv(data['close'], data['vol'])
        
        plt.plot(data['rsi'], label='RSI', color='red')
        plt.plot(data['williams_r'], label='威廉指标', color='green')
        plt.plot(data['emv'], label='EMV', color='purple')
        plt.plot(data['sma'], label='SMA', color='orange')
        plt.plot(data['obv'], label='OBV', color='brown')
        
        plt.xlabel('日期', fontsize=12)
        plt.ylabel('指标值', fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"技术指标图表已保存至: {save_path}")
        plt.close()


def predict_next_day(model, last_sequence, scaler):
    model.eval()
    with torch.no_grad():
        # 准备输入数据
        x = torch.tensor(last_sequence, dtype=torch.float32).unsqueeze(0).to(device)
        # 进行预测
        prediction = model(x)
        # 转换预测结果
        prediction = prediction.cpu().numpy()
        # 反归一化
        close_range = scaler.data_range_[3]
        close_min = scaler.data_min_[3]
        prediction = prediction * close_range + close_min
    return prediction[0][0]


# 主函数
def main(ts_code, factor, att, save_dir='results', 
        start_date='20200101', end_date='20231231',
        seq_length=7, device=None):
    """完整的股票预测主函数
    
    参数:
        ts_code: 股票代码
        factor: 是否使用因子数据
        att: 是否使用注意力机制
        save_dir: 结果保存路径
        start_date: 数据开始日期 (格式YYYYMMDD)
        end_date: 数据结束日期 (格式YYYYMMDD)
        seq_length: 序列长度
        device: 计算设备 (自动检测GPU)
    """
    import os
    import torch
    from torch.utils.data import DataLoader
    
    # 自动检测计算设备
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    os.makedirs(save_dir, exist_ok=True)
    
    # 获取数据（使用参数传递的日期）
    data = get_stock_data(ts_code, start_date, end_date)
    
    # 数据处理（显式传递seq_length和has_factor）
    X, y, scaler = preprocess_data(data, seq_length, has_factor=factor)

    # 划分数据集
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # 创建数据加载器（使用传入的device）
    train_dataset = StockDataset(X_train, y_train, device)
    test_dataset = StockDataset(X_test, y_test, device)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # 初始化模型
    input_size = X_train.shape[-1]
    model = CNN_LSTM(input_size, seq_length, att).to(device)
    
    # 训练配置
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = ReduceLROnPlateau(optimizer, 'min', patience=3)
    
    # 训练模型
    train_model(model, train_loader, criterion, optimizer, 50, scheduler)
    
    # 测试模型
    predictions, actuals = test_model(model, test_loader, scaler, input_size)
    
    # 保存结果
    results_df = pd.DataFrame({
        '实际价格': actuals,
        '预测价格': predictions,
        '误差': predictions - actuals
    })
    results_path = os.path.join(save_dir, 'predictions.csv')
    results_df.to_csv(results_path, index=False)
    
    # 可视化预测结果
    chart_path = os.path.join(save_dir, 'prediction_chart.png')
    plot_predictions(predictions, actuals, 
                    title=f'{ts_code}股票价格预测对比图',
                    save_path=chart_path)
    
    # 可视化技术指标和收盘价
    tech_chart_path = os.path.join(save_dir, 'tech_indicators_chart.png')
    plot_tech_indicators(data, seq_length, factor, save_path=tech_chart_path)
    
    # 预测下个交易日
    latest_close = data.iloc[-1]['close']
    last_sequence = X[-1]
    next_day_pred = predict_next_day(model, last_sequence, scaler)
    
    return {
        'predictions': predictions,
        'actuals': actuals,
        'next_day_pred': next_day_pred,
        'latest_close': latest_close,
        'results_path': results_path,
        'chart_path': chart_path,
        'tech_chart_path': tech_chart_path,
        'model': model
    }

if __name__ == "__main__":
    print("进入主程序...")
    ## 选择的时间段
    # 配置参数
    start_date = '20240101'
    end_date = '20250423'
    stock_code = '000001'
    seq_length = 7
    
    # 运行主程序
    results = main(
        ts_code=stock_code,
        factor=False,
        att=True,
        start_date=start_date,   # 传递日期参数
        end_date=end_date,
        seq_length=seq_length,   # 传递序列长度
        device=device            # 传递计算设备
    )
    
    # 打印关键信息
    print("\n关键结果摘要：")
    print(f"最新收盘价: {results['latest_close']:.2f}")
    print(f"预测次日收盘价: {results['next_day_pred']:.2f}")
    print(f"预测结果已保存至: {results['results_path']}")
    print(f"可视化图表已保存至: {results['chart_path']}")
    print(f"技术指标可视化图表已保存至: {results['tech_chart_path']}")
    sf = StockFundamentals()
    fundamental_name = "pe_ratio"
    # 获取基本面数据
    fundamental_data = sf.get_stock_fundamental(start_date, end_date, stock_code, fundamental_name)
    data = get_stock_data(stock_code, start_date, end_date)
    print(data)
    print(fundamental_data)