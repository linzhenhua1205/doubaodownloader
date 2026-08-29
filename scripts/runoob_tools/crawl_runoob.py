#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runoob.com 爬虫脚本 - 获取所有专题和文章链接
生成结构化HTML文件
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from pathlib import Path


def fetch_page(url, headers=None, timeout=10):
    """获取页面内容"""
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"请求失败 {url}: {e}")
        return None


def extract_articles(soup, category_name):
    """从页面提取所有文章链接"""
    articles = []
    soup_de_links = soup.find_all('a')

    # Runoob 文章链接特征
    for link in soup_de_links:
        href = link.get('href')
        title = link.get_text(strip=True)

        # 过滤条件：包含文章链接特征
        if href and title and len(title) > 1 and len(title) < 100:
            # 支持相对路径和绝对路径
            if href.startswith('/'):
                full_url = 'https://www.runoob.com' + href
            elif href.startswith('//'):
                full_url = 'https:' + href
            elif not href.startswith('http'):
                continue
            else:
                full_url = href

            # 排除导航链接、JS链接等
            if any(x in full_url.lower() for x in ['javascript:', '#', 'mailto:', '?']):
                continue

            # 追加文章链接
            if 'runoob.com/tutorial/' in full_url or '/tutorial/' in full_url:
                articles.append({
                    'title': title,
                    'url': full_url,
                    'category': category_name
                })

    return articles


def crawl_runoob():
    """主爬取函数"""
    base_url = 'https://www.runoob.com/'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    print("=" * 50)
    print("开始爬取 Runoob.com")
    print("=" * 50)

    result = {
        'categories': [],
        'total_articles': 0,
        'crawled_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    # Step 1: 获取首页，提取专题导航
    print(f"\n[1/3] 正在获取首页: {base_url}")
    html = fetch_page(base_url, headers)

    if not html:
        print("错误：无法获取首页内容")
        return None

    soup = BeautifulSoup(html, 'html.parser')

    # 查找专题导航链接
    nav_links = []
    selectors = [
        ('nav ul li a', 'default'),
        ('div.w3-hover-gray a', 'card style'),
        ('ul.menu.col-3 li a', 'column style'),
        ('a[href*="runoob.com/w3ccheck"]', 'footer'),
        ('a[href*="tree"]', 'tree'),
    ]

    for selector, desc in selectors:
        elements = soup.select(selector)
        for elem in elements:
            href = elem.get('href')
            text = elem.get_text(strip=True)
            if text and href and 'runoob.com' in href:
                nav_links.append({
                    'name': text,
                    'url': href if href.startswith('http') else base_url + href,
                    'selector': desc
                })

    print(f"   发现 {len(nav_links)} 个专题链接")

    # Step 2: 遍历每个专题页面
    print(f"\n[2/3] 正在爬取专题内容...")

    for idx, link in enumerate(nav_links, 1):
        category_name = link['name']
        category_url = link['url']

        print(f"   [{idx}/{len(nav_links)}] 爬取专题: {category_name}")
        print(f"      URL: {category_url}")

        html = fetch_page(category_url, headers)

        if html:
            soup = BeautifulSoup(html, 'html.parser')
            articles = extract_articles(soup, category_name)

            if articles:
                category_data = {
                    'name': category_name,
                    'url': category_url,
                    'articles': articles
                }
                result['categories'].append(category_data)
                result['total_articles'] += len(articles)
                print(f"      ✓ 提取 {len(articles)} 篇文章")
            else:
                print(f"      ! 未提取到文章，尝试显示页面内容...")
                # 尝试提取页面主要内容
                content = soup.get_text(strip=True)[:500]
                print(f"      页面内容预览: {content[:200]}...")
        else:
            print(f"      ✗ 请求失败")

        # 避免请求过快被IP限制
        time.sleep(1)

    # Step 3: 生成 HTML 文件
    print(f"\n[3/3] 正在生成 HTML 文件...")

    html_content = generate_html(result)
    output_path = Path('runoob-links.html')
    output_path.write_text(html_content, encoding='utf-8')

    print(f"\n{'=' * 50}")
    print(f"✓ 完成! 共爬取 {len(nav_links)} 个专题，{result['total_articles']} 篇文章")
    print(f"✓ 输出文件: {output_path.absolute()}")
    print(f"{'=' * 50}")

    return result


def generate_html(data):
    """生成HTML内容"""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Runoob.com 所有链接 - {data['crawled_time']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f5f5;
            line-height: 1.6;
            color: #333;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 1.1em; }}
        .stats {{
            background: white;
            padding: 20px;
            margin: 30px auto;
            max-width: 1200px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            justify-content: center;
            gap: 50px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        .category {{
            background: white;
            margin: 30px 0;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .category-header {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px 30px;
            font-size: 1.5em;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .article-count {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .article-list {{
            padding: 20px 30px;
        }}
        .article-item {{
            padding: 12px 15px;
            margin: 8px 0;
            border-radius: 6px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            height: 50px;
        }}
        .article-item:hover {{
            background: #e9ecef;
            transform: translateX(5px);
        }}
        .article-item a {{
            text-decoration: none;
            color: #333;
            font-size: 1em;
        }}
        .article-item a:hover {{
            color: #667eea;
        }}
        .article-url {{
            font-size: 0.85em;
            color: #999;
            flex: 1;
            margin-left: 20px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        .article-url a {{
            color: #667eea;
            margin-left: 10px;
        }}
        .refresh-btn {{
            display: inline-block;
            margin: 20px 0;
            padding: 15px 40px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-size: 1.1em;
        }}
        .refresh-btn:hover {{
            background: #5568d3;
        }}
        .footer {{
            text-align: center;
            padding: 40px;
            color: #999;
            font-size: 0.9em;
            margin-top: 50px;
            border-top: 1px solid #e5e5e5;
        }}
        .empty {{
            text-align: center;
            color: #999;
            padding: 40px;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📚 Runoob.com 所有链接</h1>
        <p>{data['crawled_time']}</p>
    </div>

    <a href="runoob-links.html" class="refresh-btn">🔄 刷新页面</a>

    <div class="stats">
        <div class="stat-item">
            <div class="stat-value">{len(data['categories'])}</div>
            <div class="stat-label">专题数量</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{data['total_articles']}</div>
            <div class="stat-label">文章总数</div>
        </div>
    </div>

    <div class="container">"""

    for category in data['categories']:
        html += f"""
        <div class="category">
            <div class="category-header">
                <span>{category['name']}</span>
                <span class="article-count">{len(category['articles'])} 篇</span>
            </div>
            <div class="article-list">"""

        for article in category['articles']:
            html += f"""
                <div class="article-item">
                    <a href="{article['url']}" target="_blank">{article['title']}</a>
                    <span class="article-url">
                        <a href="{article['url']}" target="_blank">🔗</a>
                        {article['url']}
                    </span>
                </div>"""

        html += """
            </div>
        </div>"""

    html += """
    </div>

    <div class="footer">
        <p>数据来源: https://www.runoob.com/</p>
        <p>爬取时间: {0}</p>
    </div>
</body>
</html>""".format(data['crawled_time'])

    return html


if __name__ == '__main__':
    try:
        result = crawl_runoob()

        # 同时保存JSON数据
        if result:
            json_path = Path('runoob-data.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'metadata': {
                        'crawled_time': result['crawled_time'],
                        'total_categories': len(result['categories']),
                        'total_articles': result['total_articles']
                    },
                    'categories': result['categories']
                }, f, ensure_ascii=False, indent=2)

            print(f"✓ JSON数据已保存: {json_path.absolute()}")

    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断")
    except Exception as e:
        print(f"\n\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
