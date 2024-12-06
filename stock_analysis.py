import akshare as ak
import pandas as pd
from datetime import datetime

def get_stock_data():
    print("正在获取股票数据，请稍候...")
    # 获取上证所有股票的实时行情
    try:
        stock_zh_a_spot_df = ak.stock_zh_a_spot()
        print("数据获取成功，正在处理...")
        print("可用的列名：", stock_zh_a_spot_df.columns.tolist())
        print(f"原始数据行数: {len(stock_zh_a_spot_df)}")
    except Exception as e:
        print(f"获取数据失败：{e}")
        raise
    
    # 选择需要的列
    columns = ['代码', '名称', '最新价', '涨跌额', '涨跌幅', '买入', '卖出', '昨收', '今开', '最高', '最低', '成交量', '成交额', '时间戳']
    df = stock_zh_a_spot_df[columns]
    print(f"选择列后数据行数: {len(df)}")
    # 检查数据是否为空
    if df.empty:
        print("警告：筛选后的数据为空！")
        print("样本数据：")
        print(stock_zh_a_spot_df['代码'].head())
        raise Exception("没有找到符合条件的股票数据")
    
    # 按照涨跌幅排序
    df = df.sort_values('涨跌幅', ascending=False)
    
    # 生成文件名（包含当前日期）
    today = datetime.now().strftime('%Y%m%d')
    filename = f'上证股票行情_{today}.xlsx'
    
    # 添加一些基本的统计信息
    stats = pd.DataFrame({
        '统计项': ['平均价格', '平均涨跌幅', '最大涨幅', '最大跌幅', '平均成交额(万)'],
        '数值': [
            df['最新价'].mean(),
            df['涨跌幅'].mean(),
            df['涨跌幅'].max(),
            df['涨跌幅'].min(),
            df['成交额'].mean() / 10000  # 转换为万元
        ]
    })
    
    # 创建Excel写入器
    with pd.ExcelWriter(filename) as writer:
        # 写入主要数据
        df.to_excel(writer, sheet_name='股票行情', index=False)
        # 写入统计数据
        stats.to_excel(writer, sheet_name='统计分析', index=False)
        
    print(f'数据已保存到文件：{filename}')
    return filename

if __name__ == '__main__':
    try:
        filename = get_stock_data()
        print('数据获取和分析完成！')
    except Exception as e:
        print(f'发生错误：{e}')
