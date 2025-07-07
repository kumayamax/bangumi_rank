import pandas as pd
import re

# 1. 读取修复后的标准csv
raw_file = 'bangumi_anime_2015_2024.csv'
col_names = ['name', 'name_cn', 'info', 'score', 'score_count', 'rank', 'type', 'tags']
df = pd.read_csv(raw_file, encoding='utf-8-sig', names=col_names, header=0)
print('实际列名:', df.columns)
print(df.head())

# 2. 提取年份
def extract_year(info):
    match = re.search(r'(20\d{2})', str(info))
    return int(match.group(1)) if match else None

df['year'] = df['info'].apply(extract_year)

# 调试：打印无法提取年份的info内容
print('无法提取年份的info样例:')
print(df[df['year'].isna()]['info'].head(20))

# 3. 强制转换score为数值型，无法转换的设为NaN
score_numeric = pd.to_numeric(df['score'], errors='coerce')
mask = score_numeric.isna() & df['score'].notna()
print('无法转换为数字的score内容:')
print(df.loc[mask, 'score'].unique())
df['score'] = score_numeric

# 4. 去除无年份或无评分的行
df = df.dropna(subset=['year', 'score'])

# 5. 填充空标签
df['tags'] = df['tags'].fillna('')

# 6. 标签拆分
df['tags_list'] = df['tags'].apply(lambda x: x.split(',') if x else [])

# 7. 类型one-hot编码
df['type'] = df['type'].fillna('unknown')
type_dummies = pd.get_dummies(df['type'], prefix='type')
df = pd.concat([df, type_dummies], axis=1)

# 8. 保存清洗后数据
cleaned_file = 'bangumi_anime_2015_2024_cleaned.csv'
df.to_csv(cleaned_file, index=False, encoding='utf-8-sig')
print(f'预处理后的数据已保存为 {cleaned_file}')

# 9. 检查结果
print(df.head())
print(df.info())
print(df['year'].value_counts().sort_index()) 