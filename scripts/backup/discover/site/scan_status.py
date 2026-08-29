#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from deep_enhance_full import load_all_articles, assess_article_quality
from collections import Counter

all_articles, category_articles = load_all_articles()
print('技术类文章总数:', len(all_articles))
print()

for cat in ['AI与机器学习', '系统与运维', '编程与开发', '数据库与存储', '云计算', '知识管理']:
    files = category_articles.get(cat, [])
    cat_stats = {'total': len(files), 'has_bg': 0, 'has_deep': 0, 'has_latest': 0, 'has_resources': 0, 'S': 0, 'A': 0, 'B': 0, 'C': 0}
    for f in files:
        info = all_articles[f]
        content = info['content']
        quality = assess_article_quality(info)
        cat_stats[quality] = cat_stats.get(quality, 0) + 1
        if '背景与上下文' in content:
            cat_stats['has_bg'] += 1
        if '深度解读' in content:
            cat_stats['has_deep'] += 1
        if '最新进展' in content:
            cat_stats['has_latest'] += 1
        if '相关技术资源' in content or '相关资源' in content:
            cat_stats['has_resources'] += 1
    print('=== ' + cat + ' (' + str(len(files)) + '篇) ===')
    print('  质量等级: S=' + str(cat_stats['S']) + ', A=' + str(cat_stats['A']) + ', B=' + str(cat_stats['B']) + ', C=' + str(cat_stats['C']))
    print('  背景与上下文: ' + str(cat_stats['has_bg']) + '/' + str(len(files)))
    print('  深度解读: ' + str(cat_stats['has_deep']) + '/' + str(len(files)))
    print('  最新进展: ' + str(cat_stats['has_latest']) + '/' + str(len(files)))
    print('  相关资源: ' + str(cat_stats['has_resources']) + '/' + str(len(files)))
    print()
