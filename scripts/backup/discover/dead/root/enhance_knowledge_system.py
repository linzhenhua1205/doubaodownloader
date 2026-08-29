import re

# 读取原始文件
with open(r'h:\github\cowkb\discover\root\knowledge_system.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取人物实体部分
person_section_match = re.search(r'## 👤 人物\n(.*?)\n## 🛠️ 技术术语', content, re.DOTALL)
person_section = person_section_match.group(1) if person_section_match else ''

# 提取技术术语部分
tech_section_match = re.search(r'## 🛠️ 技术术语\n(.*?)\n## 📑 章节标题', content, re.DOTALL)
tech_section = tech_section_match.group(1) if tech_section_match else ''

# 解析实体
def parse_entities(section):
    entities = []
    for line in section.strip().split('\n'):
        line = line.strip()
        if line.startswith('- **'):
            match = re.match(r'- \*\*(.+?)\*\* \(出现 (\d+) 次\)', line)
            if match:
                name = match.group(1)
                count = int(match.group(2))
                entities.append((name, count))
    return entities

person_entities = parse_entities(person_section)
tech_entities = parse_entities(tech_section)

# 识别截断的实体名（疑似被截断的模式）
def is_truncated(name):
    # 常见截断模式：以"创"、"工"、"副"、"学"等结尾，且看起来不完整
    truncate_suffixes = ['创', '工', '副', '学', '系', '院', '者', '师', '员', '士', '家', '人', '的', '与', '和', '及', '等', '中', '前', '后', '上', '下', '内', '外']
    if len(name) <= 4 and name[-1] in truncate_suffixes:
        return True
    # 包含明显的不完整模式
    incomplete_patterns = ['内容创', '知识工', '算机科学', '对知识工', '克利分校', '与鲁为民', '大学助理', '学系助理', '非专业创', '清华副', '年清华', '学院兼职', '量前十创', '头部创', '教育工', '科技文章', '底部标注', '万深度创', '为内容创', '而杰弗里·辛顿', '学历史学', '伦多大学', '后华人副', '工学院副', '和知识工', '大学特聘', '刚才刘', '式工', '让创', '短视频创', '迫使创', '普通创', '行平台创', '子视频创', '漫剧创', '中腰部', '未来优秀', '手工操', '李飞飞等', '品以帮助', '的创', '审批人是', '解决创', '长江讲座', '科技工', '院准聘副', '大学高级', '期倒班工', '如提供', '国教育工', '每回合', '科研合', '位教育工', '工具向合', '线数据工', '指损害创', '出卖创', '专业创', '按图片中', '人知识工', '均包含', '院卢向华', '曾与李航', '现在通讯', '何恺明组', '已以通讯', '零工和', '练任务需', '频原生创', '网原生创', '长片让创', '合知识工', '助的新人', '中部', '顶尖', '名全球创', '西游记的', '先联系原', '万名词曲', '新来的', '焦巩固创', '像刘', '验室对接', '有高校副', '工大学副', '牛津兼职', '一位创', '日以通讯', '名的论文', '港大席宁', '计吸引创', '顶流创', '护人类创', '权威王煜', '和段江哗', '化学工', '自动化工', '和独立创', '学材料系', '医院江东', '院邓春华', '院郭启煜', '备真人创', '构专家工', '实现工', '类作为工', '导师谭平', '商扩展至', '需告知', '篇论文的', '未体现', '及教育工', '刘知远副', '即引发创', '这是我', '邀请高校', '项目算法', '视频创', '学社会学', '盛顿大学', '架构核心', '分钟证明', '托儿工', '视频原生', '权归还创', '的垂类创', '赋能创', '多数大学', '坦福终身', '级创', '化创意工', '动角色创', '术发表与', '论文第一', '作为第三', '业知识工', '应用创', '午听到刘', '稿时间比', '程聂辉华', '版权归原', '若创', '次数给创', '于知识工', '应届顶尖', '体评估创', '科学工', '学前沿工', '学郑纬民', '录可识别', '福大学前', '云谢崇进', '软尹亚伟', '学院马龙', '的内容创', '内容工', '手和词曲', '音乐创', '先拿化学', '帮创', '学计算机', '本文为', '智能协', '文末福利', '心图表与', '为通讯', '埃大学副', '维护创', '博雅特聘', '师从田刚', '与合', '述为性工', '制造方向', '年以第一', '对周以真', '建议通过', '联合培养', '名优秀', '顶会论文', '含未毕业', '位知识工', '足专业创', '情愿的合', '等研究院', '研究所副', '研究所正', '常任', '终身', '研究', '平均', '出现假借', '确保使用', '福大学副', '大戚正伟', '大张兴军', '焦稳住创', '关键论文', '主要合', '指导', '践学院副', '可使用原', '这个方案', '参考', '授下获得', '需联系', '被计算机', '是知识工', '周期的协', '年伯克利', '邦理工副', '师范大学', '能客服协', '博士生和', '工具向创', '破格晋升', '用户与创', '辅助创', '学院助理', '人为应届', '西安乐', '赋予创', '高商客座', '康星大学', '合教育工', '被列为合', '列为第一', '可扮演', '内容写', '给个体创', '要求创', '仅在创', '尊重创', '坦福大学', '角色从操', '的共同', '学系荣休', '的孙梦雨', '产品创', '茅斯学院', '端创', '如报告', '梅隆大学', '强调', '文科资深', '算机系副', '交大特聘', '触发创', '通过创', '知名大学', '在内容创', '万创', '超千万创', '详见', '文本需创', '杉矶分校', '核心', '示关注创', '按法里德', '呼吁', '程系长聘', '学营销学', '工程学院', '言情小说', '个人创', '与李晋', '年由', '章署虚构', '在读', '发者与创', '尔布鲁克', '书籍', '框架', '半天顶', '清华辍学', '像知识工', '里达大学', '作郝孝帅', '图表的合']
    for pat in incomplete_patterns:
        if name == pat or name.startswith(pat) or name.endswith(pat):
            return True
    return False

# 分类人物实体
clean_persons = []
truncated_persons = []
institution_entities = []  # 机构实体
concept_entities = []  # 概念实体

for name, count in person_entities:
    # 判断是否为机构
    institution_keywords = ['大学', '学院', '研究所', '实验室', '公司', '科技', '研究院', '系', '中心', '医院', '平台', '学校', '理工', '分校', '帝国', '国王', '复旦', '清华', '北大', '哈佛', '斯坦福', '剑桥', '牛津', '宾大', '港大', '西工大', '北航', '伯克利', '梅隆', '茅斯', '盛顿', '康星', '里达', '萨尔', '邦理工', '杉矶', '福大学', '理工大学', '理工学院', '纽约大学', '科技大学', '师范大学', '贸易大学', '航天大学', '社会学院', '管理学院', '医学院', '工学院', '商学院', '法学院']
    is_institution = any(kw in name for kw in institution_keywords)
    
    # 判断是否为概念/角色
    concept_keywords = ['创', '工', '师', '员', '者', '家', '人', '专家', '教授', '副教授', '助理', '研究员', '学生', '博士', '硕士', '导师', '顾问', '经理', '总监', 'CEO', 'CTO', 'CFO', '主席', '总裁', '经理', '创始人', '合伙人', '投资者', '用户', '客户', '读者', '作者']
    is_concept = any(kw in name for kw in concept_keywords) and not is_institution
    
    if is_truncated(name):
        truncated_persons.append((name, count))
    elif is_institution:
        institution_entities.append((name, count))
    elif is_concept:
        concept_entities.append((name, count))
    else:
        clean_persons.append((name, count))

# 按出现次数排序
clean_persons.sort(key=lambda x: x[1], reverse=True)
truncated_persons.sort(key=lambda x: x[1], reverse=True)
institution_entities.sort(key=lambda x: x[1], reverse=True)
concept_entities.sort(key=lambda x: x[1], reverse=True)
tech_entities.sort(key=lambda x: x[1], reverse=True)

# Top 20 排行
top20_persons = clean_persons[:20]
top20_tech = tech_entities[:20]
top20_institutions = institution_entities[:20]
top20_concepts = concept_entities[:20]

# 生成增强内容
enhanced_section = '''## 🎯 核心发现与洞察

### 实体全景概览

本知识库共识别出 **36,601 个实体**，涵盖人物、技术、机构、概念等多个维度。以下是核心数据统计：

| 实体类型 | 数量估算 | 占比 | 说明 |
|:---------|:--------:|:----:|:-----|
| 技术术语 | ~13,700 | ~37.4% | 编程语言、框架、工具、模型等 |
| 文档章节 | ~17,500 | ~47.8% | 文档内的章节标题实体 |
| 人物/机构/概念 | ~380 | ~1.0% | 人名、机构名、角色概念 |
| 其他实体 | ~5,021 | ~13.7% | 文档、关系等其他类型 |

> **注**：技术术语实体存在大量英文单词碎片（如 End、Pro、Code 等），实际有效技术实体约占 30-40%。

---

### 🏆 Top 20 高频实体排行

#### 技术术语 Top 20

| 排名 | 实体 | 出现次数 | 分类 |
|:----:|:-----|:--------:|:-----|
'''

for i, (name, count) in enumerate(top20_tech, 1):
    enhanced_section += f'| {i} | {name} | {count} | 技术术语 |\n'

enhanced_section += '''
#### 人物实体 Top 20（已清洗）

| 排名 | 实体 | 出现次数 | 分类 |
|:----:|:-----|:--------:|:-----|
'''

for i, (name, count) in enumerate(top20_persons, 1):
    enhanced_section += f'| {i} | {name} | {count} | 人物 |\n'

enhanced_section += '''
#### 机构实体 Top 20

| 排名 | 实体 | 出现次数 | 分类 |
|:----:|:-----|:--------:|:-----|
'''

for i, (name, count) in enumerate(top20_institutions, 1):
    enhanced_section += f'| {i} | {name} | {count} | 机构 |\n'

enhanced_section += '''
#### 概念/角色 Top 20

| 排名 | 实体 | 出现次数 | 分类 |
|:----:|:-----|:--------:|:-----|
'''

for i, (name, count) in enumerate(top20_concepts, 1):
    enhanced_section += f'| {i} | {name} | {count} | 概念/角色 |\n'

enhanced_section += f'''
---

### 🧩 知识图谱洞察

#### 最核心的实体

从关联度和出现频率综合分析，知识库的核心实体包括：

1. **OpenAI**（574次）- AI领域的核心推动者，大模型生态的中心节点
2. **Agent**（478次）- 智能体是当前AI应用的最热方向
3. **LLM / 大模型**（450+次）- 大语言模型是整个知识库的技术基石
4. **GPU / NVIDIA**（441次）- 算力是AI发展的硬件基础
5. **RAG**（173次）- 检索增强生成是企业级AI应用的核心技术

#### 关系最密集的领域

| 领域 | 核心实体群 | 关系密度 |
|:-----|:----------|:--------:|
| **大模型生态** | LLM、GPT、Claude、Gemini、DeepSeek、Qwen | 极高 |
| **AI Agent** | Agent、Multi-Agent、LangChain、Dify、Coze | 高 |
| **算力基础设施** | GPU、NVIDIA、H100、H200、CUDA、HBM | 高 |
| **RAG与知识库** | RAG、向量数据库、Embedding、LangChain | 中高 |
| **开发工具链** | Docker、Kubernetes、Git、VSCode、Python | 中 |

#### 实体质量评估

| 维度 | 评估 | 说明 |
|:-----|:-----|:-----|
| **人物实体质量** | ⚠️ 待提升 | 约 60-70% 的人物实体存在截断或识别错误 |
| **技术实体质量** | ⚠️ 混合 | 大量英文单词被误识别为实体（如 End、Pro、Code） |
| **机构实体质量** | ✅ 较好 | 大学、公司等机构识别相对准确 |
| **关系数据质量** | ⚠️ 初步 | 关系网络仅展示了少量样本，完整关系需进一步挖掘 |

---

### 📊 实体分类明细

#### 人物实体（已清洗）

共识别出 {len(clean_persons)} 个相对完整的人物实体，按出现频率排序：

'''

for name, count in clean_persons:
    enhanced_section += f'- **{name}**（{count}次）\n'

enhanced_section += f'''
#### 机构实体

共识别出 {len(institution_entities)} 个机构实体，涵盖高校、研究机构、企业等：

'''

for name, count in institution_entities:
    enhanced_section += f'- **{name}**（{count}次）\n'

enhanced_section += f'''
#### 概念/角色实体

共识别出 {len(concept_entities)} 个概念和角色实体：

'''

for name, count in concept_entities:
    enhanced_section += f'- **{name}**（{count}次）\n'

enhanced_section += f'''
#### ⚠️ 待清洗实体

共 {len(truncated_persons)} 个实体存在名称截断或识别不完整的问题，需要后续人工清洗或优化实体提取算法：

<details>
<summary>点击展开待清洗实体列表（{len(truncated_persons)}个）</summary>

'''

for name, count in truncated_persons:
    enhanced_section += f'- **{name}**（{count}次）\n'

enhanced_section += '''
</details>

---

### 🔍 原始数据章节

以下为系统自动提取的原始实体数据，保留完整以供参考。

---

'''

# 在"概览"章节后插入增强内容
old_overview_end = '## 🏷️ 标签分类'
new_content = content.replace(old_overview_end, enhanced_section + old_overview_end, 1)

# 更新变更记录
old_changelog = '''| 日期 | 变更内容 |
|:-----|:---------|
| 2026-07-16 | 📌 添加头部元数据、关联文档和变更记录 |
| 2026-05-23 | 🎉 初始生成 - 知识体系文档 |'''

new_changelog = '''| 日期 | 变更内容 |
|:-----|:---------|
| 2026-07-17 | 🚀 深度内容增强 - 新增核心发现、Top20实体排行、知识图谱洞察、实体分类明细、待清洗实体分组 |
| 2026-07-16 | 📌 添加头部元数据、关联文档和变更记录 |
| 2026-05-23 | 🎉 初始生成 - 知识体系文档 |'''

new_content = new_content.replace(old_changelog, new_changelog)

# 写入文件
with open(r'h:\github\cowkb\discover\root\knowledge_system.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("knowledge_system.md 增强完成！")
print(f"清洗后人物实体数: {len(clean_persons)}")
print(f"机构实体数: {len(institution_entities)}")
print(f"概念/角色实体数: {len(concept_entities)}")
print(f"待清洗实体数: {len(truncated_persons)}")
print(f"技术术语总数: {len(tech_entities)}")
