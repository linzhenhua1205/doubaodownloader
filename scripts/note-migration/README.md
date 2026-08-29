# 多笔记系统迁移 — 执行手册（参考脚本集）

> **适用**: 8 套笔记系统（纸件/XML/OneNote/Markdown/AI文档/得到/飞书/cowagent）迁移整合
> **运行环境**: 用户本机（脚本均为 Python 3 标准库，跨平台，无需安装依赖）
> **状态**: 参考脚本 v1.0（2026-08-13），待用户拿数据后调试

---

## 🗺 执行总览

```
P0 盘点 → P1 批量转换 → P2 清洗去重 → P3 分类路由 → P4 索引重建 → P5 验证
```

**铁律**: 所有转换结果先进 `import/migration/` 暂存区，**不直接写入 knowledge/ 主结构**。

---

## 📜 脚本清单

| 脚本 | 用途 | 输入 → 输出 |
|:-----|:-----|:-----------|
| `xmind2md.py` | XMind 思维导图 → Markdown（新旧格式兼容） | .xmind → .md |
| `freemind2md.py` | FreeMind .mm → Markdown | .mm → .md |
| `text_xml2md.py` | 通用文本 XML → Markdown（inspect+config 两步） | .xml → .md |
| `onenote_scan.py` | OneNote 目录构成扫描（文本 vs 附件占比） | 目录 → 统计+CSV |
| `paper_index_card_gen.py` | 60 本纸件索引卡批量生成 | --count → NW-XXX.md |
| `add_frontmatter.py` | 批量补 frontmatter（source/migrated/value） | 目录 → 加头 |
| `dedup_scan.py` | 去重扫描（完全相同/标题相同/内容相似） | 目录 → 候选清单 |

---

## 🚀 分步执行

### P0 盘点（0.5-1 天）

1. 建迁移台账：复制 `manifest_template.md` 为 `import/migration/MANIFEST.md`，填各源数量/状态
2. 生成纸件索引卡：`python3 paper_index_card_gen.py --count 60 --out paper-index-cards`
   - 之后每周整理 2-3 本：封面信息 → 章节页码 → 关键事件 → A 类标注
3. 扫描 OneNote 构成：`python3 onenote_scan.py "C:\Users\xxx\Documents\OneNote Notebooks" --csv onenote-attach.csv`
   - 据此决定: 文本直接导出 vs 附件清单化

### P1 批量转换（1-2 天）

```bash
# XMind 200 个 (批量)
python3 xmind2md.py --dir /path/xmind --out import/migration/xmind

# 先 inspect 1 个确认格式
python3 xmind2md.py --inspect sample.xmind

# FreeMind 200 个 (批量)
python3 freemind2md.py --dir /path/freemind --out import/migration/freemind

# 文本 XML (先看结构)
python3 text_xml2md.py --inspect data.xml
# 然后写 cfg.json (见脚本头部说明), 再转换
python3 text_xml2md.py --config cfg.json --dir /path/xml --out import/migration/xml

# OneNote: 用桌面客户端导出文本 (见 onenote_export_guide.md)
# 飞书: 见 feishu_export_guide.md

# 给所有转换结果补 frontmatter
python3 add_frontmatter.py import/migration/xmind --source xmind
python3 add_frontmatter.py import/migration/freemind --source freemind
python3 add_frontmatter.py import/migration/xml --source xml
```

### P2 清洗去重（1-2 天）

```bash
python3 dedup_scan.py import/migration --csv dedup-candidates.csv
```

- 完全相同/标题相同 → 人工确认后保留最新
- 内容相似 ≥0.8 → 只标记，逐对人工判断（可能是一文多版本或多主题需拆分）
- 噪声清理: 空文件、纯导航、重复头尾

### P3 分类路由（1-2 天，人工核心环节）

按 `value` 分级路由到 knowledge/ 模块（参考 `knowledge/README.md` 模块说明）:

| value | 去向 |
|:------|:-----|
| A | 对应业务模块（02_rd/ 03_AI/ 05_tools/ 07_industry-research/ ...）精整理 |
| B | 对应模块带日期前缀归档 |
| C | 不迁移（转任务系统） |
| D | 冷归档（PDF 打包，不进知识库） |

格式规范遵循 `knowledge-wiki` 技能: TOC/交叉链接/changelog。

### P4 索引重建（0.5 天）

- `python3 scripts/tools/kb-global-index.py` 刷新 index.md
- `python3 scripts/tools/kb-log-append.py --file <草稿>` 批量追加 log.md

### P5 验证（0.5 天）

- `python3 scripts/check/format-validator.py <文件>`（逐个或批量）
- `python3 scripts/check/link-validator.py --file <文件>`
- **源系统冻结不删**，90 天后确认无误再清理

---

## ⚠️ 常见问题

| 问题 | 处理 |
|:-----|:-----|
| XMind 报"未找到 content.xml/json" | 先 `--inspect` 看内部结构；可能是 XMind Zen 特殊版本 |
| .mm 根标签不是 `<map>` | 可能不是 FreeMind；可能是 XMind 导出的 .mm（结构不同） |
| 文本 XML 结构复杂 | `--inspect` 逐层看；嵌套层级深时把 cfg 的 xpath 写具体 |
| OneNote 导出丢表格/嵌套 | 抽样比对；丢的附件在 CSV 清单中定位，按需补 |
| 中文乱码 | 确保文件是 UTF-8；GBK 的 XML 需先转码（`iconv -f GBK -t UTF-8`） |
| 去重误删风险 | dedup 只标记不删，合并前人工确认 |

---

## 📌 与 cowagent 知识库的对接

迁移完成后（或分批），把索引卡/精炼后的文档通过知识库三件套纪律归档：
1. 新建/修改文件 → 摘要写 tmp/ 草稿 → `kb-log-append.py` 追加 log.md
2. index.md/README.md 由 `kb-global-index.py` 批量刷新
3. 纸件索引卡建议统一放 `knowledge/04_person/`（或独立子目录）

## Changelog

- 2026-08-13 v1.0: 创建脚本集（xmind/freemind/text_xml 转换、onenote 扫描、索引卡生成、frontmatter、去重）
