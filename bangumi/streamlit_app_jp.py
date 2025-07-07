import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
import re
import matplotlib.font_manager as fm
import os

font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'NotoSansJP-Regular.ttf')
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    matplotlib.rcParams['font.sans-serif'] = ['Noto Sans JP']
else:
    matplotlib.rcParams['font.sans-serif'] = [
        'IPAexGothic', 'Noto Sans CJK JP', 'Yu Gothic', 'MS Gothic', 'SimHei', 'Arial Unicode MS', 'Microsoft YaHei'
    ]
matplotlib.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="Bangumi アニメデータ分析", layout="wide")

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
    "年区間を選択",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

topic_tags = [
    "ファンタジー", "コメディ", "バトル", "日常", "癒し", "恋愛", "学園", "熱血", "SF",
    "百合", "冒険", "ハーレム", "萌え", "青春", "異世界", "音楽", "サスペンス", "子供向け", "アイドル",
    "玄幻", "ドラマ", "メカ", "俺TUEEE", "エロ", "ロボ", "スポーツ", "ロリ", "女性向け",
    "競技", "アクション", "グロ", "歴史", "魔法", "純愛", "乙女向け", "戦争", "肉", "励まし",
    "魔法少女", "超能力", "感動", "武侠", "ツッコミ", "エロアニメ", "BL", "萌系"
]
present_topic_tags = [t for t in topic_tags if any(df['tags'].str.contains(t))]
tag_options = ['全部'] + present_topic_tags
tag_name = st.sidebar.selectbox("ジャンル・テーマを選択", tag_options)

# 中日标签对照表
jp2cn_tag_map = {
    "ファンタジー": "奇幻",
    "コメディ": "搞笑",
    "バトル": "战斗",
    "日常": "日常",
    "癒し": "治愈",
    "恋愛": "恋爱",
    "学園": "校园",
    "熱血": "热血",
    "SF": "科幻",
    "百合": "百合",
    "冒険": "冒险",
    "ハーレム": "后宫",
    "萌え": "萌",
    "青春": "青春",
    "異世界": "穿越",
    "音楽": "音乐",
    "サスペンス": "悬疑",
    "子供向け": "童年",
    "アイドル": "偶像",
    "玄幻": "玄幻",
    "ドラマ": "剧情",
    "メカ": "机战",
    "俺TUEEE": "龙傲天",
    "エロ": "卖肉",
    "ロボ": "萝卜",
    "スポーツ": "运动",
    "ロリ": "萝莉",
    "女性向け": "女性向",
    "競技": "竞技",
    "アクション": "动作",
    "グロ": "猎奇",
    "歴史": "历史",
    "魔法": "魔法",
    "純愛": "纯爱",
    "乙女向け": "乙女向",
    "戦争": "战争",
    "肉": "肉",
    "励まし": "励志",
    "魔法少女": "魔法少女",
    "超能力": "超能力",
    "感動": "催泪",
    "武侠": "武侠",
    "ツッコミ": "吐槽",
    "エロアニメ": "肉番",
    "BL": "耽美",
    "萌系": "萌系"
}

df_show = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
if tag_name != '全部':
    # 用中日对照表查找对应中文标签
    cn_tag = jp2cn_tag_map.get(tag_name, None)
    if cn_tag:
        df_show = df_show[df_show['tags'].str.contains(cn_tag, case=False, na=False, regex=True)]
    else:
        df_show = df_show[df_show['tags'].str.contains(tag_name, case=False, na=False, regex=True)]

if 'type' in df.columns:
    df = df[df['type'].astype(str).str.lower() != 'unknown']

st.write(f'現在の年区間: {year_range}')
st.write(f'フィルタ後のデータ年分布:')
st.write(df_show['year'].value_counts().sort_index())

st.write(f"### {year_range[0]}年～{year_range[1]}年{' - ' + tag_name if tag_name != '全部' else ''} アニメデータ")
show_df = df_show.copy()
col_rename = {}
if 'name_cn' in show_df.columns:
    col_rename['name_cn'] = 'アニメタイトル'
if 'name' in show_df.columns:
    col_rename['name'] = '中国語タイトル'
if 'info' in show_df.columns:
    col_rename['info'] = '話数/放送日/スタッフ'
if 'score' in show_df.columns:
    col_rename['score'] = '評価'
if 'score_count' in show_df.columns:
    col_rename['score_count'] = '評価人数'
if 'rank' in show_df.columns:
    col_rename['rank'] = 'ランキング'
if 'year' in show_df.columns:
    col_rename['year'] = '年'
if 'tags_list' in show_df.columns:
    col_rename['tags_list'] = 'タグ'

show_df = show_df.rename(columns=col_rename)

def extract_number(s):
    if pd.isna(s):
        return None
    m = re.search(r'\d+', str(s))
    return int(m.group()) if m else None

for col in ['ランキング', '評価人数']:
    if col in show_df.columns:
        show_df[col + '_原始'] = show_df[col]
        show_df[col] = show_df[col].apply(extract_number)
        if show_df[col].isna().all():
            show_df[col] = show_df[col + '_原始']
        show_df = show_df.drop(columns=[col + '_原始'])

if 'ランキング' in show_df.columns:
    show_df = show_df[show_df['ランキング'].notna()]

for col in ['type', 'type_unknown', 'tags']:
    if col in show_df.columns:
        show_df = show_df.drop(columns=[col])
# st.dataframe(show_df)
st.dataframe(show_df)

st.write("#### 評価分布")
fig, ax = plt.subplots()
sns.histplot(show_df['評価'], bins=20, kde=True, ax=ax)
ax.set_xlabel('評価')
ax.set_ylabel('件数')
st.pyplot(fig)

st.write("#### 年別平均評価推移（フィルタ結果のみ）")
if show_df.shape[0] > 0:
    # 只基于当前筛选结果的"評価"数据生成趋势图
    if '年' in show_df.columns and '評価' in show_df.columns:
        trend = show_df.groupby('年')['評価'].mean()
        fig3, ax3 = plt.subplots()
        trend.plot(marker='o', ax=ax3, label='平均評価')
        ax3.set_title('年別平均評価推移（フィルタ結果のみ）')
        ax3.set_xlabel('年')
        ax3.set_ylabel('平均評価')
        ax3.legend(loc='best')
        st.pyplot(fig3)

st.write("#### 高頻度ジャンル・テーマの年別平均評価推移")
if tag_name == '全部':
    valid_top_tags = []
    if 'タグ' in show_df.columns:
        for t in present_topic_tags:
            mask = show_df['タグ'].str.contains(t)
            year_counts = show_df[mask].groupby('年').size()
            if (year_counts >= 10).sum() >= 10:
                valid_top_tags.append(t)
        top_tags = valid_top_tags[:10]

        fig2, ax2 = plt.subplots(figsize=(12, 6))
        for t in top_tags:
            mask = show_df['タグ'].str.contains(t)
            trend = show_df[mask].groupby('年')['評価'].mean()
            if not trend.empty:
                trend = trend.reindex(range(show_df['年'].min(), show_df['年'].max() + 1))
                ax2.plot(trend.index, trend.values, marker='o', label=t, linewidth=2)
        ax2.set_title("高頻度ジャンル・テーマの年別平均評価推移")
        ax2.set_xlabel('年')
        ax2.set_ylabel('平均評価')
        ax2.legend(loc='best', title="ジャンル")
        st.pyplot(fig2)

# 6. 拡張可能：中日比較など
# st.write("#### さらに多くの分析機能を追加できます！") 