# 🛠️ 知识库工具与跟踪日志

> 本目录存放 **`tools/` 模块的跟踪日志** 和工具参考文档。
> **自动化管线脚本已迁移至 [`scripts/`](../scripts/) 目录**。

## 目录结构

```
knowledge/tools/          ← 跟踪日志 (.md) + 工具文档
├── README.md               # 本文件
├── TRACKING.md             # 跟踪框架
├── YYYY-MM-DD.md           # 每日跟踪日志
├── *.md                    # 专题报告/参考文档
└── golang/                 # Go 语言笔记

scripts/                  ← 可执行脚本
├── check_links.py           # 链接检测与修复
├── fix_index_links.py       # index.md URL编码修复
├── reformat_log.py          # log.md 格式重整
└── autokb/                  # 知识库自动化导入管线
    ├── run_pipeline.py       # CLI 入口
    ├── pipeline.py           # 主编排器
    ├── discover.py           # 文件发现
    ├── classify.py           # 内容分类
    ├── importer.py           # 导入管线
    ├── index_updater.py      # 索引更新
    └── config.py             # 全局配置
```

## 运行方式

```bash
# 从项目根目录 ~/cow 运行

# 链接检测
python3 scripts/check_links.py --file knowledge/notes/some-file.md

# 知识库导入管线
python3 scripts/autokb/run_pipeline.py --all
python3 scripts/autokb/run_pipeline.py --source doubao
python3 scripts/autokb/run_pipeline.py --dry-run
```
