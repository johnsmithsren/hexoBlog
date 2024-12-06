---
title: 再学python
date: 2024-12-06 16:00:00
categories:
  - 编程
tags:
  - Python
  - 学习笔记
---
## 实战项目示例：股票数据分析

这里是一个使用Python获取和分析股票数据的实际例子，展示了Python在数据处理方面的强大能力：

```python
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
    columns = ['代码', '名称', '最新价', '涨跌额', '涨跌幅', '买入', '卖出', 
              '昨收', '今开', '最高', '最低', '成交量', '成交额', '时间戳']
    df = stock_zh_a_spot_df[columns]
    
    # 按照涨跌幅排序
    df = df.sort_values('涨跌幅', ascending=False)
    
    # 生成文件名（包含当前日期）
    today = datetime.now().strftime('%Y%m%d')
    filename = f'上证股票行情_{today}.xlsx'
    
    # 添加统计信息
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
    
    # 保存到Excel
    with pd.ExcelWriter(filename) as writer:
        df.to_excel(writer, sheet_name='股票行情', index=False)
        stats.to_excel(writer, sheet_name='统计分析', index=False)
    
    return filename

if __name__ == '__main__':
    try:
        filename = get_stock_data()
        print('数据获取和分析完成！')
    except Exception as e:
        print(f'发生错误：{e}')
```

这个例子展示了Python在实际应用中的几个重要特点：

1. **数据获取**：使用 `akshare` 库获取实时股票数据
2. **数据处理**：使用 `pandas` 进行数据筛选和统计分析
3. **文件操作**：将数据保存为Excel文件
4. **异常处理**：使用try-except进行错误处理
5. **日期处理**：使用datetime处理日期格式

