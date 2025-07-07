import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
import ast

# 1. 读取清洗后数据
df = pd.read_csv('bangumi_anime_2015_2024_cleaned.csv', encoding='utf-8-sig')

# 2. 标签多热编码（确保tags_list为列表类型）
def safe_eval(val):
    if isinstance(val, list):
        return val
    try:
        return ast.literal_eval(val)
    except Exception:
        return []

df['tags_list'] = df['tags_list'].apply(safe_eval)
mlb = MultiLabelBinarizer()
tags_encoded = mlb.fit_transform(df['tags_list'])
tags_df = pd.DataFrame(tags_encoded, columns=mlb.classes_)
df = pd.concat([df, tags_df], axis=1)

# 3. 评分离散化（高分/中分/低分）
def score_level(score):
    if score >= 7.5:
        return '高分'
    elif score >= 6:
        return '中分'
    else:
        return '低分'

df['score_level'] = df['score'].apply(score_level)

# 4. 年份归一化
year_scaler = MinMaxScaler()
df['year_norm'] = year_scaler.fit_transform(df[['year']])

# 5. 保存特征工程后数据
df.to_csv('bangumi_anime_2015_2024_features.csv', index=False, encoding='utf-8-sig')
print('特征工程后的数据已保存为 bangumi_anime_2015_2024_features.csv')

# 6. 检查特征
print(df.head())
print([col for col in df.columns if col in ['百合', '热血', '奇幻', '科幻', '恋爱', '战斗']])
print(df[['百合', '热血', '奇幻', '科幻', '恋爱', '战斗']].sum()) 