import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import unicodedata

BASE_URL = "https://bangumi.tv/anime/browser/airtime/{year}?sort=title&page={page}"
HEADERS = {
    "User-Agent": "zemi/bangumi-research/0.1 (https://github.com/zemi/bangumi-research)"
}

# 清理不可见字符
def clean_text(text):
    return ''.join(c for c in text if unicodedata.category(c)[0] != 'C')

# 详情页标签抓取
def fetch_tags(subject_url):
    try:
        resp = requests.get(subject_url, headers=HEADERS, timeout=10)
        try:
            resp.encoding = 'utf-8'
            html = resp.text
        except Exception:
            resp.encoding = resp.apparent_encoding
            html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        tag_spans = soup.select('div.subject_tag_section div.inner a.l span')
        tags = [span.text.strip() for span in tag_spans]
        tags_str = ','.join(tags)
        return clean_text(tags_str)
    except Exception as e:
        print(f"标签抓取失败: {subject_url}, {e}")
        return ''

# 主列表页抓取
def fetch_anime_list(year, max_pages=100, max_workers=20):
    results = []
    for page in range(1, max_pages+1):
        url = BASE_URL.format(year=year, page=page)
        resp = requests.get(url, headers=HEADERS)
        resp.encoding = resp.apparent_encoding
        if year == 2015 and page == 1:
            with open('test.html', 'w', encoding='utf-8') as f:
                f.write(resp.text)
            print("已保存 test.html，请用浏览器打开检查内容。")
        if resp.status_code != 200:
            print(f"Error: {resp.status_code} at {url}")
            break
        soup = BeautifulSoup(resp.text, 'html.parser')
        items = soup.select('ul#browserItemList > li.item')
        if not items:
            break
        anime_data = []
        for item in items:
            name = item.select_one('div.inner h3 a.l')
            name_cn = item.select_one('div.inner h3 small.grey')
            info = item.select_one('div.inner p.info.tip')
            score = item.select_one('div.inner p.rateInfo small.fade')
            score_count = item.select_one('div.inner p.rateInfo span.tip_j')
            rank = item.select_one('div.inner span.rank')
            type_name = ''
            class_list = item.get('class', [])
            for c in class_list:
                if c in ['tv', 'movie', 'ova', 'web', 'anime_comic', 'misc']:
                    type_name = c
                    break
            subject_url = 'https://bangumi.tv' + name['href'] if name and name.has_attr('href') else ''
            anime_data.append({
                'name': name.text.strip() if name else '',
                'name_cn': name_cn.text.strip() if name_cn else '',
                'info': info.text.strip() if info else '',
                'score': score.text.strip() if score else '',
                'score_count': score_count.text.strip() if score_count else '',
                'rank': rank.text.strip() if rank else '',
                'type': type_name,
                'subject_url': subject_url
            })
        # 多线程抓取详情页标签
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {executor.submit(fetch_tags, anime['subject_url']): idx for idx, anime in enumerate(anime_data) if anime['subject_url']}
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    tags = future.result()
                except Exception as exc:
                    tags = ''
                anime_data[idx]['tags'] = tags
        for anime in anime_data:
            if 'tags' not in anime:
                anime['tags'] = ''
            del anime['subject_url']
        results.extend(anime_data)
        print(f"{year} 第{page}页, 累计: {len(results)}")
        time.sleep(0.5)
    return results

all_data = []
for year in range(2015, 2025):
    print(f"抓取 {year} 年...")
    year_data = fetch_anime_list(year, max_workers=20)
    all_data.extend(year_data)
    print(f"{year}年完成, 累计: {len(all_data)}")

# 保证字段顺序和表头一致
columns = ['name', 'name_cn', 'info', 'score', 'score_count', 'rank', 'type', 'tags']
df = pd.DataFrame(all_data, columns=columns)
df.to_csv("bangumi_anime_2015_2024.csv", index=False, encoding="utf-8-sig")
print("数据已保存到 bangumi_anime_2015_2024.csv")

# 检查tags中包含疑似乱码的行（包含或不可见字符）
def is_garbled(s):
    return '' in s or any(ord(c) < 32 and c not in '\t\n\r' for c in s)

garbled_rows = df[df['tags'].apply(is_garbled)]
if not garbled_rows.empty:
    print("疑似乱码的tags行：")
    print(garbled_rows[['name', 'tags']]) 