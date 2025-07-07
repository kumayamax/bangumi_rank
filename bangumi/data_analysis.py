import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 设置matplotlib支持中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'STSong', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 读取特征工程后的数据
features_file = 'bangumi_anime_2015_2024_features.csv'
df = pd.read_csv(features_file, encoding='utf-8-sig')

# 1. 类型流行度随年份变化
plt.figure(figsize=(14,7))
type_year_count = df.groupby(['year', 'type'])['name'].count().unstack(fill_value=0)
type_year_count.plot(kind='line', marker='o', ax=plt.gca())
plt.title('2015-2024各类型番剧数量变化')
plt.ylabel('数量')
plt.xlabel('年份')
plt.grid(True)
plt.tight_layout()
plt.savefig('type_year_trend.png')
plt.show()

# 2. 标签流行趋势
hot_tags = ['百合', '热血', '奇幻', '科幻', '恋爱', '战斗']
for tag in hot_tags:
    if tag not in df.columns:
        df[tag] = 0
plt.figure(figsize=(14,7))
tag_year_count = df.groupby('year')[hot_tags].sum()
tag_year_count.plot(kind='line', marker='o', ax=plt.gca())
plt.title('热门标签随年份数量变化')
plt.ylabel('数量')
plt.xlabel('年份')
plt.grid(True)
plt.tight_layout()
plt.savefig('tag_year_trend.png')
plt.show()

# 3. 评分分布
plt.figure(figsize=(10,6))
sns.histplot(df['score'], bins=30, kde=True)
plt.title('番剧评分分布')
plt.xlabel('评分')
plt.ylabel('数量')
plt.tight_layout()
plt.savefig('score_distribution.png')
plt.show()

print('数据分析与可视化已完成，图表已保存。') 