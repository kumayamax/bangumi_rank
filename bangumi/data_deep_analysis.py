import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

plt.rcParams['font.sans-serif'] = ['SimHei', 'STSong', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 读取特征工程后的数据
features_file = 'bangumi_anime_2015_2024_features.csv'
df = pd.read_csv(features_file, encoding='utf-8-sig')

# 热门标签
hot_tags = ['百合', '热血', '奇幻', '科幻', '恋爱', '战斗']
for tag in hot_tags:
    if tag not in df.columns:
        df[tag] = 0

# 1. 各类型每年平均评分
plt.figure(figsize=(14,7))
type_year_score = df.groupby(['year', 'type'])['score'].mean().unstack(fill_value=0)
type_year_score.plot(kind='line', marker='o', ax=plt.gca())
plt.title('2015-2024各类型番剧平均评分变化')
plt.ylabel('平均评分')
plt.xlabel('年份')
plt.grid(True)
plt.tight_layout()
plt.savefig('type_year_score_trend.png')
plt.show()

# 2. 各标签每年平均评分
plt.figure(figsize=(14,7))
for tag in hot_tags:
    df_tag = df[df[tag] == 1]
    tag_score = df_tag.groupby('year')['score'].mean()
    plt.plot(tag_score.index, tag_score.values, marker='o', label=tag)
plt.title('热门标签番剧平均评分随年份变化')
plt.xlabel('年份')
plt.ylabel('平均评分')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('tag_year_score_trend.png')
plt.show()

# 3. 用户偏好聚类（KMeans）
X = df[hot_tags].values
kmeans = KMeans(n_clusters=4, random_state=42)
df['cluster'] = kmeans.fit_predict(X)
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X)
plt.figure(figsize=(10,7))
sns.scatterplot(x=X_pca[:,0], y=X_pca[:,1], hue=df['cluster'], palette='Set2', alpha=0.6)
plt.title('用户偏好聚类（热门标签）')
plt.xlabel('PCA1')
plt.ylabel('PCA2')
plt.tight_layout()
plt.savefig('user_preference_cluster.png')
plt.show()

# 4. 各聚类的标签偏好
for i in range(4):
    print(f'聚类{i}高频标签：')
    print(df[df['cluster']==i][hot_tags].sum().sort_values(ascending=False))
    print('-'*30)

# 5. 高分番剧的类型/标签分布
high_score_df = df[df['score'] >= 8]
type_count = high_score_df['type'].value_counts()
tag_count = high_score_df[hot_tags].sum().sort_values(ascending=False)
print('高分番剧类型分布：')
print(type_count)
print('高分番剧热门标签分布：')
print(tag_count)

# 6. 高分番剧随年份变化
high_score_year = high_score_df.groupby('year').size()
plt.figure(figsize=(10,6))
high_score_year.plot(kind='bar')
plt.title('每年高分番剧数量')
plt.xlabel('年份')
plt.ylabel('数量')
plt.tight_layout()
plt.savefig('high_score_year.png')
plt.show()

# 7. 评分与标签/类型的相关性分析
corr = df[hot_tags + ['score']].corr()['score'].sort_values(ascending=False)
print('各标签与评分的相关性：')
print(corr)

# 8. 国产番剧与日本番剧差异分析
china_df = df[df['tags'].apply(lambda x: '国产' in str(x))]
japan_df = df[df['tags'].apply(lambda x: '日本' in str(x))]
print(f'国产番剧数量: {len(china_df)}, 日本番剧数量: {len(japan_df)}')
plt.figure(figsize=(10,6))
sns.kdeplot(china_df['score'], label='国产', fill=True)
sns.kdeplot(japan_df['score'], label='日本', fill=True)
plt.title('国产番剧与日本番剧评分分布对比')
plt.xlabel('评分')
plt.ylabel('密度')
plt.legend()
plt.tight_layout()
plt.savefig('china_japan_score_dist.png')
plt.show()
print('国产番剧热门标签：')
print(china_df[hot_tags].sum().sort_values(ascending=False))
print('日本番剧热门标签：')
print(japan_df[hot_tags].sum().sort_values(ascending=False))

# 9. 低分番剧共性分析
low_score_df = df[df['score'] <= 6]
print('低分番剧数量:', len(low_score_df))
print('低分番剧热门标签：')
print(low_score_df[hot_tags].sum().sort_values(ascending=False))
print('低分番剧类型分布：')
print(low_score_df['type'].value_counts())

# 10. 机器学习模型预测高分番剧特征
df['is_high_score'] = (df['score'] >= 8).astype(int)
features = hot_tags + ['year_norm']
X = df[features]
y = df['is_high_score']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)
print('高分番剧预测准确率:', clf.score(X_test, y_test))
importances = pd.Series(clf.feature_importances_, index=features).sort_values(ascending=False)
print('特征重要性：')
print(importances)
importances.plot(kind='bar')
plt.title('预测高分番剧的特征重要性')
plt.tight_layout()
plt.savefig('high_score_feature_importance.png')
plt.show()

print('深入数据分析与可视化已完成，图表已保存。') 