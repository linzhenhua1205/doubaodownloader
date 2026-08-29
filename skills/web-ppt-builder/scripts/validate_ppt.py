#!/usr/bin/env python3
"""web-ppt-builder 质量校验脚本
检查: HTML 标签闭合 / section.slide 数量 / 每页标题+来源 / 红绿语义 / 结论页四维影响 / 配图官方源
用法: python3 validate_ppt.py <index.html> [--strict]
"""
import re, sys
from html.parser import HTMLParser

class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__(); self.stack = []; self.errors = []
        self.void = {'meta','img','br','hr','link','input','source','wbr','area','base','col','embed','track'}
    def handle_starttag(self, tag, attrs):
        if tag not in self.void: self.stack.append(tag)
    def handle_endtag(self, tag):
        if tag in self.void: return
        if self.stack and self.stack[-1] == tag: self.stack.pop()
        else: self.errors.append(f'line {self.getpos()[0]}: mismatched </{tag}>')

def main():
    path = sys.argv[1]
    strict = '--strict' in sys.argv
    html = open(path, encoding='utf-8').read()
    issues = []; passes = []

    # 1. 标签闭合
    c = TagChecker(); c.feed(html)
    if c.errors or c.stack:
        issues.append(f'HTML 标签错误: {c.errors[:3]}{c.stack[:3]}')
    else:
        passes.append('HTML 标签闭合 ✅')

    # 2. section.slide 数量
    slides = re.findall(r'<section class="slide[^"]*"', html)
    n = len(slides)
    if n < 5: issues.append(f'section 过少 ({n} 页，至少 5 页)')
    else: passes.append(f'{n} 页 slide ✅')

    # 3. 每页是否有标题与来源脚注
    sections = re.split(r'<section class="slide', html)[1:]
    for i, sec in enumerate(sections, 1):
        tag_open = sec.split('>')[0]
        is_cover = 'cover' in tag_open
        is_part = 'part' in tag_open
        has_title = ('<h1' in sec or '<h2' in sec or 'class="big"' in sec
                     or 'class="title"' in sec or 'cover' in tag_open)
        if not has_title:
            issues.append(f'第 {i} 页缺标题（行动式标题铁律②）')
        if 'class="src"' not in sec and not is_part:
            issues.append(f'第 {i} 页缺来源脚注（铁律⑥）')

    # 4. 红绿语义
    reds = len(re.findall(r'class="red"', html))
    greens = len(re.findall(r'class="green"', html))
    if reds == 0 and greens == 0:
        issues.append('全篇无红/绿关键色（铁律③未使用）')
    else:
        passes.append(f'红 {reds} 处 / 绿 {greens} 处 ✅')

    # 5. 结论页四维影响（总结+技术+产品+业务经营）
    if '.impact' in html:
        dims = len(re.findall(r'class="dim', html))
        impact_block = html[html.find('.impact'):]
        for kw in ['总结', '技术', '产品', '业务']:
            if kw not in impact_block:
                issues.append(f'结论页缺维度: {kw}')
        if dims < 4:
            issues.append(f'结论页维度 <4（实际 {dims}）')
        else:
            passes.append(f'结论页四维影响 ✅（{dims} 维）')

    # 6. 配图官方源
    imgs = re.findall(r'<img[^>]*src="([^"]+)"', html)
    if imgs:
        for u in imgs:
            if not re.match(r'https?://', u):
                issues.append(f'配图非 web 直链: {u}')
            if 'onerror' not in html[html.find(u)-200:html.find(u)+50] and u != 'about:blank':
                pass  # onerror 检查放宽（可能在 img 标签后）
        if any('onerror' not in m for m in re.findall(r'<img[^>]*>', html)):
            issues.append('有 img 缺 onerror 兜底（建议加 onerror="this.style.display=\'none\'"）')
        passes.append(f'配图 {len(imgs)} 张（建议逐张 curl 验证 200）✅')
    else:
        passes.append('无配图（建议增加官方图提升可信度，铁律⑦）')

    # 7. 来源链接（URL 存在性）
    urls = re.findall(r'https?://[^\s"<>\)]+', html)
    if urls: passes.append(f'来源链接 {len(urls)} 个（建议抽查 curl 200）✅')

    print('='*50)
    print(f'校验: {path}')
    for p in passes: print(f'  ✓ {p}')
    if issues:
        print('  ✗ 问题:')
        for it in issues: print(f'    - {it}')
        sys.exit(1 if strict else 0)
    else:
        print('  ✅ 全部通过')
    return 0

if __name__ == '__main__':
    main()
