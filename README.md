# 豆包批量导出工具

> 🚀 基于 Selenium + DS随心转 插件的豆包对话批量导出工具，支持断点续传、智能去重和配置化管理

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Test Status](https://img.shields.io/badge/tests-passing-brightgreen)](test/)

需要自行保存豆包聊天历史记录条目的网页到本地，用于提取对话链接信息和标题信息。若无法解析保存下来的链接网页，需要重新调整下代码。

---

## 📋 功能特性

### 核心功能

| 功能 | 描述 |
|------|------|
| **批量链接提取** | 自动从 HTML 索引文件中提取豆包对话链接和标题 |
| **智能去重机制** | 支持精确匹配、子串匹配、相似度匹配（阈值 0.7）、去下划线匹配 |
| **断点续传** | 自动记录下载进度，支持中断后继续下载 |
| **错误记录** | 自动记录下载失败的链接，方便后续处理 |
| **智能排序** | 未匹配的链接优先下载，已匹配的按相似度排序后置 |
| **配置化管理** | 通过 `config.json` 集中管理所有路径和参数 |

### 技术亮点

- **双级去重**：第一级基于链接ID去重，第二级基于文件名匹配去重
- **多重触发机制**：DOM 点击优先，JS 内部调用兜底，提高稳定性
- **状态检测**：实时检测批量模式状态、按钮状态、消息加载状态
- **错误恢复**：浏览器崩溃后自动重启，支持重新登录

---

## 🛠️ 系统要求

- **Python**：3.8 及以上版本
- **浏览器**：Google Chrome（需对应版本的 ChromeDriver）
- **插件**：DS随心转 浏览器插件

---

## 📦 依赖安装

```bash
# 安装核心依赖
pip install selenium

# 运行单元测试（可选）
pip install pytest
```

---

## 📁 项目结构

```
doubaodownloader/
├── doubao_ds_sxz_auto_optimized.py  # 主程序
├── config.json                      # 配置文件
├── README.md                        # 项目文档
├── test/                            # 单元测试目录
│   ├── test_config.py               # 配置加载测试
│   └── test_utils.py                # 工具函数测试
├── chrome-win64/                    # Chrome 浏览器（需自行放置）
│   └── chrome.exe
├── chromedriver-win64/              # ChromeDriver（需自行放置）
│   └── chromedriver.exe
├── dssxz/                           # DS随心转插件（需自行放置）
├── md/                              # 最终 Markdown 文件存储目录
├── ai_md_exports/                   # 临时下载目录
├── chrome_profile/                  # Chrome 用户配置目录
├── 豆包链接索引.html                 # 链接索引文件（需自行创建）
├── 豆包会话索引.html                 # 会话索引文件（需自行创建）
├── download_progress.json           # 下载进度记录（自动生成）
└── export_errors.json               # 错误记录（自动生成）
```

---

## ⚙️ 配置文件

程序使用 `config.json` 文件进行集中配置管理。首次运行时，如果配置文件不存在，将自动创建默认配置。

### 配置项说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `chrome_path` | `D:\123\md\chrome-win64\chrome-win64\chrome.exe` | Chrome 浏览器可执行文件路径 |
| `chromedriver_path` | `D:\123\md\chromedriver-win64\chromedriver.exe` | ChromeDriver 可执行文件路径 |
| `extension_path` | `D:\123\md\dssxz` | DS随心转插件目录路径 |
| `download_dir` | `D:\123\md\ai_md_exports` | 临时下载目录 |
| `md_dir` | `D:\123\md\md` | 最终 Markdown 文件存放目录 |
| `chrome_profile_dir` | `D:\123\md\chrome_profile` | Chrome 用户配置目录（保存登录状态） |
| `progress_path` | `D:\123\md\download_progress.json` | 下载进度记录文件路径 |
| `error_log_path` | `D:\123\md\export_errors.json` | 错误日志文件路径 |
| `index_html_files` | `["豆包链接索引.html", "豆包会话索引.html"]` | 链接索引文件列表 |
| `download_timeout` | `10` | 下载超时时间（秒） |
| `export_timeout` | `5` | 导出操作超时时间（秒） |
| `page_load_timeout` | `8` | 页面加载超时时间（秒） |
| `batch_mode_timeout` | `3` | 批量模式激活超时时间（秒） |
| `max_concurrent_downloads` | `5000` | 单次最大下载数量限制 |

### 配置文件示例

```json
{
    "chrome_path": "D:\\123\\md\\chrome-win64\\chrome-win64\\chrome.exe",
    "chromedriver_path": "D:\\123\\md\\chromedriver-win64\\chromedriver.exe",
    "extension_path": "D:\\123\\md\\dssxz",
    "download_dir": "D:\\123\\md\\ai_md_exports",
    "md_dir": "D:\\123\\md\\md",
    "chrome_profile_dir": "D:\\123\\md\\chrome_profile",
    "progress_path": "D:\\123\\md\\download_progress.json",
    "error_log_path": "D:\\123\\md\\export_errors.json",
    "index_html_files": [
        "D:\\123\\md\\豆包链接索引.html",
        "D:\\123\\md\\豆包会话索引.html"
    ],
    "download_timeout": 10,
    "export_timeout": 5,
    "page_load_timeout": 8,
    "batch_mode_timeout": 3,
    "max_concurrent_downloads": 5000
}
```

---

## 🚀 使用方法

### 快速开始

```bash
# 1. 确保配置文件正确配置
# 2. 运行主程序
python doubao_ds_sxz_auto_optimized.py

# 3. 首次运行时，根据提示登录豆包账号
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--check` | 仅检查已下载链接数，不进行实际下载 |
| `--config <path>` | 指定自定义配置文件路径 |

### 使用示例

```bash
# 基本用法（使用默认配置文件）
python doubao_ds_sxz_auto_optimized.py

# 仅检查模式（查看统计信息，不下载）
python doubao_ds_sxz_auto_optimized.py --check

# 使用自定义配置文件
python doubao_ds_sxz_auto_optimized.py --config my_config.json
```

### 运行流程

1. **启动程序**：运行主脚本，自动加载配置文件
2. **登录验证**：首次运行需要手动登录豆包账号（后续使用保存的配置）
3. **链接提取**：从索引文件提取所有对话链接
4. **去重排序**：智能判断已下载内容，未匹配的优先处理
5. **批量下载**：自动打开每个对话并导出 Markdown
6. **进度记录**：成功后记录进度，失败则记录错误信息

---

## 🧠 工作原理

### 链接提取流程

```
HTML索引文件 → 正则匹配 → (link_id, title)列表 → 去重处理 → 智能排序 → 输出
```

### 智能匹配算法

1. **精确匹配**：标题完全一致
2. **子串匹配**：规范化后的标题互为子串
3. **去下划线匹配**：去除下划线后进行匹配
4. **相似度匹配**：使用 `difflib.SequenceMatcher`，相似度 ≥ 0.7 视为匹配

### 断点续传机制

```
加载进度文件 → 排除已完成ID → 文件名匹配检查 → 生成待处理列表
```

### 进度文件格式

```json
{
  "123456789": {
    "title": "对话标题",
    "filename": "对话标题_20240101.md",
    "timestamp": "2024-01-01 10:30:00"
  }
}
```

---

## 🔍 导出步骤详解

| 步骤 | 操作 | 说明 |
|------|------|------|
| 1 | 打开对话页面 | 访问 `https://www.doubao.com/chat/{link_id}` |
| 2 | 激活批量模式 | 派发 `dssxz-toggle-batch-mode` 自定义事件 |
| 3 | 等待底部栏出现 | 等待操作栏元素加载完成 |
| 4 | 等待消息收集 | 等待豆包 API 消息加载完成（关键步骤） |
| 5 | 全选对话 | 优先 DOM 点击，失败则调用 JS 方法 |
| 6 | 导出 Markdown | 点击 MD 导出按钮或调用 `dssxzBatchUI.exportBatch("md")` |
| 7 | 验证结果 | 检查下载目录中 MD 文件数量是否增加 |

---

## ❌ 错误处理

### 错误记录格式

```json
[
  {
    "link_id": "123456789",
    "url": "https://www.doubao.com/chat/123456789",
    "error": "批量模式无法激活",
    "timestamp": "2024-01-01 10:30:00"
  }
]
```

### 常见错误及解决方案

| 错误类型 | 可能原因 | 解决方案 |
|----------|----------|----------|
| 批量模式未激活 | 插件未加载或版本不兼容 | 检查插件是否正确加载，更新插件版本 |
| 底部栏未出现 | 页面加载超时 | 增加 `page_load_timeout` 配置值 |
| 全选失败 | 按钮不可点击 | 检查网络连接，刷新页面重试 |
| 导出超时 | 网络延迟或服务器问题 | 重新运行，断点续传会自动跳过已完成项 |

---

## ⚠️ 注意事项

1. **首次运行**：需要手动登录豆包账号，确保 DS随心转插件已启用
2. **浏览器配置**：使用指定的 Chrome 配置目录，可保存登录状态避免重复登录
3. **网络稳定性**：建议在网络稳定的环境下运行，避免下载中断
4. **插件版本**：确保 DS随心转插件为最新版本，以保证兼容性
5. **文件权限**：确保下载目录和配置目录有写入权限

---

## 📊 日志说明

### 进度日志示例

```
============================================================
豆包批量导出工具 - 全自动优化版 (支持断点续传 + 智能排序)
============================================================
[配置] 已从 config.json 加载配置
[配置] Chrome路径: D:\123\md\chrome-win64\chrome-win64\chrome.exe
[配置] 下载目录: D:\123\md\ai_md_exports
[配置] 索引文件数: 2
从 豆包链接索引.html 提取到 50 个链接
从 豆包会话索引.html 提取到 30 个链接
md 目录已有文件: 60 个
排序结果: 未匹配(优先) 15 个, 已匹配(后置) 5 个
第一级去重后: 75 个链接
进度文件标记完成: 55 个
文件名匹配已下载: 5 个
已完成(合计): 60 个, 待处理: 15 个
总进度: 60/75 (80.0%)
```

### 单条记录日志示例

```
[1/15] 处理对话: 123456789
  [HTML标题] 关于Python的学习笔记
  [步骤1/7] 打开对话页面
  [标题] 关于Python的学习笔记
  [步骤2/7] 激活批量模式
  [步骤3/7] 等待底部操作栏出现
  [步骤4/7] 等待消息加载完成
  [OK] API消息加载完成! 计数: '共 25 条消息'
  [步骤5/7] 全选对话内容
  [OK] DOM 方式全选成功
  [步骤6/7] 执行MD导出 (当前目录文件数: 60)
  [OK] DOM 方式点击成功
  [步骤7/7] 等待导出完成
  [OK] 导出完成
     ✓ 下载成功: 关于Python的学习笔记_20240101.md
  [记录] 已记录进度: 123456789 -> 关于Python的学习笔记
```

---

## 🧪 单元测试

项目包含完整的单元测试套件，确保核心功能的正确性。

```bash
# 运行所有测试
python -m pytest test/ -v

# 运行特定测试文件
python -m pytest test/test_config.py -v
python -m pytest test/test_utils.py -v
```

### 测试覆盖

| 测试文件 | 测试内容 | 测试用例数 |
|----------|----------|------------|
| `test_config.py` | 配置加载、合并、验证 | 6 |
| `test_utils.py` | 链接提取、标题规范化、排序 | 10 |

---

## 📝 更新日志

### v2.1（配置化优化版）
- ✅ 新增 `config.json` 配置文件支持
- ✅ 所有路径参数化，支持自定义配置
- ✅ 优化步骤标号显示（`[步骤1/7]` 格式）
- ✅ 新增单元测试套件
- ✅ 更新 README.md 文档

### v2.0（优化版）
- ✅ 新增智能去重机制
- ✅ 新增断点续传功能
- ✅ 新增相似度匹配算法
- ✅ 优化排序逻辑
- ✅ 增强错误处理

### v1.0（初始版本）
- ✅ 支持基本的批量导出功能
- ✅ 支持链接提取和去重
- ✅ 支持错误记录

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

*项目维护中，如有问题请提交 Issue*
