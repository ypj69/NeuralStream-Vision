import rqdatac as rq
from datetime import datetime

class StockFundamentals:
    def __init__(self):
        # 初始化米筐API
        try:
            rq.init('13220075013','Qhw821564698')
            print("米筐API初始化成功")
        except Exception as e:
            print(f"米筐API初始化失败: {e}")

    def get_stock_fundamental(self, start_date, end_date, stock_code, fundamental_name):
        """
        获取股票的基本面数据。
        :param start_date: 开始时间 (格式: 'YYYYMMDD')
        :param end_date: 结束时间 (格式: 'YYYYMMDD')
        :param stock_code: 股票代码 (前6位数字)
        :param fundamental_name: 基本面指标名称
        :return: 基本面数据
        """
        try:
            # 将日期从'YYYYMMDD'格式转换为'YYYY-MM-DD'格式
            start_date = self.format_date(start_date)
            end_date = self.format_date(end_date)

            # 补全股票代码为完整的格式（如：'000001.XSHE'）
            stock_code = self.complete_stock_code(stock_code)

            # 根据基本面名称调用相应的方法
            if hasattr(self, fundamental_name):
                method = getattr(self, fundamental_name)
                return method(start_date, end_date, stock_code)
            else:
                raise ValueError(f"未找到基本面指标方法: {fundamental_name}")
        except Exception as e:
            print(f"获取基本面数据失败: {e}")
            return None

    def format_date(self, date_str):
        """
        将日期从'YYYYMMDD'格式转换为'YYYY-MM-DD'格式。
        :param date_str: 输入日期字符串（'YYYYMMDD'）
        :return: 转换后的日期字符串（'YYYY-MM-DD'）
        """
        return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"

    def complete_stock_code(self, stock_code):
        """
        将6位股票代码补全为米筐所需的完整格式。
        :param stock_code: 6位股票代码
        :return: 完整股票代码
        """
        all_instruments = rq.all_instruments(type="CS")
        matched_stocks = all_instruments[all_instruments['order_book_id'].str.startswith(stock_code)]
        if not matched_stocks.empty:
            return matched_stocks.iloc[0]['order_book_id']
        else:
            raise ValueError(f"未找到匹配的股票代码: {stock_code}")

    def pe_ratio(self, start_date, end_date, stock_code):
        """市盈率"""
        return rq.get_factor(stock_code, 'pe_ratio', start_date=start_date, end_date=end_date)

    def pb_ratio(self, start_date, end_date, stock_code):
        """市净率"""
        return rq.get_factor(stock_code, 'pb_ratio', start_date=start_date, end_date=end_date)

    def market_cap(self, start_date, end_date, stock_code):
        """总市值"""
        return rq.get_factor(stock_code, 'market_cap', start_date=start_date, end_date=end_date)

    def dividend_yield(self, start_date, end_date, stock_code):
        """股息率"""
        return rq.get_factor(stock_code, 'dividend_yield', start_date=start_date, end_date=end_date)

    def eps(self, start_date, end_date, stock_code):
        """每股收益"""
        return rq.get_factor(stock_code, 'eps', start_date=start_date, end_date=end_date)

    def roe(self, start_date, end_date, stock_code):
        """净资产收益率"""
        return rq.get_factor(stock_code, 'roe', start_date=start_date, end_date=end_date)

    def roa(self, start_date, end_date, stock_code):
        """总资产收益率"""
        return rq.get_factor(stock_code, 'roa', start_date=start_date, end_date=end_date)

    def net_profit_margin(self, start_date, end_date, stock_code):
        """净利率"""
        return rq.get_factor(stock_code, 'net_profit_margin', start_date=start_date, end_date=end_date)

    def debt_to_equity(self, start_date, end_date, stock_code):
        """资产负债率"""
        return rq.get_factor(stock_code, 'debt_to_equity', start_date=start_date, end_date=end_date)

    def current_ratio(self, start_date, end_date, stock_code):
        """流动比率"""
        return rq.get_factor(stock_code, 'current_ratio', start_date=start_date, end_date=end_date)

    def quick_ratio(self, start_date, end_date, stock_code):
        """速动比率"""
        return rq.get_factor(stock_code, 'quick_ratio', start_date=start_date, end_date=end_date)

    def total_assets(self, start_date, end_date, stock_code):
        """总资产"""
        return rq.get_factor(stock_code, 'total_assets', start_date=start_date, end_date=end_date)

    def total_liabilities(self, start_date, end_date, stock_code):
        """总负债"""
        return rq.get_factor(stock_code, 'total_liabilities', start_date=start_date, end_date=end_date)

    def total_revenue(self, start_date, end_date, stock_code):
        """总收入"""
        return rq.get_factor(stock_code, 'total_revenue', start_date=start_date, end_date=end_date)

    def net_profit(self, start_date, end_date, stock_code):
        """净利润"""
        return rq.get_factor(stock_code, 'net_profit', start_date=start_date, end_date=end_date)

    def operating_income(self, start_date, end_date, stock_code):
        """营业收入"""
        return rq.get_factor(stock_code, 'operating_income', start_date=start_date, end_date=end_date)

    def gross_profit_margin(self, start_date, end_date, stock_code):
        """毛利率"""
        return rq.get_factor(stock_code, 'gross_profit_margin', start_date=start_date, end_date=end_date)

# 示例用法
if __name__ == "__main__":
    sf = StockFundamentals()

    # 设置查询参数
    start_date = "20230101"
    end_date = "20231231"
    stock_code = "000001"  # 平安银行的股票代码前6位
    fundamental_name = "pe_ratio"

    # 获取基本面数据
    data = sf.get_stock_fundamental(start_date, end_date, stock_code, fundamental_name)
    if data is not None:
        print(data)
