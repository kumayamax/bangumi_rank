import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import re

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="Bangumi 动漫数据分析", layout="wide")

def load_data():
    df = pd.read_csv('bangumi_anime_2015_2024_cleaned.csv', encoding='utf-8-sig')
    return df

def clean_tag(tag):
    return tag.strip().lower()

def clean_tags_field(tags):
    return ','.join(sorted(set([clean_tag(t) for t in str(tags).split(',') if t.strip()])))

df = load_data()
df['tags'] = df['tags'].fillna('').apply(clean_tags_field)
df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
years = sorted([int(y) for y in df['year'].dropna().unique()])
min_year, max_year = min(years), max(years)
year_range = st.sidebar.slider(
    "选择年份区间",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

topic_tags = [
    "奇幻", "搞笑", "战斗", "日常", "治愈", "恋爱", "校园", "热血", "科幻",
    "百合", "冒险", "后宫", "萌", "青春", "穿越", "音乐", "悬疑", "童年", "偶像",
    "玄幻", "剧情", "机战", "龙傲天", "卖肉", "萝卜", "运动", "萝莉", "女性向",
    "竞技", "动作", "猎奇", "历史", "魔法", "纯爱", "乙女向", "战争", "肉", "励志",
    "魔法少女", "超能力", "催泪", "武侠", "吐槽", "肉番", "耽美", "萌系"
]
present_topic_tags = [t for t in topic_tags if any(df['tags'].str.contains(t))]
tag_options = ['全部'] + present_topic_tags
tag_name = st.sidebar.selectbox("选择题材/风格标签", tag_options)

df_show = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
if tag_name != '全部':
    df_show = df_show[df_show['tags'].str.contains(tag_name, case=False, na=False, regex=True)]

if 'type' in df.columns:
    df = df[df['type'].astype(str).str.lower() != 'unknown']

st.write(f'当前年份区间: {year_range}')
st.write(f'筛选后数据年份分布:')
st.write(df_show['year'].value_counts().sort_index())

st.write(f"### {year_range[0]}-{year_range[1]}年{' - ' + tag_name if tag_name != '全部' else ''} 动漫数据")
show_df = df_show.copy()
col_rename = {}
if 'name' in show_df.columns:
    col_rename['name'] = '中文名'
if 'name_cn' in show_df.columns:
    col_rename['name_cn'] = '日文名'
if 'info' in show_df.columns:
    col_rename['info'] = '集数/首播时间/主创人员'
if 'score' in show_df.columns:
    col_rename['score'] = '评分'
if 'score_count' in show_df.columns:
    col_rename['score_count'] = '评分人数'
if 'rank' in show_df.columns:
    col_rename['rank'] = '排行'
if 'year' in show_df.columns:
    col_rename['year'] = '年份'
if 'tags_list' in show_df.columns:
    col_rename['tags_list'] = '标签'

show_df = show_df.rename(columns=col_rename)

def extract_number(s):
    if pd.isna(s):
        return None
    m = re.search(r'\d+', str(s))
    return int(m.group()) if m else None

for col in ['排行', '评分人数']:
    if col in show_df.columns:
        show_df[col + '_原始'] = show_df[col]
        show_df[col] = show_df[col].apply(extract_number)
        if show_df[col].isna().all():
            show_df[col] = show_df[col + '_原始']
        show_df = show_df.drop(columns=[col + '_原始'])

if '排行' in show_df.columns:
    show_df = show_df[show_df['排行'].notna()]

for col in ['type', 'type_unknown', 'tags']:
    if col in show_df.columns:
        show_df = show_df.drop(columns=[col])
st.dataframe(show_df)

st.write("#### 评分分布")
fig, ax = plt.subplots()
sns.histplot(df_show['score'], bins=20, kde=True, ax=ax)
ax.set_xlabel('评分')
ax.set_ylabel('数量')
st.pyplot(fig)

st.write("#### 历年标签平均评分趋势")
if tag_name == '全部':
    valid_top_tags = []
    for t in present_topic_tags:
        mask = show_df['标签'].str.contains(t)
        year_counts = show_df[mask].groupby('年份').size()
        if (year_counts >= 10).sum() >= 10:
            valid_top_tags.append(t)
    top_tags = valid_top_tags[:10]

    fig2, ax2 = plt.subplots(figsize=(12, 6))
    for t in top_tags:
        mask = show_df['标签'].str.contains(t)
        trend = show_df[mask].groupby('年份')['评分'].mean()
        if not trend.empty:
            trend = trend.reindex(range(show_df['年份'].min(), show_df['年份'].max() + 1))
            ax2.plot(trend.index, trend.values, marker='o', label=t, linewidth=2)
    ax2.set_title("高频题材/风格标签历年平均评分趋势")
    ax2.set_xlabel('年份')
    ax2.set_ylabel('平均评分')
    ax2.legend(loc='best')
    st.pyplot(fig2)
else:
    trend = show_df[show_df['标签'].str.contains(tag_name)].groupby('年份')['评分'].mean()
    fig2, ax2 = plt.subplots()
    trend.plot(marker='o', ax=ax2)
    ax2.set_title(f"{tag_name} 历年平均评分趋势")
    ax2.set_xlabel('年份')
    ax2.set_ylabel('平均评分')
    st.pyplot(fig2)

# 6. 可扩展：国产/日本对比等分析
# st.write("#### 更多分析功能，欢迎补充！") 