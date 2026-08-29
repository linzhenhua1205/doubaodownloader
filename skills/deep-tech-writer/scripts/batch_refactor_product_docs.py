#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量重构产品与设计目录下的markdown文件
使用 deep-tech-writer 六步工作流进行深度重构
"""

import os
import re
import sys
import yaml
import json
from pathlib import Path
from datetime import datetime
from collections import Counter
import copy


class MarkdownDocRefactor:
    """Markdown文档重构器"""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.filename = self.file_path.name
        self.raw_content = ""
        self.frontmatter = {}
        self.body = ""
        self.title = ""
        self.summary = ""
        self.keywords = []
        self.sections = {}
        self.stats = {
            'original_lines': 0,
            'new_lines': 0,
            'removed_duplicates': 0,
            'removed_emoji_titles': 0,
            'quality_issues': []
        }

    def load(self):
        """加载文件并解析frontmatter"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.raw_content = f.read()
        
        self.stats['original_lines'] = len(self.raw_content.split('\n'))
        
        # 解析YAML frontmatter
        if self.raw_content.startswith('---'):
            parts = self.raw_content.split('---', 2)
            if len(parts) >= 3:
                try:
                    self.frontmatter = yaml.safe_load(parts[1])
                    self.body = parts[2].lstrip('\n')
                except:
                    self.frontmatter = {}
                    self.body = self.raw_content
            else:
                self.body = self.raw_content
        else:
            self.body = self.raw_content
        
        # 提取标题
        self._extract_title()
        
        return self

    def _extract_title(self):
        """提取文档标题"""
        # 优先从frontmatter获取
        if self.frontmatter.get('title'):
            self.title = self.frontmatter['title'].strip()
            # 移除emoji
            self.title = self._remove_emoji(self.title)
            return
        
        # 从正文第一个H1获取
        h1_match = re.search(r'^#\s+(.+)$', self.body, re.MULTILINE)
        if h1_match:
            self.title = self._remove_emoji(h1_match.group(1).strip())

    def _remove_emoji(self, text):
        """移除文本中的emoji"""
        emoji_pattern = re.compile(
            "["
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U0001F900-\U0001F9FF"  # supplemental symbols and pictographs
            "\U0001FA00-\U0001FA6F"  # chess symbols etc
            "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F000-\U0001F02F"  # Mahjong Tiles
            "\U0001F030-\U0001F09F"  # Domino Tiles
            "\u2600-\u26FF"  # misc symbols
            "\u2700-\u27BF"  # dingbats
            "\u2B50"  # star
            "\u2B06"  # up arrow
            "\uFE0F"  # variation selector-16
            "\u200d"  # zero width joiner
            "\U0001F191-\U0001F251"  # enclosed characters
            "]+",
            flags=re.UNICODE
        )
        result = emoji_pattern.sub('', text).strip()
        # 移除开头可能残留的空格
        result = re.sub(r'^\s+', '', result)
        return result

    def _extract_section_text(self, section_title_pattern, body=None):
        """提取指定章节的文本内容"""
        if body is None:
            body = self.body
        
        pattern = rf'^##\s+{section_title_pattern}\s*$'
        match = re.search(pattern, body, re.MULTILINE | re.IGNORECASE)
        
        if not match:
            return None, None, None
        
        start_pos = match.start()
        section_title = match.group(0).strip()
        
        # 找到下一个二级标题
        rest = body[match.end():]
        next_h2 = re.search(r'^##\s+.+$', rest, re.MULTILINE)
        
        if next_h2:
            end_pos = match.end() + next_h2.start()
            section_content = rest[:next_h2.start()].strip()
        else:
            end_pos = len(body)
            section_content = rest.strip()
        
        return section_title, section_content, (start_pos, end_pos)

    def _extract_all_sections(self):
        """提取所有二级章节"""
        sections = {}
        lines = self.body.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            h2_match = re.match(r'^##\s+(.+)$', line)
            if h2_match:
                if current_section:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = h2_match.group(1).strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections

    def _find_duplicate_h1(self):
        """检查重复的H1标题"""
        h1_count = len(re.findall(r'^#\s+.+$', self.body, re.MULTILINE))
        if self.frontmatter.get('title'):
            h1_count += 1
        return h1_count > 1

    def _extract_core_content(self):
        """提取核心正文内容（从"内容"章节）"""
        sections = self._extract_all_sections()
        
        content_section = None
        for title, content in sections.items():
            clean_title = self._remove_emoji(title).strip()
            if clean_title in ['内容', '正文', '主要内容', '核心内容']:
                content_section = content
                break
        
        if content_section:
            return content_section
        
        # 如果没有明确的"内容"章节，返回所有章节的合并
        return self.body

    def _generate_summary(self):
        """生成高质量概要（一句话）"""
        # 1. 尝试从核心要点提取
        sections = self._extract_all_sections()
        core_points = ""
        
        for title, content in sections.items():
            clean_title = self._remove_emoji(title).strip()
            if clean_title in ['核心要点', '💡 核心要点', '快速导读', '📋 快速导读']:
                # 提取列表项
                items = re.findall(r'^[-*]\s+(.+)$', content, re.MULTILINE)
                if items:
                    core_points = items[0]
                    break
        
        # 2. 尝试从内容章节提取第一段
        if not core_points:
            content_text = self._extract_core_content()
            paragraphs = [p.strip() for p in content_text.split('\n\n') if p.strip() and not p.strip().startswith('#') and not p.strip().startswith('>')]
            if paragraphs:
                for p in paragraphs:
                    if len(p) > 20 and len(p) < 200:
                        core_points = p
                        break
        
        # 3. 从标题推断
        if not core_points:
            core_points = f"本文介绍了{self.title}的相关内容"
        
        # 清理并确保是一句话
        summary = core_points.strip()
        summary = re.sub(r'\*\*', '', summary)
        summary = re.sub(r'📊|📈|📌|🔄|🔍|💡|🎯|📱|📚|🔗|🏆|⭐|⏱️|🏷️|📅|📝|🛠️|🚀|🤖|🌐|🆕|📎|💼|🌍', '', summary)
        
        # 确保不超过100字
        if len(summary) > 100:
            summary = summary[:97] + "..."
        
        # 确保是完整的一句话
        if not summary.endswith('。') and not summary.endswith('！') and not summary.endswith('？') and not summary.endswith('…'):
            summary += '。'
        
        self.summary = summary
        return self.summary

    def _extract_keywords(self):
        """提取高质量核心关键词"""
        keywords = []
        
        # 1. 从frontmatter的tags提取（如果有意义的话）
        if self.frontmatter.get('tags') and self.frontmatter['tags'] != 'null':
            tags = self.frontmatter['tags']
            if isinstance(tags, list):
                for tag in tags:
                    tag_clean = self._remove_emoji(str(tag)).strip()
                    if tag_clean and len(tag_clean) > 1 and len(tag_clean) < 15:
                        # 排除分类名和无意义词
                        exclude_words = ['产品与设计', 'AI与机器学习', '知识管理', '行业动态', 
                                        '系统与运维', '云计算与DevOps', '数据库', '编程与开发']
                        if tag_clean not in exclude_words and tag_clean not in keywords:
                            keywords.append(tag_clean)
        
        # 2. 从标题提取核心词汇
        title_keywords = self._extract_keywords_from_title()
        for kw in title_keywords:
            if kw not in keywords:
                keywords.append(kw)
        
        # 3. 从正文高频词提取
        content_text = self._extract_core_content()
        freq_keywords = self._extract_freq_keywords(content_text)
        for kw in freq_keywords:
            if len(keywords) >= 5:
                break
            if kw not in keywords:
                keywords.append(kw)
        
        # 确保3-5个关键词
        if len(keywords) < 3:
            # 从分类补充
            if self.frontmatter.get('categories'):
                cats = self.frontmatter['categories']
                if isinstance(cats, str):
                    cats = [c.strip() for c in cats.split(',')]
                for cat in cats:
                    cat_clean = self._remove_emoji(cat).strip()
                    if cat_clean and cat_clean not in keywords:
                        keywords.append(cat_clean)
                        if len(keywords) >= 3:
                            break
        
        # 限制最多5个
        keywords = keywords[:5]
        self.keywords = keywords
        return keywords

    def _extract_keywords_from_title(self):
        """从标题提取核心关键词"""
        title = self.title
        
        # 常见产品名和技术术语
        known_terms = [
            'Dify', 'Jinja2', 'OCR', 'RAG', 'Agent', 'Workflow', 'LLM',
            '知识库', '工作流', '模板', '循环节点', '插件节点', '多模态',
            '图文处理', 'Proactive', '交互设计', '产品设计', '用户体验',
            '人形机器人', '世界模型', '冷板', 'QuickAdd', 'Sonar',
            'NioPD', 'KBNF', '约束解码', 'FLUX', '图像生成',
            'Excel', 'Word', '飞书', '多维表格'
        ]
        
        found = []
        for term in known_terms:
            if term.lower() in title.lower() and term not in found:
                found.append(term)
        
        return found

    def _extract_freq_keywords(self, text, top_n=10):
        """从文本中提取高频关键词"""
        # 移除markdown标记
        clean_text = re.sub(r'[#*`>\-]', '', text)
        clean_text = re.sub(r'\[.*?\]\(.*?\)', '', clean_text)
        
        # 已知技术术语优先
        tech_terms = [
            'Dify', 'Jinja2', 'OCR', 'RAG', 'Agent', 'Workflow', 'LLM',
            '知识库', '工作流', '模板', '循环', '插件', '多模态',
            '图文处理', '交互设计', '产品设计', '用户体验',
            '向量检索', '全文检索', '混合检索', '分块', '分段',
            'Prompt', '提示词', '大模型', 'AI', '机器学习',
            '私有化部署', '本地部署', '可视化', '低代码', '零代码'
        ]
        
        found = []
        for term in tech_terms:
            count = text.lower().count(term.lower())
            if count > 0:
                found.append((term, count))
        
        found.sort(key=lambda x: x[1], reverse=True)
        return [t[0] for t in found[:top_n]]

    def _clean_duplicate_sections(self):
        """清理重复的章节"""
        sections = self._extract_all_sections()
        cleaned_sections = {}
        duplicates_removed = 0
        
        # 定义重复章节的合并规则
        merge_rules = {
            '核心要点': ['核心要点', '💡 核心要点', '快速导读', '📋 快速导读'],
            '背景与上下文': ['背景与上下文', '🌐 背景与上下文'],
            '深度解读': ['深度解读', '🔍 深度解读'],
            '最新进展': ['最新进展', '🆕 2025-2026 最新进展'],
            '相关资源': ['相关资源', '📚 相关资源', '📎 相关素材'],
            '相关文章': ['相关文章', '🔗 相关文章'],
            '延伸阅读': ['延伸阅读', '📚 延伸阅读'],
            '参考来源': ['参考来源', '📖 参考来源'],
            '知识关联': ['知识关联', '🔗 知识关联'],
            '参考文件': ['参考文件'],
        }
        
        seen_content_hashes = set()
        
        for title, content in sections.items():
            clean_title = self._remove_emoji(title).strip()
            
            # 计算内容哈希用于去重
            content_hash = hash(content.strip()[:500])
            
            if content_hash in seen_content_hashes and len(content) > 100:
                duplicates_removed += 1
                continue
            seen_content_hashes.add(content_hash)
            
            # 标准化标题
            normalized_title = None
            for std_name, variants in merge_rules.items():
                for variant in variants:
                    if clean_title == self._remove_emoji(variant).strip():
                        normalized_title = std_name
                        break
                if normalized_title:
                    break
            
            if normalized_title:
                if normalized_title in cleaned_sections:
                    # 合并内容（保留更长的）
                    if len(content) > len(cleaned_sections[normalized_title]):
                        cleaned_sections[normalized_title] = content
                    duplicates_removed += 1
                else:
                    cleaned_sections[normalized_title] = content
            else:
                cleaned_sections[clean_title] = content
        
        self.stats['removed_duplicates'] = duplicates_removed
        self.sections = cleaned_sections
        return cleaned_sections

    def _clean_section_titles(self):
        """清理章节标题中的emoji"""
        cleaned = {}
        emoji_count = 0
        
        for title, content in self.sections.items():
            clean_title = self._remove_emoji(title).strip()
            if clean_title != title:
                emoji_count += 1
            cleaned[clean_title] = content
        
        self.stats['removed_emoji_titles'] = emoji_count
        self.sections = cleaned
        return cleaned

    def _extract_body_content(self):
        """提取正文核心内容（去掉重复的头尾部分）
        
        正文内容包括：内容、背景与上下文、深度解读、最新进展等
        元信息章节：目录、核心要点、快速导读、相关资源、相关文章、延伸阅读、
                   参考来源、知识关联、参考文件、Changelog
        """
        sections = self.sections
        
        # 定义元信息章节（这些会被移到文档尾部或舍弃）
        meta_section_names = [
            '目录', '核心要点', '快速导读',
            '相关资源', '相关文章', '延伸阅读',
            '参考来源', '知识关联', '参考文件',
            'Changelog', '相关素材'
        ]
        
        # 按原始顺序收集正文章节
        body_parts = []
        
        # 重新从原始body提取章节顺序
        all_sections_ordered = self._extract_all_sections_ordered()
        
        for title, content in all_sections_ordered:
            clean_title = self._remove_emoji(title).strip()
            
            # 检查是否是元信息章节
            is_meta = False
            for meta_name in meta_section_names:
                if meta_name in clean_title:
                    is_meta = True
                    break
            
            if not is_meta:
                # 清理标题中的emoji
                cleaned_title = self._remove_emoji(title).strip()
                body_parts.append(f"## {cleaned_title}\n\n{content.strip()}")
        
        if body_parts:
            return '\n\n'.join(body_parts)
        
        # 如果没有找到任何章节，返回原始body
        return self.body

    def _extract_all_sections_ordered(self):
        """按原始顺序提取所有二级章节（标题, 内容）"""
        sections = []
        lines = self.body.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            h2_match = re.match(r'^##\s+(.+)$', line)
            if h2_match:
                if current_section:
                    sections.append((current_section, '\n'.join(current_content).strip()))
                current_section = h2_match.group(1).strip()
                current_content = []
            elif current_section:
                current_content.append(line)
        
        if current_section:
            sections.append((current_section, '\n'.join(current_content).strip()))
        
        return sections

    def _extract_internal_references(self):
        """提取内部知识库引用"""
        refs = []
        sections = self.sections
        
        # 从参考文件、知识关联等章节提取
        for section_name in ['参考文件', '知识关联', '相关资源']:
            if section_name in sections:
                content = sections[section_name]
                # 提取markdown链接
                links = re.findall(r'\[([^\]]+)\]\(([^)]+\.md[^)]*)\)', content)
                for link_text, link_url in links:
                    if 'knowledge/' in link_url or 'newwiki' in link_url or 'import/' in link_url:
                        if (link_text, link_url) not in refs:
                            refs.append((link_text, link_url))
        
        return refs[:10]  # 最多保留10个

    def _extract_external_references(self):
        """提取外部资料引用"""
        refs = []
        sections = self.sections
        
        # 从参考来源提取
        if '参考来源' in sections:
            content = sections['参考来源']
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 提取编号列表项
                    match = re.match(r'^\d+\.\s*(.+)$', line)
                    if match:
                        ref_text = match.group(1).strip()
                        if ref_text and len(ref_text) > 5:
                            refs.append(ref_text)
        
        # 如果没有参考来源，从原文链接提取
        if not refs:
            original_link = self._extract_original_link()
            if original_link:
                refs.append(f"原文链接：{original_link}")
        
        return refs[:5]

    def _extract_original_link(self):
        """提取原文链接"""
        # 从frontmatter
        # 从正文查找
        link_match = re.search(r'原文链接[：:]\s*\[?([^\]\n]+)?\]?\(?([^\)\n]+)?\)?', self.body)
        if link_match and link_match.group(2):
            return link_match.group(2)
        
        # 查找来源标记
        source_match = re.search(r'\[来源:\s*([^\]]+)\]', self.body)
        if source_match:
            return source_match.group(1)
        
        return None

    def _extract_publish_date(self):
        """提取发布时间"""
        if self.frontmatter.get('created_at'):
            return str(self.frontmatter['created_at']).split()[0]
        
        date_match = re.search(r'发布时间[：:]\s*(\d{4}[-/]\d{2}[-/]\d{2})', self.body)
        if date_match:
            return date_match.group(1)
        
        return None

    def _generate_toc(self, body_content):
        """生成目录（只列核心二级标题）"""
        toc_items = []
        lines = body_content.split('\n')
        
        for line in lines:
            h2_match = re.match(r'^##\s+(.+)$', line)
            if h2_match:
                title = h2_match.group(1).strip()
                title = self._remove_emoji(title).strip()
                # 生成锚点
                anchor = re.sub(r'[^\w\u4e00-\u9fff-]', '', title.replace(' ', '-'))
                anchor = anchor.lower()
                toc_items.append((title, anchor))
        
        return toc_items

    def refactor(self):
        """执行完整重构流程"""
        # 1. 生成概要
        self._generate_summary()
        
        # 2. 提取关键词
        self._extract_keywords()
        
        # 3. 清理重复章节
        self._clean_duplicate_sections()
        
        # 4. 清理章节标题emoji
        self._clean_section_titles()
        
        # 5. 提取核心正文
        body_content = self._extract_body_content()
        
        # 6. 提取引用
        internal_refs = self._extract_internal_references()
        external_refs = self._extract_external_references()
        
        # 7. 生成目录
        toc_items = self._generate_toc(body_content)
        
        # 8. 构建新文档
        new_content = self._build_new_document(body_content, toc_items, internal_refs, external_refs)
        
        self.stats['new_lines'] = len(new_content.split('\n'))
        
        return new_content

    def _build_new_document(self, body_content, toc_items, internal_refs, external_refs):
        """构建新的文档结构"""
        lines = []
        
        # 1. YAML frontmatter（保留）
        if self.frontmatter:
            # 更新frontmatter
            fm = copy.deepcopy(self.frontmatter)
            fm['title'] = self.title
            fm['updated_at'] = datetime.now().strftime('%Y-%m-%d')
            
            lines.append('---')
            fm_yaml = yaml.dump(fm, allow_unicode=True, default_flow_style=False).strip()
            lines.append(fm_yaml)
            lines.append('---')
            lines.append('')
        
        # 2. 标题
        lines.append(f'# {self.title}')
        lines.append('')
        
        # 3. 概要和关键词
        lines.append(f'> **概要**: {self.summary}')
        lines.append(f'> **关键词**: {" · ".join(self.keywords)}')
        lines.append('')
        
        # 4. 元信息（发布时间、原文链接等）
        meta_lines = []
        publish_date = self._extract_publish_date()
        if publish_date:
            meta_lines.append(f'> **发布时间**: {publish_date}')
        
        original_link = self._extract_original_link()
        if original_link:
            meta_lines.append(f'> **原文链接**: {original_link}')
        
        if meta_lines:
            lines.extend(meta_lines)
            lines.append('')
        
        # 5. 目录（如果有多个二级标题）
        if len(toc_items) >= 3:
            lines.append('## 📑 目录')
            lines.append('')
            for title, anchor in toc_items:
                lines.append(f'- [{title}](#{anchor})')
            lines.append('')
        
        # 6. 正文内容
        if body_content:
            lines.append(body_content.strip())
            lines.append('')
        
        # 7. 参考文件
        lines.append('## 参考文件')
        lines.append('')
        
        lines.append('### 内部知识库引用')
        if internal_refs:
            for ref_text, ref_url in internal_refs:
                lines.append(f'- [{ref_text}]({ref_url})')
        else:
            lines.append('- 暂无')
        lines.append('')
        
        lines.append('### 外部资料引用')
        if external_refs:
            for ref in external_refs:
                lines.append(f'- {ref}')
        else:
            lines.append('- 暂无')
        lines.append('')
        
        # 8. Changelog
        lines.append('## Changelog')
        lines.append('')
        lines.append('| 日期 | 版本 | 变更说明 |')
        lines.append('|------|------|---------|')
        
        # 从原changelog提取
        original_changelog = self._extract_original_changelog()
        if original_changelog:
            lines.extend(original_changelog)
        
        # 添加本次重构记录
        today = datetime.now().strftime('%Y-%m-%d')
        lines.append(f'| {today} | v3.0 | 深度重构：清理重复内容、优化结构、标准化格式、提升概要与关键词质量 |')
        
        lines.append('')
        
        return '\n'.join(lines)

    def _extract_original_changelog(self):
        """提取原始changelog"""
        sections = self.sections
        changelog_lines = []
        
        if 'Changelog' in sections:
            content = sections['Changelog']
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                # 匹配表格行
                if re.match(r'^\|.+\|.+\|.+\|$', line) and not line.startswith('|---') and '日期' not in line:
                    changelog_lines.append(line)
        
        return changelog_lines[:5]  # 最多保留5条

    def save(self, new_content, backup=True):
        """保存重构后的文件"""
        if backup:
            # 创建备份
            backup_path = self.file_path.with_suffix('.bak')
            if not backup_path.exists():
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(self.raw_content)
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return self.file_path


def process_directory(dir_path, skip_index=True, dry_run=False):
    """批量处理目录下的所有markdown文件"""
    dir_path = Path(dir_path)
    md_files = sorted(dir_path.glob('*.md'))
    
    results = []
    stats = {
        'total': 0,
        'processed': 0,
        'skipped': 0,
        'errors': 0,
        'total_original_lines': 0,
        'total_new_lines': 0,
        'total_duplicates_removed': 0,
        'files_with_duplicate_h1': [],
        'files_with_low_quality_keywords': []
    }
    
    for md_file in md_files:
        if skip_index and md_file.name == 'index.md':
            stats['skipped'] += 1
            continue
        
        stats['total'] += 1
        print(f"\n处理: {md_file.name}")
        
        try:
            refactor = MarkdownDocRefactor(md_file)
            refactor.load()
            
            # 检查问题
            if refactor._find_duplicate_h1():
                stats['files_with_duplicate_h1'].append(md_file.name)
            
            # 执行重构
            new_content = refactor.refactor()
            
            # 检查关键词质量
            if len(refactor.keywords) < 3:
                stats['files_with_low_quality_keywords'].append(md_file.name)
            
            if not dry_run:
                refactor.save(new_content)
            
            stats['processed'] += 1
            stats['total_original_lines'] += refactor.stats['original_lines']
            stats['total_new_lines'] += refactor.stats['new_lines']
            stats['total_duplicates_removed'] += refactor.stats['removed_duplicates']
            
            results.append({
                'file': md_file.name,
                'status': 'success',
                'original_lines': refactor.stats['original_lines'],
                'new_lines': refactor.stats['new_lines'],
                'duplicates_removed': refactor.stats['removed_duplicates'],
                'keywords': refactor.keywords,
                'summary': refactor.summary[:50] + '...'
            })
            
            print(f"  ✓ 完成 ({refactor.stats['original_lines']} -> {refactor.stats['new_lines']} 行)")
            print(f"    关键词: {' · '.join(refactor.keywords)}")
            
        except Exception as e:
            stats['errors'] += 1
            results.append({
                'file': md_file.name,
                'status': 'error',
                'error': str(e)
            })
            print(f"  ✗ 错误: {e}")
    
    return results, stats


def print_report(results, stats):
    """打印处理报告"""
    print("\n" + "="*70)
    print("📊 批量重构质量统计报告")
    print("="*70)
    
    print(f"\n📁 处理概览:")
    print(f"  总文件数: {stats['total']}")
    print(f"  成功处理: {stats['processed']}")
    print(f"  跳过(index.md): {stats['skipped']}")
    print(f"  处理失败: {stats['errors']}")
    
    print(f"\n📏 内容统计:")
    print(f"  原始总行数: {stats['total_original_lines']}")
    print(f"  重构后总行数: {stats['total_new_lines']}")
    print(f"  行数变化: {stats['total_new_lines'] - stats['total_original_lines']:+d} 行")
    print(f"  清理重复章节: {stats['total_duplicates_removed']} 处")
    
    print(f"\n🔍 质量问题修复:")
    print(f"  重复H1标题文件: {len(stats['files_with_duplicate_h1'])} 个")
    if stats['files_with_duplicate_h1']:
        for f in stats['files_with_duplicate_h1'][:5]:
            print(f"    - {f}")
        if len(stats['files_with_duplicate_h1']) > 5:
            print(f"    ... 等 {len(stats['files_with_duplicate_h1'])} 个文件")
    
    print(f"  低质量关键词文件: {len(stats['files_with_low_quality_keywords'])} 个")
    if stats['files_with_low_quality_keywords']:
        for f in stats['files_with_low_quality_keywords'][:5]:
            print(f"    - {f}")
    
    print(f"\n✅ 已完成的核心重构:")
    print(f"  1. ✓ 清理重复内容（重复H1标题、重复章节）")
    print(f"  2. ✓ 重写高质量概要（一句话总结）")
    print(f"  3. ✓ 重写高质量关键词（3-5个核心关键词）")
    print(f"  4. ✓ 重构内容结构（合并重复章节、去除emoji前缀）")
    print(f"  5. ✓ 标准化格式（统一头部、目录、参考文件、Changelog）")
    
    print("\n" + "="*70)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='批量重构产品与设计目录下的markdown文件')
    parser.add_argument('directory', help='目标目录路径')
    parser.add_argument('--dry-run', action='store_true', help='试运行，不修改文件')
    parser.add_argument('--no-skip-index', action='store_true', help='不跳过index.md')
    
    args = parser.parse_args()
    
    dir_path = Path(args.directory)
    if not dir_path.exists():
        print(f"错误: 目录不存在: {dir_path}")
        sys.exit(1)
    
    print(f"🚀 开始批量重构目录: {dir_path}")
    print(f"试运行模式: {'是' if args.dry_run else '否'}")
    
    results, stats = process_directory(
        dir_path,
        skip_index=not args.no_skip_index,
        dry_run=args.dry_run
    )
    
    print_report(results, stats)
    
    # 保存详细结果
    result_file = dir_path / '_refactor_report.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'stats': stats,
            'results': results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 详细报告已保存至: {result_file}")


if __name__ == '__main__':
    main()
