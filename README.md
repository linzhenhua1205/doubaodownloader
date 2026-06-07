# 豆包批量导出工具 (全自动优化版)

> 基于 Selenium + DS随心转 插件的豆包对话批量导出工具，支持断点续传和智能去重

## 功能介绍

### 核心功能

1. **批量链接提取**：自动从 HTML 索引文件中提取豆包对话链接和标题
2. **智能去重机制**：
   - 精确标题匹配
   - 子串匹配
   - 相似度匹配（阈值 0.7）
   - 去除下划线后的匹配
3. **断点续传**：记录下载进度，支持中断后继续
4. **错误记录**：自动记录下载失败的链接，方便后续处理
5. **智能排序**：未匹配的链接优先下载，已匹配的按相似度排序后置

### 技术特点

- **双级去重**：第一级基于链接ID去重，第二级基于文件名匹配去重
- **多重触发机制**：DOM 点击优先，JS 内部调用兜底
- **状态检测**：实时检测批量模式状态、按钮状态、消息加载状态
- **错误恢复**：浏览器崩溃后自动重启，支持重新登录

## 系统要求

- Python 3.8+
- Google Chrome 浏览器（需对应版本的 ChromeDriver）
- DS随心转 浏览器插件

## 依赖安装

```bash
pip install selenium
```

## 文件结构

```
├── doubao_ds_sxz_auto_optimized.py  # 主程序
├── config.json                      # 配置文件（新增）
├── chrome-win64/                    # Chrome 浏览器目录
│   └── chrome.exe
├── chromedriver-win64/              # ChromeDriver 目录
│   └── chromedriver.exe
├── dssxz/                           # DS随心转插件目录
├── md/                              # 导出的 Markdown 文件目录
├── ai_md_exports/                   # 临时下载目录
├── chrome_profile/                  # Chrome 用户配置目录
├── 豆包链接索引.html                 # 链接索引文件
├── 豆包会话索引.html                 # 会话索引文件
├── download_progress.json           # 下载进度记录
└── export_errors.json               # 错误记录
```

## 配置文件

程序使用 `config.json` 文件进行配置管理。首次运行时，如果配置文件不存在，将自动创建默认配置。

### 配置项说明

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| chrome_path | `D:\123\md\chrome-win64\chrome-win64\chrome.exe` | Chrome 浏览器路径 |
| chromedriver_path | `D:\123\md\chromedriver-win64\chromedriver.exe` | ChromeDriver 路径 |
| extension_path | `D:\123\md\dssxz` | DS随心转插件路径 |
| download_dir | `D:\123\md\ai_md_exports` | 临时下载目录 |
| md_dir | `D:\123\md\md` | 最终 Markdown 存放目录 |
| chrome_profile_dir | `D:\123\md\chrome_profile` | Chrome 用户配置目录 |
| progress_path | `D:\123\md\download_progress.json` | 进度文件路径 |
| error_log_path | `D:\123\md\export_errors.json` | 错误日志路径 |
| index_html_files | `["豆包链接索引.html", "豆包会话索引.html"]` | 链接索引文件列表 |
| download_timeout | `10` | 下载超时时间（秒） |
| export_timeout | `5` | 导出超时时间（秒） |
| page_load_timeout | `8` | 页面加载超时时间（秒） |
| batch_mode_timeout | `3` | 批量模式激活超时时间（秒） |
| max_concurrent_downloads | `5000` | 最大并发下载数量 |

### 配置文件格式

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

## 使用方法

### 基本用法

```bash
python doubao_ds_sxz_auto_optimized.py
```

### 仅检查模式（不下载）

```bash
python doubao_ds_sxz_auto_optimized.py --check
```

该模式会输出统计信息，但不进行实际下载操作。

### 运行流程

1. **启动程序**：运行主脚本
2. **登录验证**：首次运行需要手动登录豆包账号
3. **链接提取**：从索引文件提取所有对话链接
4. **去重排序**：智能判断已下载内容，未匹配的优先处理
5. **批量下载**：自动打开每个对话并导出 Markdown
6. **进度记录**：成功后记录进度，失败则记录错误

## 工作原理

### 链接提取流程

```
HTML索引文件 → 正则匹配 → (link_id, title)列表 → 去重处理 → 排序输出
```

### 智能匹配算法

1. **精确匹配**：标题完全一致
2. **子串匹配**：规范化后的标题互为子串
3. **去下划线匹配**：去除下划线后匹配
4. **相似度匹配**：使用 `difflib.SequenceMatcher`，阈值 0.7

### 断点续传机制

```
加载进度文件 → 排除已完成ID → 文件名匹配检查 → 生成待处理列表
```

进度文件格式：
```json
{
  "123456789": {
    "title": "对话标题",
    "filename": "对话标题_20240101.md",
    "timestamp": "2024-01-01 10:30:00"
  }
}
```

## 导出步骤详解

### 步骤1：打开对话页面

访问 `https://www.doubao.com/chat/{link_id}`，等待页面加载完成。

### 步骤2：激活批量模式

派发自定义事件 `dssxz-toggle-batch-mode`，触发 DS随心转插件的批量操作模式。

### 步骤3：等待底部栏出现

等待 `dssxz-batch-bar-container`、`dssxz-select-all`、`dssxz-batch-export-container` 元素出现。

### 步骤4：等待消息收集完成

关键步骤，等待豆包 API 消息加载完成，通过 `dssxz-selected-count` 元素判断加载状态。

### 步骤5：全选对话

优先使用 DOM 点击方式，失败则调用 `_doubaoInstance.toggleSelectAll(true)`。

### 步骤6：导出 Markdown

点击 MD 导出按钮，或调用 `dssxzBatchUI.exportBatch("md")`。

### 步骤7：验证下载结果

检查下载目录中 MD 文件数量是否增加。

## 错误处理

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
| 批量模式未激活 | 插件未加载或版本不兼容 | 检查插件是否正确加载 |
| 底部栏未出现 | 页面加载超时 | 增加等待时间 |
| 全选失败 | 按钮不可点击 | 检查网络连接 |
| 导出超时 | 网络延迟或服务器问题 | 重新运行，断点续传会自动跳过已完成项 |

## 注意事项

1. **首次运行**：需要手动登录豆包账号，确保 DS随心转插件已启用
2. **浏览器配置**：使用指定的 Chrome 配置目录，保存登录状态
3. **网络稳定性**：建议在网络稳定的环境下运行，避免中断
4. **插件版本**：确保 DS随心转插件为最新版本
5. **文件权限**：确保下载目录有写入权限

## 日志说明

### 进度日志

程序会输出详细的处理进度：

```
============================================================
豆包批量导出工具 - 全自动优化版 (支持断点续传 + 智能排序)
============================================================
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

### 单条记录日志

```
[1/15] 处理对话: 123456789
  [HTML标题] 关于Python的学习笔记
  [步骤0] 打开对话页面
  [标题] 关于Python的学习笔记
  [步骤1] 派发批量模式事件
  [步骤2] 等待底部操作栏出现
  [步骤3.5] 等待豆包API消息加载完成 (关键步骤)...
  [OK] API消息加载完成! 计数: '共 25 条消息'
  [步骤3] 全选所有对话...
  [OK] DOM 方式全选成功
  [步骤3.5] 导出前MD文件数: 60
  [步骤4] 点击Markdown导出按钮...
  [OK] DOM 方式点击成功
  [步骤5] 等待导出完成...
  [OK] 导出完成
     ✓ 下载成功: 关于Python的学习笔记_20240101.md
  [记录] 已记录进度: 123456789 -> 关于Python的学习笔记
```

## 更新日志

### v1.0 (2024-01-01)
- 初始版本
- 支持基本的批量导出功能

### v2.0 (优化版)
- 新增智能去重机制
- 新增断点续传功能
- 新增相似度匹配算法
- 优化排序逻辑
- 增强错误处理

## License

MIT License
