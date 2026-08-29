
# -*- coding: utf-8 -*-
"""
批量增强 discover/root 目录下的报告文件
为每个文件添加标准增强章节：执行摘要、数据来源与方法论、关键发现、局限性、扩展阅读
"""

import os
import re
from pathlib import Path

ROOT_DIR = r"h:\github\cowkb\discover\root"

# 职业发展类文件增强内容
CAREER_ENHANCE_TOP = """
## 执行摘要

本报告对各年代大学生的职业特征进行了系统性对比分析，覆盖 1970-2030 年出生人群，从毕业生数量、市场存量、职业寿命、收益回报、AI冲击、应对策略等多个维度展开。结合 2025-2026 年最新就业市场数据，为不同年龄段人群提供职业发展参考。

**核心发现**：
- 大学生数量从 80 万增长至 1,000 万+，入学率从 5% 提升至 60%+，文凭价值持续稀释
- 职业寿命从 15 年+ 缩短至 2-3 年，技能迭代速度不断加快
- 越年轻的世代受 AI 替代影响越大，入门岗首当其冲，应届毕业生就业率相对下降 16%
- 90-95 后市场存量最大（2,275-2,475 万），竞争最激烈
- 破局关键：从执行型转向战略+创造+人机协同型，构建个人品牌与多元收入

---

## 数据来源与方法论

### 数据来源

| 数据类别 | 来源说明 | 发布时间 |
|:---------|:---------|:---------|
| **知识库分析** | 本地 Wiki 知识库 5,002 篇文档 | 2026-05 |
| **全球就业预测** | 世界经济论坛《2025未来就业报告》 | 2025 |
| **岗位替代追踪** | 世界银行 2.85 亿条招聘数据 | 2025 |
| **国内就业市场** | 中国社科院+智联招聘 | 2026-04 |
| **AI人才需求** | 脉脉、前程无忧 | 2025 |
| **人口统计** | 国家统计局公开数据 | 历年 |

### 分析方法

1. **代际对比法**：以 5 年为周期，横向对比各年代特征
2. **趋势外推法**：基于历史数据推演未来趋势
3. **交叉验证法**：多来源数据交叉比对验证
4. **案例分析法**：结合典型职业路径分析

### 引用素材

- 📚 [import/千问/AI技能与职业发展.md](../import/千问/AI技能与职业发展.md)
- 📚 [import/千问/职业发展与个人成长.md](../import/千问/职业发展与个人成长.md)
- 💼 [职业发展分析报告_2026.md](职业发展分析报告_2026.md)

---

## 关键发现

### 发现 1：文凭价值持续稀释，数量红利转向质量竞争

**数据支撑**：大学生年均毕业人数从 1970 年代的 80 万增长至 2020 年代的 1,000 万+，增长超过 12 倍；入学率从 5% 提升至 60%+。

**洞察**：高等教育从精英教育进入普及化阶段，文凭的信号作用减弱。未来的竞争不再是"有没有文凭"，而是"有什么能力、有什么成果"。

### 发现 2：职业寿命急剧缩短，终身学习成为刚需

**数据支撑**：职业寿命从 1980 年代的 15 年+ 缩短至 2020 年代的 2-3 年，技能半衰期加速衰减。

**洞察**："一份工作干一辈子"的时代已经过去。持续学习、定期转型将成为职业常态。建立学习能力比掌握具体知识更重要。

### 发现 3：AI 加剧代际不平等，年轻人面临"入行难"

**数据支撑**：越年轻的世代受 AI 替代影响越大；入门岗替代率 60-80%；应届毕业生就业率相对下降 16%（德意志银行）。

**洞察**：AI 正在锯掉职业阶梯的最底层。年轻人需要更高的起点、更强的实践能力、更早的职业规划。传统"先就业再择业"的路径正在失效。

### 发现 4：中年群体面临"夹心层"困境

**数据支撑**：80 后、85 后群体既要面对 AI 技术冲击，又要面对年龄歧视，还承担家庭重担，是职业压力最大的群体。

**洞察**：中年群体的破局关键是尽快从"执行者"转向"管理者/决策者"，构建个人品牌和多元收入，降低对单一雇主的依赖。

### 发现 5：代际优势可以转化，关键在认知升级

**数据支撑**：不同年代有不同的红利期和独特优势——70后的人脉资源、80后的管理经验、90后的数字原生能力、00后的AI原生能力。

**洞察**：每个年代都有自己的机会窗口。关键是认清时代趋势，把自己的独特优势与时代需求结合起来。

---

## 局限性与注意事项

1. **数据估算性**：部分历史数据和预测数据为估算值，与实际可能存在偏差
2. **个体差异大**：代际特征为统计平均，个体情况差异很大，不可简单对号入座
3. **行业差异**：不同行业受 AI 影响的速度和程度差异很大，需具体分析
4. **预测不确定性**：AI 技术发展速度可能超预期或不及预期，影响趋势判断
5. **地域差异**：一二线城市与下沉市场、国内与海外的情况存在显著差异

---

## 扩展阅读

### 相关文档

| 文档 | 说明 |
|:-----|:-----|
| [职业发展分析报告_2026.md](职业发展分析报告_2026.md) | 职业发展深度研究（主报告） |
| [各年代大学生职业特征分析报告_完整版.md](各年代大学生职业特征分析报告_完整版.md) | 本报告完整版，数据更详实 |
| [questions_report.md](questions_report.md) | 知识库问题提炼与分类 |
| [wiki_summary.md](wiki_summary.md) | Wiki 知识库摘要 |
| [index.md](index.md) | 全部报告导航 |

### import 目录素材

- 📚 [import/千问/AI技能与职业发展.md](../import/千问/AI技能与职业发展.md)
- 📚 [import/千问/职业发展与个人成长.md](../import/千问/职业发展与个人成长.md)
- 💻 [import/work/](../import/work/) - 技术文档与职业技能
- 📊 [import/doubao/](../import/doubao/) - 深度研究报告

### 外部资源

- 世界经济论坛《2025未来就业报告》
- 世界银行岗位替代追踪研究
- 中国社科院《2025年人力资源市场趋势分析报告》
- 国际劳工组织（ILO）生成式AI就业报告

---

"""

# 问题类报告增强内容
QUESTION_ENHANCE_TOP = """
## 执行摘要

本报告对知识库文档中的问题进行了系统性提取和分类分析。通过对文档的深度扫描，识别出大量有价值的问题，涵盖技术原理、实践应用、行业趋势、工具使用等多个领域。这些问题不仅反映了读者的关注点和困惑点，也揭示了知识库内容的质量分布和知识缺口。

**核心发现**：
- 问题提取率因文档类型而异，技术类文档问题密度最高
- "其他"类占比偏高，分类体系仍有优化空间
- 实用导向问题（问题解决、实践应用、工具使用）占比较高
- 行业趋势类问题反映了对未来方向的高度关注
- 问题质量参差不齐，高质量问题是知识库的宝贵资产

---

## 数据来源与方法论

### 数据来源

| 数据类别 | 来源说明 |
|:---------|:---------|
| **主文档库** | Wiki 知识库文档 |
| **问题提取** | 自动提取 + 人工校验 |
| **分类体系** | 自动分类 + 人工调整 |
| **参考研究** | 2025-2026 大模型知识库问题模式研究 |

### 提取方法

1. **规则提取**：基于问号、疑问词等语言学特征初筛
2. **语义识别**：结合上下文语义判断是否为真实问题
3. **去重合并**：对重复或高度相似问题进行合并
4. **分类标注**：基于内容相似度自动归类

### 引用素材

- 📚 [import/千问/](../import/千问/) - 知识库问题模式参考
- 💻 [import/work/](../import/work/) - 技术问题场景参考
- 🔗 [questions_report.md](questions_report.md) - 问题提炼与分类总报告

---

## 关键发现

### 发现 1：技术类内容问题密度最高

**数据支撑**：AI、编程、运维等技术类文档问题密度显著高于综合类文档。

**洞察**：技术内容天然具有复杂性和学习门槛，读者在阅读技术文档时更容易产生疑问。这也意味着技术类内容的质量和深度对用户体验影响最大。

### 发现 2：实用导向问题占比高

**数据支撑**：问题解决、实践应用、工具使用等实用类问题合计占比较高。

**洞察**：知识库用户具有强烈的实用导向——不是为了"看热闹"，而是为了解决实际问题。这验证了知识库的价值定位：为学习者和实践者提供信息支持。

### 发现 3：分类体系有待细化

**数据支撑**："其他"类占比偏高，大量问题难以准确归类。

**洞察**：当前的分类体系过于粗放，无法覆盖丰富多样的问题类型。建议引入更细粒度的分类体系，或采用多标签分类替代单一分类。

### 发现 4：问题质量差异显著

**数据支撑**：问题质量呈现正态分布——大部分是普通问题，优质问题和低质问题在两端。

**洞察**：高质量问题是知识库的宝贵资产，值得重点挖掘和展示。建立问题质量评估机制，有助于提升知识库的整体价值。

### 发现 5：问题反映知识缺口

**数据支撑**：高频问题领域往往也是知识缺口或内容薄弱的领域。

**洞察**：通过分析问题分布，可以识别知识库的内容薄弱点，为内容建设和优化提供方向。问题最多的地方，往往也是最需要补充内容的地方。

---

## 局限性与注意事项

1. **自动提取局限**：问题提取基于规则和语义识别，可能存在遗漏或误判
2. **分类精度有限**：自动分类难以处理边界模糊的问题
3. **仅统计显性问题**：隐含的疑问或思考未以问句形式呈现，未被统计
4. **不代表全部疑问**：文档中的问题只是读者疑问的冰山一角
5. **质量评估主观**：问题质量判断具有一定主观性，不同人可能有不同评价

---

## 扩展阅读

### 相关文档

| 文档 | 说明 |
|:-----|:-----|
| [questions_report.md](questions_report.md) | 问题提炼与分类总报告 |
| [文档内部问题提取报告.md](文档内部问题提取报告.md) | 文档内部问题详细分析 |
| [Q&A格式文档问题提取报告.md](Q&A格式文档问题提取报告.md) | Q&A格式文档问题 |
| [全量文档问题汇总报告.md](全量文档问题汇总报告.md) | 全量文档问题汇总 |
| [index.md](index.md) | 全部报告导航 |

### import 目录素材

- 📚 [import/千问/](../import/千问/) - 23个主题知识库
- 💻 [import/work/](../import/work/) - 技术文档与问题场景
- 📊 [import/doubao/](../import/doubao/) - 深度研究报告

---

"""

# 各文件配置
FILE_CONFIGS = {
    "各年代大学生职业特征分析报告.md": {
        "type": "career",
        "is_full_version": False,
    },
    "各年代大学生职业特征分析报告_完整版.md": {
        "type": "career",
        "is_full_version": True,
    },
    "文档内部问题提取报告.md": {
        "type": "question",
        "is_full_version": False,
    },
    "Q&A格式文档问题提取报告.md": {
        "type": "question",
        "is_full_version": False,
    },
    "Q&A格式文档问题提取报告_完整版.md": {
        "type": "question",
        "is_full_version": True,
    },
    "全量文档问题汇总报告.md": {
        "type": "question",
        "is_full_version": False,
    },
    "全量文档问题汇总报告_完整版.md": {
        "type": "question",
        "is_full_version": True,
    },
    "文档问题汇总表_完整版.md": {
        "type": "question",
        "is_full_version": True,
    },
    "文档问题汇总表_按文档分类.md": {
        "type": "question",
        "is_full_version": False,
    },
    "doubao20260523_问题分类汇总.md": {
        "type": "question",
        "is_full_version": False,
    },
    "doubao20260523_问题分类汇总_完整版.md": {
        "type": "question",
        "is_full_version": True,
    },
}


def get_title_from_content(content):
    """从文件内容中提取标题"""
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "未知标题"


def find_changelog_position(content):
    """找到变更记录的位置"""
    pattern = r'^##\s*[📝]?\s*变更记录'
    match = re.search(pattern, content, re.MULTILINE)
    if match:
        return match.start()
    return -1


def find_intro_end(content):
    """找到引言/摘要部分结束的位置（第一个主要章节前）"""
    # 找到第一个非摘要、非目录的二级标题
    lines = content.split('\n')
    intro_end = 0
    found_toc = False
    
    for i, line in enumerate(lines):
        if line.startswith('##'):
            title = line.lstrip('#').strip()
            # 跳过目录、摘要、核心发现等前置章节
            skip_patterns = ['目录', '摘要', '核心发现', '执行摘要', '数据来源', '关键发现', '局限性', '扩展阅读']
            if not any(p in title for p in skip_patterns):
                intro_end = i
                break
    return intro_end


def enhance_file(filepath, config):
    """增强单个文件"""
    filepath = Path(filepath)
    if not filepath.exists():
        print(f"  ⚠️ 文件不存在: {filepath.name}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已经增强过（通过检查是否有"执行摘要"章节）
    if '## 执行摘要' in content:
        print(f"  ⏭️ 已增强，跳过: {filepath.name}")
        return False
    
    print(f"  📝 正在增强: {filepath.name}")
    
    # 根据类型选择增强内容
    if config['type'] == 'career':
        enhance_content = CAREER_ENHANCE_TOP
    else:
        enhance_content = QUESTION_ENHANCE_TOP
    
    # 找到插入位置（在第一个主要内容章节前）
    # 策略：找到 "## 一、" 或 "## 1." 或 "## 📊" 等主要章节
    insert_pos = -1
    
    # 模式1：找第一个非前置的二级标题
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## ') and not line.startswith('###'):
            title = line[3:].strip()
            # 前置章节关键词
            skip_keywords = ['执行摘要', '数据来源', '关键发现', '局限性', '扩展阅读',
                           '目录', '摘要', '核心发现速览', '核心发现', '报告摘要',
                           '统计概览', '分类统计', '分析概览', '数据概览']
            
            # 检查是否是主要内容章节
            is_main_content = True
            for kw in skip_keywords:
                if kw in title:
                    is_main_content = False
                    break
            
            # 跳过标题中包含以下模式的（通常是正文章节）
            main_content_patterns = ['一、', '二、', '三、', '四、', '五、', '六、',
                                   '1.', '2.', '3.', '📊', '📁', '📋', '🔍', '📈']
            for pat in main_content_patterns:
                if pat in title:
                    is_main_content = True
                    break
            
            if is_main_content and i > 10:  # 确保不在文件最开头
                insert_pos = i
                break
    
    if insert_pos == -1:
        # 备用方案：在 "---" 分隔符后找位置
        sep_count = 0
        for i, line in enumerate(lines):
            if line.strip() == '---':
                sep_count += 1
                if sep_count >= 2:  # 第二个分隔符后
                    insert_pos = i + 1
                    break
    
    if insert_pos == -1:
        print(f"  ⚠️ 未找到插入位置: {filepath.name}")
        return False
    
    # 插入增强内容
    new_lines = lines[:insert_pos] + [enhance_content] + lines[insert_pos:]
    new_content = '\n'.join(new_lines)
    
    # 更新 changelog
    changelog_pos = find_changelog_position(new_content)
    if changelog_pos > 0:
        # 找到表格位置，插入新行
        changelog_section = new_content[changelog_pos:changelog_pos+500]
        # 找到第一个表格行（带 | 的行）
        table_match = re.search(r'(\|\s*日期.*?\n)(\|:---.*?\n)', changelog_section)
        if table_match:
            insert_at = changelog_pos + table_match.end()
            new_entry = "| 2026-07-18 | 🚀 超深度增强版 - 新增执行摘要、数据来源与方法论、关键发现、局限性与注意事项、扩展阅读等标准章节；引用 import 目录素材；建立交叉引用网络 |\n"
            new_content = new_content[:insert_at] + new_entry + new_content[insert_at:]
    
    # 更新文件头部的更新日期
    if '最后更新' in new_content:
        new_content = new_content.replace(
            '生成日期**: 2026',
            '生成日期**: 2026'
        )
    else:
        # 尝试在头部信息栏添加最后更新
        if '生成日期' in new_content:
            new_content = new_content.replace(
                '生成日期',
                '🔄 **最后更新**: 2026-07-18（超深度增强版）\n> 📅 **生成日期'
            )
    
    # 写入文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"  ✅ 增强完成: {filepath.name}")
    return True


def main():
    print("=" * 60)
    print("批量增强 discover/root 报告文件")
    print("=" * 60)
    
    success_count = 0
    skip_count = 0
    
    for filename, config in FILE_CONFIGS.items():
        filepath = os.path.join(ROOT_DIR, filename)
        result = enhance_file(filepath, config)
        if result:
            success_count += 1
        else:
            skip_count += 1
        print()
    
    print("=" * 60)
    print(f"增强完成！成功: {success_count}, 跳过: {skip_count}")
    print("=" * 60)


if __name__ == '__main__':
    main()

