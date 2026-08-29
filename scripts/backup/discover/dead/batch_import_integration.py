#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import 素材大规模深度嵌入 - 批量处理脚本
将 import 目录中的高质量素材深度嵌入到 discover 目录的内容中
"""

import os
import re
from pathlib import Path


class ImportIntegration:
    def __init__(self, discover_root, import_root):
        self.discover_root = Path(discover_root)
        self.import_root = Path(import_root)
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'total_added_chars': 0,
            'materials_used': [],
        }

    def read_file(self, filepath):
        """读取文件内容"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"读取文件失败 {filepath}: {e}")
            return None

    def write_file(self, filepath, content):
        """写入文件内容"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"写入文件失败 {filepath}: {e}")
            return False

    def compute_relative_path(self, target_file, source_file):
        """计算从目标文件到源文件的相对路径"""
        target_dir = Path(target_file).parent
        rel_path = os.path.relpath(source_file, target_dir)
        return rel_path

    def extract_section(self, content, section_title, max_chars=800):
        """从内容中提取指定章节的内容（前N字）"""
        lines = content.split('\n')
        in_section = False
        extracted = []
        char_count = 0
        
        for line in lines:
            # 检测标题
            if line.startswith('#') and section_title in line:
                in_section = True
                continue
            
            if in_section:
                # 遇到同级或更高级标题时停止
                if line.startswith('#') and len(line.strip()) > 0:
                    # 检查标题级别
                    title_level = len(line) - len(line.lstrip('#'))
                    if title_level <= len(section_title) // 2:
                        break
                
                # 跳过空行和图片注释行
                if line.strip() == '' or '<!--' in line or 'picture text' in line.lower():
                    continue
                
                extracted.append(line)
                char_count += len(line)
                
                if char_count >= max_chars:
                    break
        
        return '\n'.join(extracted) if extracted else ''

    def extract_key_paragraphs(self, content, keywords, max_chars=600):
        """根据关键词提取相关段落"""
        lines = content.split('\n')
        relevant_lines = []
        char_count = 0
        current_paragraph = []
        
        for line in lines:
            # 跳过图片注释和空行
            if '<!--' in line or 'picture text' in line.lower() or line.strip() == '':
                if current_paragraph:
                    para_text = ' '.join(current_paragraph)
                    if any(kw in para_text for kw in keywords):
                        relevant_lines.extend(current_paragraph)
                        relevant_lines.append('')
                        char_count += len(para_text)
                    current_paragraph = []
                continue
            
            current_paragraph.append(line)
            
            if char_count >= max_chars:
                break
        
        # 处理最后一段
        if current_paragraph and char_count < max_chars:
            para_text = ' '.join(current_paragraph)
            if any(kw in para_text for kw in keywords):
                relevant_lines.extend(current_paragraph)
        
        return '\n'.join(relevant_lines) if relevant_lines else ''

    def clean_content(self, content):
        """清理内容，移除图片注释等无用内容"""
        # 移除 HTML 注释
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        # 移除多余空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content.strip()

    def insert_after_section(self, target_content, section_marker, insert_content):
        """在指定章节后插入内容"""
        lines = target_content.split('\n')
        result = []
        inserted = False
        section_found = False
        section_level = 0
        
        for i, line in enumerate(lines):
            result.append(line)
            
            # 找到目标章节
            if not inserted and section_marker in line and line.startswith('#'):
                section_found = True
                section_level = len(line) - len(line.lstrip('#'))
                continue
            
            # 在章节内容中找到合适的插入点（下一个同级或更高级标题前）
            if section_found and not inserted:
                if line.startswith('#') and len(line) - len(line.lstrip('#')) <= section_level:
                    # 在这个标题前插入
                    result.pop()  # 移除刚加入的标题行
                    result.append('')
                    result.append(insert_content)
                    result.append('')
                    result.append(line)  # 重新加入标题行
                    inserted = True
                elif i == len(lines) - 1:
                    # 文件末尾
                    result.append('')
                    result.append(insert_content)
                    result.append('')
                    inserted = True
        
        if not inserted:
            # 如果没找到插入点，追加到文件末尾（参考来源之前）
            if '## 参考来源' in target_content:
                idx = target_content.index('## 参考来源')
                return target_content[:idx] + '\n' + insert_content + '\n\n' + target_content[idx:]
            else:
                return target_content + '\n\n' + insert_content + '\n'
        
        return '\n'.join(result)

    def integrate_material(self, target_file, source_file, section_marker, material_title, keywords=None, max_chars=600):
        """
        将单个素材整合到目标文件中
        
        Args:
            target_file: 目标文件路径
            source_file: 源素材文件路径
            section_marker: 插入位置的章节标记
            material_title: 插入内容的标题
            keywords: 关键词列表（用于提取相关内容）
            max_chars: 最大提取字数
        """
        target_content = self.read_file(target_file)
        source_content = self.read_file(source_file)
        
        if not target_content or not source_content:
            return False
        
        # 检查是否已经整合过（避免重复）
        source_name = Path(source_file).name
        if source_name in target_content:
            print(f"  跳过（已整合）: {source_name}")
            return False
        
        # 提取素材内容
        if keywords:
            extracted = self.extract_key_paragraphs(source_content, keywords, max_chars)
        else:
            extracted = self.extract_section(source_content, material_title, max_chars)
        
        if not extracted or len(extracted.strip()) < 100:
            # 如果提取不到足够内容，尝试从全文提取
            cleaned = self.clean_content(source_content)
            extracted = cleaned[:max_chars]
        
        if not extracted or len(extracted.strip()) < 50:
            print(f"  跳过（内容不足）: {source_name}")
            return False
        
        # 计算相对路径
        rel_path = self.compute_relative_path(target_file, source_file)
        
        # 构建插入内容
        insert_block = f"""### 深度扩展：{material_title}

{extracted.strip()}

> 来源：[{source_name}]({rel_path})"""
        
        # 插入到目标文件
        new_content = self.insert_after_section(target_content, section_marker, insert_block)
        
        if new_content != target_content:
            self.write_file(target_file, new_content)
            added_chars = len(new_content) - len(target_content)
            self.stats['total_added_chars'] += added_chars
            self.stats['materials_used'].append(source_name)
            print(f"  ✓ 已整合: {source_name} (+{added_chars}字)")
            return True
        
        return False

    def batch_integrate(self, integration_map):
        """
        批量整合
        
        Args:
            integration_map: 整合映射列表，每个元素是一个 dict：
                {
                    'target': 目标文件,
                    'sources': [
                        {
                            'source': 源文件,
                            'section': 插入章节标记,
                            'title': 内容标题,
                            'keywords': 关键词列表（可选）,
                            'max_chars': 最大字数（可选）
                        }
                    ]
                }
        """
        for item in integration_map:
            target = item['target']
            sources = item.get('sources', [])
            
            if not os.path.exists(target):
                print(f"跳过不存在的文件: {target}")
                continue
            
            self.stats['total_files'] += 1
            print(f"\n处理文件: {Path(target).name}")
            
            for src in sources:
                source_file = src['source']
                if not os.path.exists(source_file):
                    print(f"  跳过不存在的素材: {source_file}")
                    continue
                
                self.integrate_material(
                    target_file=target,
                    source_file=source_file,
                    section_marker=src.get('section', '技术详解'),
                    material_title=src.get('title', '素材扩展'),
                    keywords=src.get('keywords', None),
                    max_chars=src.get('max_chars', 600)
                )
            
            self.stats['processed_files'] += 1

    def print_stats(self):
        """打印统计信息"""
        print("\n" + "="*60)
        print("整合统计")
        print("="*60)
        print(f"目标文件总数: {self.stats['total_files']}")
        print(f"已处理文件数: {self.stats['processed_files']}")
        print(f"新增总字数: {self.stats['total_added_chars']}")
        print(f"使用素材数: {len(self.stats['materials_used'])}")
        print(f"使用素材列表: {', '.join(self.stats['materials_used'][:10])}...")
        print("="*60)


def main():
    discover_root = r'h:\github\cowkb\discover'
    import_root = r'h:\github\cowkb\import'
    
    integrator = ImportIntegration(discover_root, import_root)
    
    # ========== 第一批：AI 技术类 ==========
    print("="*60)
    print("第一批：AI 技术类内容整合")
    print("="*60)
    
    ai_model_arch = os.path.join(discover_root, 'newwiki2', 'AI-模型架构')
    doubao_dir = os.path.join(import_root, 'doubao')
    qianwen_dir = os.path.join(import_root, '千问')
    
    # 定义整合映射
    integration_map = [
        # 1. Transformer 架构
        {
            'target': os.path.join(ai_model_arch, 'transformer.md'),
            'sources': [
                {
                    'source': os.path.join(doubao_dir, '机器学习基础.md'),
                    'section': '### 一、Transformer的革命性突破',
                    'title': '神经网络基础与学习原理',
                    'keywords': ['神经网络', '学习', '训练', '梯度下降'],
                    'max_chars': 500
                },
                {
                    'source': os.path.join(doubao_dir, '注意力机制通俗解析.md'),
                    'section': '### 一、Transformer的革命性突破',
                    'title': '注意力机制通俗理解',
                    'keywords': ['注意力', 'Q', 'K', 'V', 'self-attention'],
                    'max_chars': 600
                },
            ]
        },
        # 2. Attention 注意力机制
        {
            'target': os.path.join(ai_model_arch, 'attention.md'),
            'sources': [
                {
                    'source': os.path.join(doubao_dir, '注意力机制通俗解析.md'),
                    'section': '### 一、标准 Scaled Dot-Product Attention',
                    'title': '注意力机制的通俗比喻',
                    'keywords': ['注意力', 'Q', 'K', 'V', '通俗'],
                    'max_chars': 500
                },
                {
                    'source': os.path.join(doubao_dir, '机器学习基础.md'),
                    'section': '### 一、标准 Scaled Dot-Product Attention',
                    'title': '机器学习中的特征加权思想',
                    'keywords': ['特征', '权重', '学习', '回归'],
                    'max_chars': 400
                },
            ]
        },
        # 3. Training 模型训练
        {
            'target': os.path.join(ai_model_arch, 'training.md'),
            'sources': [
                {
                    'source': os.path.join(doubao_dir, '机器学习基础.md'),
                    'section': '### 二、预训练核心技术',
                    'title': '梯度下降与优化基础',
                    'keywords': ['梯度下降', '代价函数', '学习率', '训练'],
                    'max_chars': 600
                },
                {
                    'source': os.path.join(doubao_dir, '深入研究.md'),
                    'section': '### 二、预训练核心技术',
                    'title': '深度学习训练前沿研究',
                    'keywords': ['训练', '优化', '模型', '学习'],
                    'max_chars': 500
                },
            ]
        },
        # 4. Finetuning 微调
        {
            'target': os.path.join(ai_model_arch, 'finetuning.md'),
            'sources': [
                {
                    'source': os.path.join(doubao_dir, '机器学习基础.md'),
                    'section': '### 一、微调基础',
                    'title': '监督学习与模型泛化',
                    'keywords': ['监督学习', '泛化', '过拟合', '训练'],
                    'max_chars': 400
                },
                {
                    'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                    'section': '### 三、参数高效微调（PEFT）',
                    'title': '大模型微调技术综述',
                    'keywords': ['微调', 'LoRA', 'SFT', '对齐'],
                    'max_chars': 500
                },
            ]
        },
        # 5. Memory 记忆
        {
            'target': os.path.join(ai_model_arch, 'memory.md'),
            'sources': [
                {
                    'source': os.path.join(doubao_dir, '深入研究.md'),
                    'section': '### 一、大模型的两种记忆',
                    'title': 'AI记忆机制研究',
                    'keywords': ['记忆', 'memory', '上下文', '长期记忆'],
                    'max_chars': 500
                },
            ]
        },
        # 6. LLM 大语言模型
        {
            'target': os.path.join(ai_model_arch, 'llm.md'),
            'sources': [
                {
                    'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                    'section': '技术详解',
                    'title': '大模型技术全景',
                    'keywords': ['大模型', 'LLM', '语言模型', '技术'],
                    'max_chars': 700
                },
                {
                    'source': os.path.join(doubao_dir, '机器学习基础.md'),
                    'section': '技术详解',
                    'title': '语言模型的机器学习基础',
                    'keywords': ['语言模型', '概率', '预测', '序列'],
                    'max_chars': 400
                },
            ]
        },
        # 7. MoE 混合专家
        {
            'target': os.path.join(ai_model_arch, 'moe.md'),
            'sources': [
                {
                    'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                    'section': '技术详解',
                    'title': '混合专家模型技术分析',
                    'keywords': ['MoE', '混合专家', '稀疏', '路由'],
                    'max_chars': 500
                },
            ]
        },
        # 8. Inference 推理优化
        {
            'target': os.path.join(ai_model_arch, 'inference.md'),
            'sources': [
                {
                    'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                    'section': '技术详解',
                    'title': '大模型推理优化技术',
                    'keywords': ['推理', 'inference', '优化', '加速'],
                    'max_chars': 500
                },
            ]
        },
        # 9. RAG 检索增强
        {
            'target': os.path.join(ai_model_arch, 'rag.md'),
            'sources': [
                {
                    'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                    'section': '技术详解',
                    'title': '检索增强生成技术',
                    'keywords': ['RAG', '检索', '知识库', '增强'],
                    'max_chars': 500
                },
            ]
        },
        # 10. Model 模型基础
        {
            'target': os.path.join(ai_model_arch, 'model.md'),
            'sources': [
                {
                    'source': os.path.join(doubao_dir, '机器学习基础.md'),
                    'section': '深度导读',
                    'title': '机器学习模型基础',
                    'keywords': ['模型', '学习', '监督', '回归', '分类'],
                    'max_chars': 600
                },
            ]
        },
        # 11. Architecture 架构
        {
            'target': os.path.join(ai_model_arch, 'architecture.md'),
            'sources': [
                {
                    'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                    'section': '技术详解',
                    'title': '大模型架构演进',
                    'keywords': ['架构', '模型', 'Transformer', '演进'],
                    'max_chars': 600
                },
            ]
        },
        # 12. GPU 图形处理器
        {
            'target': os.path.join(ai_model_arch, 'gpu.md'),
            'sources': [
                {
                    'source': os.path.join(qianwen_dir, '大模型技术与原理.md'),
                    'section': '技术详解',
                    'title': 'AI算力与GPU加速',
                    'keywords': ['GPU', '算力', '训练', '加速'],
                    'max_chars': 400
                },
            ]
        },
    ]
    
    # 执行批量整合
    integrator.batch_integrate(integration_map)
    
    # 打印统计
    integrator.print_stats()
    
    print("\n第一批 AI 技术类整合完成！")


if __name__ == '__main__':
    main()
