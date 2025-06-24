# 数据处理规则

## 数据处理和分析规范

### 数据清洗
```python
import pandas as pd
import numpy as np

# 处理缺失值
df.fillna(method='forward')  # 前向填充
df.dropna(subset=['key_column'])  # 删除关键字段为空的行

# 数据类型转换
df['date'] = pd.to_datetime(df['date'])
df['price'] = pd.to_numeric(df['price'], errors='coerce')
```

### 数据验证
- 字段类型检查
- 数值范围验证
- 重复数据检测
- 数据一致性校验

### 文件处理
- 支持多种格式: CSV, Excel, JSON
- 大文件分块读取
- 编码格式处理(UTF-8, GBK)
- 文件路径标准化

### 数据存储
```python
# 高效存储格式
df.to_parquet('data.parquet')  # 推荐格式
df.to_pickle('data.pkl')       # Python专用

# 数据库存储
df.to_sql('table_name', engine, if_exists='append')
```

### 性能优化
- 使用pandas的向量化操作
- 避免循环处理大数据
- 合理使用内存
- 并行处理

### 数据分析
- 使用scikit-learn进行机器学习
- 统计分析和可视化
- 数据报告生成
- 趋势分析

### 监控和日志
- 处理进度监控
- 异常数据记录
- 性能指标统计
- 定期数据质量检查 