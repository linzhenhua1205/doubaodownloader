#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
遍历项目中的md和txt文件，提取用户提问的问题并汇总
"""

import os
import re
from pathlib import Path


def extract_user_questions_from_file(file_path):
    """
    从文件中提取用户提问
    """
    questions = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
            lines = content.split('\n')
            
            # 用于标记上一行的内容
            prev_line = ''
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                if not line or len(line) < 3:
                    prev_line = line
                    continue
                
                # AI回复的特征 - 这些行前面的行可能是用户提问
                ai_response_patterns = [
                    r'^我将.*',
                    r'^即将开始.*',
                    r'^接下来将为你生成报告：',
                    r'^为了给你提供更有针对性的',
                    r'^为了更好地支持您的',
                    r'^为了更准确地分析您的',
                    r'^创建时间：',
                    r'^需要我.*吗[？?]$',
                    r'^补充内容已覆盖各维度',
                    r'^我将严格按照你给出的',
                ]
                
                # 检查上一行是否是AI回复的特征
                is_prev_line_ai = False
                for pattern in ai_response_patterns:
                    if re.match(pattern, prev_line):
                        is_prev_line_ai = True
                        break
                
                # 检查当前行是否是用户提问
                is_user_question = False
                
                # 规则1：如果上一行是AI回复特征，则当前行可能是用户提问
                if is_prev_line_ai:
                    # 排除明显不是用户提问的情况
                    exclude_patterns = [
                        r'^来自\s*<',
                        r'^###',
                        r'^##',
                        r'^#',
                        r'^- ',
                        r'^\d+\.\s',
                        r'^\d+\.$',
                        r'^[a-z]\.\s',
                        r'^[A-Z]\.\s',
                        r'^\*',
                        r'^[a-zA-Z]',
                    ]
                    should_exclude = False
                    for pattern in exclude_patterns:
                        if re.match(pattern, line):
                            should_exclude = True
                            break
                    if not should_exclude:
                        is_user_question = True
                
                # 规则2：包含明确的用户提问标识词
                user_question_keywords = [
                    '如何', '怎么', '怎样', '能否', '能不能', '是否', '有没有', 
                    '有什么', '什么', '哪些', '哪个', '哪里', '多少', '为什么', 
                    '请问', '我需要', '希望', '希望能够', '希望你', '帮我', '请帮我',
                    '详细描述', '详细说明', '全面分析', '重新创建', '结合',
                    '整理', '提炼', '细化补充', '参考', '改用',
                ]
                for keyword in user_question_keywords:
                    if keyword in line and len(line) > 10:
                        # 进一步排除不是用户提问的情况
                        exclude_phrases = [
                            '我将', '我会', '为你', '给你', '为您', '给您',
                            '创建时间', '即将开始', '接下来', '需要我', '希望我',
                        ]
                        is_excluded = False
                        for phrase in exclude_phrases:
                            if phrase in line:
                                is_excluded = True
                                break
                        if not is_excluded:
                            is_user_question = True
                            break
                
                # 规则3：以问号结尾，且不是AI的提问
                if (line.endswith('?') or line.endswith('？')) and not line.startswith('需要我') and not line.startswith('希望我'):
                    is_user_question = True
                
                # 排除AI回复的特征
                ai_exclude_patterns = [
                    r'^我将.*',
                    r'^即将开始.*',
                    r'^接下来将为你生成报告：',
                    r'^为了给你提供更有针对性的',
                    r'^为了更好地支持您的',
                    r'^为了更准确地分析您的',
                    r'^创建时间：',
                    r'^需要我.*吗[？?]$',
                    r'^补充内容已覆盖各维度',
                    r'^我将严格按照你给出的',
                    r'^我还用网页的形式',
                    r'^来自\s*<',
                    r'^[a-zA-Z]',
                ]
                for pattern in ai_exclude_patterns:
                    if re.match(pattern, line):
                        is_user_question = False
                        break
                
                if is_user_question:
                    # 最终过滤 - 确保不是列表项、标题等
                    if not re.match(r'^- ', line) and not re.match(r'^\d+\.\s', line) and not re.match(r'^#', line):
                        questions.append(line)
                
                prev_line = line
    
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
    
    # 去重
    questions = list(set(questions))
    return questions


def main():
    base_dir = Path(r"H:\github\md")
    all_questions = {}
    
    # 查找所有md和txt文件
    file_patterns = ['**/*.md', '**/*.txt']
    
    print("开始遍历文件...")
    
    for pattern in file_patterns:
        files = list(base_dir.glob(pattern))
        print(f"找到 {len(files)} 个 {pattern} 文件")
        
        for file_path in files:
            questions = extract_user_questions_from_file(file_path)
            if questions:
                all_questions[str(file_path)] = questions
                print(f"  {file_path.name}: 提取到 {len(questions)} 个问题")
    
    # 汇总所有问题
    total_questions = sum(len(q) for q in all_questions.values())
    print(f"\n总共从 {len(all_questions)} 个文件中提取到 {total_questions} 个问题")
    
    # 生成汇总报告
    output_file = base_dir / "用户提问汇总.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 用户提问汇总\n\n")
        f.write(f"- 生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- 汇总文件数: {len(all_questions)}\n")
        f.write(f"- 问题总数: {total_questions}\n\n")
        
        f.write("## 问题列表\n\n")
        
        for file_path, questions in all_questions.items():
            f.write(f"### 文件: {Path(file_path).name}\n\n")
            for i, question in enumerate(questions, 1):
                f.write(f"{i}. {question}\n")
            f.write("\n")
    
    print(f"\n汇总已保存到: {output_file}")


if __name__ == "__main__":
    main()
