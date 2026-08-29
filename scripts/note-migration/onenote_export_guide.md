# OneNote 导出指南（文本优先 + 附件清单化）

> OneNote ~100G 中，正文文本通常只占小部分，大头是附件/图片/嵌入文件。
> 策略：**文本全导出 + 附件只建清单按需取**，避免无谓下载 100G。

---

## 1. 先扫描构成（决定策略）

```bash
python3 onenote_scan.py "C:\Users\<用户名>\Documents\OneNote Notebooks" --csv onenote-attach.csv
```

- 若 `.one` 分区文件占大头 → 文本在分区内部，用客户端导出（见下）
- 若附件/媒体文件占大头 → 附件清单化，只在文档引用时下载

> 注意：OneNote 分区内嵌的图片/文件存在 `.one` 二进制内部，扫描不到。
> 真实构成以客户端导出时为准，扫描结果仅作粗估。

## 2. 文本导出（推荐顺序）

### 方案 A：OneNote 桌面客户端「导出」⭐ 最稳
1. 打开 OneNote → 选中笔记本/分区/页
2. 文件 → 导出 → 选择格式：
   - **Word 文档 (.docx)**：保真最好（表格/图片/层级都在）
   - **PDF**：只读归档用
3. 每个分区导出一个文件，按分区命名
4. 导出后用 `markdown-converter`（markitdown）批量转 Markdown

### 方案 B：OneNote Md Exporter（社区工具，适合批量）
- 项目: https://github.com/alxnbl/onenote-md-exporter
- 特点: 批量导出笔记本 → Markdown + 附件目录，保留层级
- 依赖: .NET，Windows 环境
- 注意: 表格/复杂排版可能简化，导出后抽样检查

### 方案 C：ConvertOneNote2MarkDown
- 项目: 社区工具，Windows + OneNote COM
- 适合: 需要保留更多格式细节时
- 知识库已有调研: `knowledge/05_tools/knowledge-management/2026-06-26-ai-knowledge-guide.md` 等

## 3. 附件处理

1. `onenote_scan.py --csv` 生成的清单就是附件目录（本地独立文件）
2. 分区内嵌附件：Md Exporter 会自动抽出到 `attachments/` 子目录
3. **不要全部下载/复制 100G**——只在迁移文档引用到某个附件时按清单定位
4. 高频引用附件（A 类）→ 复制到附件库（NAS/对象存储）
5. 低频附件 → 清单保留路径，原地不动

## 4. 导出后处理

```bash
# 统一补 frontmatter
python3 add_frontmatter.py import/migration/onenote --source onenote

# 去重
python3 dedup_scan.py import/migration/onenote --csv dedup-onenote.csv
```

## 5. 质量检查清单

- [ ] 每个分区都有导出文件，无遗漏
- [ ] 表格/图片/层级抽样比对通过
- [ ] 附件清单 CSV 生成
- [ ] 中文无乱码
- [ ] frontmatter 已补

## 风险提示

| 风险 | 对策 |
|:-----|:-----|
| 100G 全下载爆存储 | 只导文本；附件按需 |
| 表格转换丢失 | 方案 A (docx→markitdown) 保真最好 |
| 分区内嵌附件找不到 | 客户端导出时勾选包含附件/图片 |
| 导出超时 | 按笔记本分批，一次一个 |
