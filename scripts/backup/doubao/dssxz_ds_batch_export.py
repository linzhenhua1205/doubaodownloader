"""
DS随心转(DSSXZ) 插件 — 批量Markdown导出 Selenium 自动化脚本

功能：在 DeepSeek 对话页面，通过 DS 随心转插件执行：批量导出 → 全选 → Markdown导出

深度分析基于 p/h:/github/md/dssxz/ 目录下的插件源码。
"""

import time
import os
import json
import glob
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ═══════════════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════════════
CHROME_PROFILE = os.path.join(os.path.dirname(__file__), "chrome_profile")
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
DEEPSEEK_CHAT_URL = "https://chat.deepseek.com/"  # 替换为具体对话URL

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ═══════════════════════════════════════════════════════════════════════
# 插件结构深度分析 (基于源码逆向)
# ═══════════════════════════════════════════════════════════════════════
"""
┌──────────────────────────────────────────────────────────────┐
│ 插件架构总览                                                  │
├──────────────────────────────────────────────────────────────┤
│ manifest.json (V3)                                           │
│   权限: scripting, tabs, activeTab, storage, downloads, ...  │
│   匹配域: chat.deepseek.com, chatgpt.com, kimi.com, ...共8个   │
│   content_scripts 注入:                                       │
│     → js/content.js         (弹窗管理 + 事件绑定)             │
│     → js/batch-manager.js   (批量模式UI管理器)                │
│     → js/platforms/deepseek.js (DeepSeek平台适配)            │
│     → js/fiber-reader.js    (React Fiber树读取)              │
│     → dist/content.bundle.js (打包核心 ~156KB)               │
├──────────────────────────────────────────────────────────────┤
│ 核心类:                                                       │
│   BatchUIManager     — 批量模式底部栏 + 右侧侧边栏             │
│   DeepSeekPlatform   — DS平台适配, 管理批量模式状态机          │
│   I18nManager        — 国际化                                 │
├──────────────────────────────────────────────────────────────┤
│ API 通信:                                                     │
│   background.js → fetch("/v11/convert-all") → dssxz.com      │
│   action: "convertBatch" 发送 batchHtmlContent/markdownContent │
│   返回: {success, data: {url}} → chrome.downloads.download()  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 批量导出流程 (源码级别)                                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [1] 触发批量模式                                             │
│      FAB按钮 (📋 "批量导出", id="dssxz-fab-batch")            │
│      → dispatchEvent(new CustomEvent("dssxz-toggle-batch-mode"))│
│      → DeepSeekPlatform.toggleBatchMode()                    │
│      → this.enableBatchUI()                                  │
│                                                              │
│  [2] 进入批量模式后:                                           │
│      → batchUI.createBatchBar(darkMode)                      │
│      → batchUI.createSidebar()                               │
│      → injectBatchModeStyles()  (隐藏工具栏)                   │
│      → 底部栏出现 (position:fixed, bottom:0, z-index:2147483647)│
│                                                              │
│  [3] 底部栏 DOM 结构 (renderBottomBarContent):                │
│      #dssxz-batch-bar-container                              │
│        └─ #dssxz-batch-inner                                 │
│             ├─ [左侧]                                         │
│             │   ├─ input#dssxz-select-all (type=checkbox)     │
│             │   ├─ label[for="dssxz-select-all"] "全选"      │
│             │   ├─ span#dssxz-selected-count "已选择 0 条对话"│
│             │   └─ (可选) input#dssxz-include-timestamp +    │
│             │              label "含发送时间"                  │
│             └─ [右侧]                                         │
│                 ├─ button "取消"                              │
│                 └─ #dssxz-batch-export-container             │
│                      ├─ [Word] dssxz-split-button-wrapper     │
│                      │   data-type="word"                     │
│                      │   data-dssxz-tooltip="导出 Word"       │
│                      ├─ [PDF] dssxz-split-button-wrapper     │
│                      │   data-type="pdf"                      │
│                      │   data-dssxz-tooltip="导出 PDF"        │
│                      └─ [MD] div                              │
│                          data-type="md"                       │
│                          data-dssxz-tooltip="导出Markdown（免费）"│
│                                                              │
│  [4] 全选: 点击 #dssxz-select-all                             │
│      → onchange → onSelectAll(true)                          │
│      → DeepSeekPlatform.toggleSelectAll(true)                │
│      → 遍历所有消息块 → selectedMessages.add(block)           │
│      → refreshBatchCheckboxes()                              │
│                                                              │
│  [5] Markdown导出: 点击 data-type="md" 按钮                   │
│      → onExport("md", null)                                  │
│      → exportBatch(selectedMessages, config, "md")           │
│      → _performBatchExport() (或 _exportFromVirtualListCache)│
│      → _sendExportRequest(htmlContent, config, "md")         │
│      → chrome.runtime.sendMessage({                          │
│          action: "convertBatch",                             │
│          platform: "deepseek",                               │
│          convertType: "md",                                  │
│          batchHtmlContent: "<html>..."                        │
│        })                                                    │
│      → background.js 处理, POST /v11/convert-all             │
│      → 返回下载URL → chrome.downloads.download({url})        │
│      → setExportLoading("md", false) → 旋转SVG消失            │
│      → toggleBatchMode() → 退出批量模式                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 图标对应关系                                                   │
├──────────────────────────────────────────────────────────────┤
│ Word:  SVG path="M531.285 85.333..." (文档+W标识)             │
│        tooltip="导出 Word"                                    │
│ PDF:   SVG path="M531.3 574.4..." (PDF文档图标)               │
│        tooltip="导出 PDF"                                     │
│ MD:    SVG path="M590.222222 73.955556..." (Markdown文件图标) │
│        tooltip="导出Markdown（免费）"                           │
│ Excel: SVG path="M640.128 64.426667..." (绿色Excel图标)       │
│ Image: SVG path="M819.2 96..." (图片图标)                      │
│ 全选:  checkbox input#dssxz-select-all + label "全选"        │
│ 取消:  <button>取消</button>                                   │
│ 加载:  SVG circle 旋转动画 (@keyframes dssxz-spin)            │
│        蓝色 (#2563EB) 圆形旋转指示器                            │
│                                                              │
│ 侧边栏标记: 蓝色(#3b82f6)选中态 / 灰色(#d1d5db)未选中态       │
│            右侧固定定位(right:8%), 圆柱形标记                   │
└──────────────────────────────────────────────────────────────┘
"""


# ═══════════════════════════════════════════════════════════════════════
# CSS Selectors 参考表 (来自源码)
# ═══════════════════════════════════════════════════════════════════════
SELECTORS = {
    # === FAB 悬浮按钮 (由 content.bundle.js 中的 addFloatingButton 创建) ===
    "fab_container": "div[style*='position: fixed'][style*='z-index']",  # FAB容器
    "fab_batch_btn": "#dssxz-fab-batch",  # 批量导出按钮 (📋 icon + "批量导出"文字)

    # === DeepSeek 页面元素 ===
    "ds_textarea": "textarea",
    "ds_messages": ".ds-markdown",
    "ds_virtual_list": ".ds-virtual-list",

    # === 批量模式底部栏 (由 batch-manager.js 的 createBatchBar 创建) ===
    "batch_bar": "#dssxz-batch-bar-container",  # 底部批量操作栏容器
    "batch_inner": "#dssxz-batch-inner",  # 底部栏内部元素
    "select_all": "#dssxz-select-all",  # 全选复选框
    "select_all_label": "label[for='dssxz-select-all']",  # "全选" 标签
    "selected_count": "#dssxz-selected-count",  # 已选择计数
    "include_timestamp": "#dssxz-include-timestamp",  # "含发送时间" 可选
    "cancel_btn": "button",  # 取消按钮 (需在batch_inner中查找 textContent="取消")
    "export_container": "#dssxz-batch-export-container",  # 导出按钮容器

    # === 导出按钮 ===
    # Word: .dssxz-split-button-wrapper[data-type="word"]  或 .dssxz-btn-word
    # PDF:  .dssxz-split-button-wrapper[data-type="pdf"]   或 .dssxz-btn-pdf
    # MD:   div[data-type="md"] (非split-button, 简单div, 免费功能)
    "export_btn_word": '[data-type="word"]',
    "export_btn_pdf": '[data-type="pdf"]',
    "export_btn_md": '[data-type="md"]',

    # === 导出加载中 ===
    "spin_style": "#dssxz-spin-style",  # 旋转动画CSS
    "loading_svg": 'svg[viewBox="0 0 24 24"]',  # 加载时替换按钮内容的旋转SVG

    # === 侧边栏导航 ===
    "sidebar": "#dssxz-sidebar",
    "sidebar_markers": ".dssxz-nav-cylinder-marker",
    "sidebar_tooltip": "#dssxz-sidebar-tooltip",

    # === 导出完成/退出批量模式 ===
    "batch_active": ".dssxz-batch-active",  # body 上的 class
    "msg_checkbox": ".dssxz-msg-checkbox",  # 每行消息的浮动复选框

    # === 弹窗 (popup) ===
    "popup_export_word": "#export-all-word",
    "popup_export_pdf": "#export-all-pdf",
    "popup_export_md": "#export-all-md",
}


# ═══════════════════════════════════════════════════════════════════════
# 核心自动化类
# ═══════════════════════════════════════════════════════════════════════
class DSSXZBatchExporter:
    """
    DS随心转 批量导出自动化

    流程对标插件源码的完整链路:
      FAB按钮 → CustomEvent("dssxz-toggle-batch-mode")
              → DeepSeekPlatform.toggleBatchMode()
              → enableBatchUI()
                → batchUI.createBatchBar()
                → batchUI.createSidebar()
              → 用户点击全选 → toggleSelectAll(true)
              → 用户点击MD导出 → exportBatch() → _performBatchExport()
                → chrome.runtime.sendMessage({action:"convertBatch"})
                → background.js → fetch POST /v11/convert-all
                → chrome.downloads.download({url})
    """

    def __init__(self, profile_dir=None, headless=False):
        self.download_dir = DOWNLOAD_DIR
        self.profile_dir = profile_dir or CHROME_PROFILE

    def init_driver(self):
        """初始化 Chrome WebDriver (连接已安装插件的 profile)"""
        opts = webdriver.ChromeOptions()
        # 使用已有 Chrome profile (含已安装的 DSSXZ 插件)
        if os.path.isdir(self.profile_dir):
            opts.add_argument(f"user-data-dir={self.profile_dir}")

        # 下载配置
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        opts.add_experimental_option("prefs", prefs)

        # 禁用自动化检测
        opts.add_argument("--disable-blink-features=AutomationControlled")
        opts.add_exclusion_keys(["enable-automation"])
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")

        # 保持浏览器打开（不用detach，用persistent profile即可）
        # 窗口大小
        opts.add_argument("--window-size=1440,900")

        self.driver = webdriver.Chrome(options=opts)
        self.wait = WebDriverWait(self.driver, 15)
        self.long_wait = WebDriverWait(self.driver, 30)
        self.short_wait = WebDriverWait(self.driver, 5)
        return self.driver

    # ═══════════════════════════════════════════════════════════════
    # 第1步: 导航到 DeepSeek 对话页面, 等待插件注入完成
    # ═══════════════════════════════════════════════════════════════
    def navigate_to_chat(self, chat_url=None):
        """
        导航到 DeepSeek 对话页面。
        对应源码:
          deepseek.js 末尾自执行:
            const t = () => {
              if (document.querySelector("textarea") || document.querySelector("#root")) {
                window[dssxz_deepseek_platform_instance] = new DeepSeekPlatform
                window[instance].init({platformId:"deepseek", ...})
              } else setTimeout(t, 200)
            }
            setTimeout(t, 500)
        """
        url = chat_url or DEEPSEEK_CHAT_URL
        self.driver.get(url)
        print(f"[导航] {url}")

        # 等待插件 content script 注入并初始化 DeepSeekPlatform
        # 条件: textarea 或 #root 存在 + .ds-markdown 消息渲染
        time.sleep(3)  # 让页面先加载
        try:
            self.long_wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
            )
            print("[OK] DeepSeek 页面就绪 (textarea found)")
        except TimeoutException:
            print("[WARN] textarea 未找到, 尝试 #root")
            self.long_wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#root"))
            )
            print("[OK] DeepSeek 页面就绪 (#root found)")

        # 等待 .ds-markdown 消息出现 (确保对话内容已渲染)
        try:
            self.long_wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ds-markdown"))
            )
            print("[OK] 对话内容已渲染 (.ds-markdown found)")
        except TimeoutException:
            print("[WARN] .ds-markdown 未出现, 可能页面无对话内容或需要滚动")

        # 额外等待插件初始化 (DeepSeekPlatform.startPlugin → 1.5s polling)
        time.sleep(3)
        print("[OK] 等待插件初始化完成")

    # ═══════════════════════════════════════════════════════════════
    # 第2步: 点击 FAB 悬浮按钮 "📋 批量导出"
    # ═══════════════════════════════════════════════════════════════
    def click_batch_export_fab(self):
        """
        定位并点击悬浮按钮中的"批量导出"。
        对应源码:
          content.bundle.js → addFloatingButton:
            l = a("📋","批量导出", () => {
              window.dispatchEvent(new CustomEvent("dssxz-toggle-batch-mode"))
            }, {id: "dssxz-fab-batch"})

          → deepseek.js:
            window.addEventListener("dssxz-toggle-batch-mode", () => {
              this.toggleBatchMode()
            })
            → enableBatchUI() → batchUI.createBatchBar() + batchUI.createSidebar()
        """
        print("\n[步骤2] 点击 FAB 批量导出按钮...")

        # 策略A: 直接通过 id 定位
        try:
            batch_btn = self.long_wait.until(
                EC.element_to_be_clickable((By.ID, "dssxz-fab-batch"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", batch_btn)
            batch_btn.click()
            print("  [OK] 通过 #dssxz-fab-batch 点击成功")
        except TimeoutException:
            print("  [策略A] #dssxz-fab-batch 未找到, 尝试策略B")

            # 策略B: 通过文本内容查找 FAB 按钮
            try:
                # FAB 是固定定位的 div, 包含多个按钮
                fab_btns = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "div[style*='position: fixed'] div[style*='cursor: pointer']"
                )
                for btn in fab_btns:
                    text = btn.text.strip()
                    if "批量导出" in text or "📋" in text:
                        btn.click()
                        print(f"  [OK] 通过文本 '{text}' 点击成功")
                        break
                else:
                    raise Exception("FAB 批量导出按钮未找到")
            except Exception as e:
                print(f"  [策略B] 失败: {e}, 尝试策略C")

                # 策略C: 直接派发 CustomEvent (最可靠)
                print("  [策略C] 直接派发 dssxz-toggle-batch-mode 事件")
                self.driver.execute_script(
                    "window.dispatchEvent(new CustomEvent('dssxz-toggle-batch-mode'))"
                )
                print("  [OK] CustomEvent 已派发")

    # ═══════════════════════════════════════════════════════════════
    # 第3步: 等待底部批量操作栏出现
    # ═══════════════════════════════════════════════════════════════
    def wait_for_batch_bar(self):
        """
        等待底部批量操作栏渲染完成。
        对应源码:
          BatchUIManager.createBatchBar():
            t.id = "dssxz-batch-bar-container"
            t.style.cssText = "position: fixed; bottom: 0; ...z-index: 2147483647;"
            document.body.appendChild(t)
            this.renderBottomBarContent(t, darkMode)
        """
        print("\n[步骤3] 等待底部批量操作栏...")
        try:
            bar = self.long_wait.until(
                EC.presence_of_element_located((By.ID, "dssxz-batch-bar-container"))
            )
            print("  [OK] 底部栏已创建: #dssxz-batch-bar-container")

            # 等待内部元素渲染
            self.wait.until(
                EC.presence_of_element_located((By.ID, "dssxz-batch-inner"))
            )
            print("  [OK] 内部元素渲染: #dssxz-batch-inner")

            # 等待全选复选框出现
            self.wait.until(
                EC.presence_of_element_located((By.ID, "dssxz-select-all"))
            )
            print("  [OK] 全选复选框就绪: #dssxz-select-all")

            # 等待导出按钮容器出现
            self.wait.until(
                EC.presence_of_element_located(
                    (By.ID, "dssxz-batch-export-container")
                )
            )
            print("  [OK] 导出按钮容器就绪: #dssxz-batch-export-container")

            # 验证 "全选" 标签文本
            label = self.driver.find_element(
                By.CSS_SELECTOR, "label[for='dssxz-select-all']"
            )
            print(f"  [验证] 全选标签文本: '{label.text}'")

            # 验证已选择计数
            count = self.driver.find_element(By.ID, "dssxz-selected-count")
            print(f"  [验证] 初始计数: '{count.text}'")

            # 额外等待侧边栏创建
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.ID, "dssxz-sidebar"))
                )
                print("  [OK] 右侧导航侧边栏已创建")
            except TimeoutException:
                print("  [INFO] 侧边栏未立即出现 (正常, 异步创建)")

            return True
        except TimeoutException as e:
            print(f"  [FAIL] 底部栏超时: {e}")
            # 检查 body 是否有 batch-active class
            body_class = self.driver.execute_script(
                "return document.body.className"
            )
            print(f"  [DEBUG] body.className = '{body_class}'")
            return False

    # ═══════════════════════════════════════════════════════════════
    # 第3.5步: 等待消息收集完成 (关键!)
    # ═══════════════════════════════════════════════════════════════
    def wait_for_collection_complete(self, timeout=60):
        """
        等待 collectAllVirtualListMessages() 异步执行完成。
        这是最关键的步骤 — 如果不等待, 全选会因 isCollecting=true 而失效。

        源码分析 (3处竞态):
          1. collectAllVirtualListMessages() 中:
               this.isCollecting = true
               this.virtualListCache.clear()       ← 清空!
               await collectMessagesFromFiber()    ← 异步 3s
               ... 填充 virtualListCache ...
               this.isCollecting = false

          2. toggleSelectAll() 中:
               virtualListCache.size>0 → 用缓存键选择  ← 缓存为空, 跳过!
               fiberDataAvailable || getPotentialMessages() → DOM扫描

          3. refreshBatchCheckboxes() 中:
               if (this.isCollecting) return;  ← 🔴 直接返回, UI不更新!

          4. updateBatchUIState() 完成后:
               selectAllCheckbox.checked =
                 selectedVirtualKeys.size === virtualListCache.size
               ← Fiber键 != DOM键 → 永远不勾选!

        结论:
          - 必须在 isCollecting=false 之后操作
          - 必须用 JS 直接调用平台实例的 toggleSelectAll(true),
            不能依赖DOM复选框的onchange事件

        检测完成标志:
          - JS: isCollecting === false && virtualListCache.size > 0
          - DOM: #dssxz-selected-count 文本不再包含 "正在读取" / "扫描中"
        """
        print("\n[步骤3.5] 等待消息收集完成 (关键步骤)...")
        start = time.time()
        while time.time() - start < timeout:
            is_collecting = self.driver.execute_script("""
                var key = Object.keys(window).find(k => k.startsWith('dssxz_deepseek'));
                var platform = key ? window[key] : null;
                if (!platform) return 'no_platform';
                return JSON.stringify({
                    isCollecting: platform.isCollecting,
                    virtualListCacheSize: platform.virtualListCache ? platform.virtualListCache.size : 0,
                    fiberDataAvailable: platform.fiberDataAvailable,
                    selectedVirtualKeysSize: platform.selectedVirtualKeys ? platform.selectedVirtualKeys.size : 0,
                    selectedMessagesSize: platform.selectedMessages ? platform.selectedMessages.size : 0
                });
            """)

            try:
                info = json.loads(is_collecting)
            except (json.JSONDecodeError, TypeError):
                time.sleep(1)
                continue

            if info == 'no_platform':
                print("  [WARN] 平台实例未找到, 等待中...")
                time.sleep(2)
                continue

            elapsed = int(time.time() - start)
            status = "收集" if info['isCollecting'] else "完成"

            # 显示进度
            count_el = None
            try:
                count_el = self.driver.find_element(By.ID, "dssxz-selected-count")
                count_text = count_el.text
            except Exception:
                count_text = "?"

            print(f"  [{elapsed}s] isCollecting={info['isCollecting']}, "
                  f"cacheSize={info['virtualListCacheSize']}, "
                  f"fiber={info['fiberDataAvailable']}, "
                  f"count='{count_text}'")

            if not info['isCollecting'] and info['virtualListCacheSize'] > 0:
                print(f"  [OK] 消息收集完成! 共 {info['virtualListCacheSize']} 条消息")
                self._collection_info = info
                return True

            if not info['isCollecting']:
                # isCollecting=false 但 cache为空 → 可能Fiber失败, 降级到DOM
                print(f"  [WARN] 收集结束但 virtualListCache 为空, "
                      f"fiberDataAvailable={info['fiberDataAvailable']}")
                print(f"  [INFO] 将使用 getPotentialMessages() DOM扫描模式 (selectedMessages)")
                self._collection_info = info
                return True

            time.sleep(2)

        print(f"  [WARN] 等待超时 ({timeout}s), 继续尝试...")
        self._collection_info = None
        return False

    # ═══════════════════════════════════════════════════════════════
    # 第4步: 全选 (必须等待收集完成后执行)
    # ═══════════════════════════════════════════════════════════════
    def click_select_all(self):
        """
        全选所有消息。必须在 wait_for_collection_complete() 之后调用。

        🔴 为什么不能直接点 DOM 复选框:
          - isCollecting=true 时 refreshBatchCheckboxes() 直接 return
          - collection 完成后 updateBatchUIState() 比较
            selectedVirtualKeys.size === virtualListCache.size
            但两者键来自不同源(Fiber vs DOM), 永远不相等 → 复选框永远不勾选

        ✅ 正确做法: 通过 JS 直接找到 DeepSeekPlatform 实例,
           调用 toggleSelectAll(true), 然后手动触发 UI 刷新。

        源码路径:
          window["dssxz_deepseek_platform_instance"]  ← 平台实例
            .toggleSelectAll(true)
            .refreshBatchCheckboxes()
        """
        print("\n[步骤4] 全选所有对话...")

        # 核心修复: 通过平台实例直接操作, 不依赖DOM复选框的onchange
        result = self.driver.execute_script("""
            // 找到 DeepSeekPlatform 实例
            var key = Object.keys(window).find(k => k.startsWith('dssxz_deepseek'));
            var platform = key ? window[key] : null;
            if (!platform) return 'no_platform';

            // 等待 isCollecting 变为 false
            if (platform.isCollecting) {
                return 'still_collecting';
            }

            // 直接调用 toggleSelectAll(true)
            platform.toggleSelectAll(true);

            // 强制刷新UI (因为 toggleSelectAll 内部的 refreshBatchCheckboxes
            // 可能在 isCollecting 状态变化时有竞态)
            if (!platform.isCollecting && !platform.isExporting) {
                platform.refreshBatchCheckboxes();
            }

            return JSON.stringify({
                virtualListCacheSize: platform.virtualListCache ? platform.virtualListCache.size : 0,
                selectedVirtualKeysSize: platform.selectedVirtualKeys ? platform.selectedVirtualKeys.size : 0,
                selectedMessagesSize: platform.selectedMessages ? platform.selectedMessages.size : 0,
                fiberDataAvailable: platform.fiberDataAvailable
            });
        """)

        print(f"  [JS返回] {result}")

        if result == 'no_platform':
            print("  [FAIL] 平台实例不存在")
            return False
        if result == 'still_collecting':
            print("  [FAIL] 消息仍在收集, 请先等待完成")
            return False

        try:
            info = json.loads(result)
        except (json.JSONDecodeError, TypeError):
            print(f"  [FAIL] 无法解析结果: {result}")
            return False

        selected_count = info['selectedVirtualKeysSize'] or info['selectedMessagesSize']
        total_count = info['virtualListCacheSize']
        print(f"  [OK] 已选择 {selected_count} / {total_count} 条消息")

        # 等待 UI 刷新
        time.sleep(1.5)

        # 验证DOM状态
        try:
            is_checked = self.driver.execute_script(
                "return document.getElementById('dssxz-select-all').checked"
            )
            count_text = self.driver.execute_script(
                "return document.getElementById('dssxz-selected-count').innerText"
            )
            print(f"  [验证] 复选框 checked={is_checked}, 计数='{count_text}'")

            # 如果复选框仍未勾选, 手动设置 (仅视觉反馈, 实际选中已在JS层完成)
            if not is_checked:
                print("  [INFO] 复选框视觉未更新, 手动设置 (实际选中状态已生效)")
                self.driver.execute_script("""
                    var cb = document.getElementById('dssxz-select-all');
                    if (cb) cb.checked = true;
                """)
        except Exception as e:
            print(f"  [INFO] DOM验证跳过: {e}")

        return selected_count > 0

    # ═══════════════════════════════════════════════════════════════
    # 第5步: 点击 Markdown 导出按钮
    # ═══════════════════════════════════════════════════════════════
    def click_markdown_export(self):
        """
        点击底部栏的 Markdown 导出按钮。
        对应源码:
          batch-manager.js renderBottomBarContent():
            if (window.exportUIManager) {
              const e = window.exportUIManager.createExportContainer({
                types: ["word", "pdf", "md"],
                onExport: (format, templateId) => {
                  this.callbacks.onExport(format, templateId === "default" ? null : templateId)
                }
              })
              p.appendChild(e)
            }

          createExportButton("md", ...):
            a.dataset.type = "md"
            a.dataset.dssxzTooltip = "导出Markdown（免费）"
            a.innerHTML = "MD" 的 SVG icon + 文字

          点击后触发链:
            onExport("md", null)
            → exportBatch(selectedMessages, config, "md")
            → _performBatchExport() 或 _exportFromVirtualListCache()
            → _sendExportRequest(htmlContent, config, "md")
            → chrome.runtime.sendMessage({action:"convertBatch", convertType:"md"})
            → setExportLoading("md", true)  → 显示旋转SVG
            → ... API调用 ...
            → setExportLoading("md", false) → 隐藏旋转SVG
            → toggleBatchMode() → 退出批量模式
        """
        print("\n[步骤5] 点击 Markdown 导出按钮...")

        # 定位 MD 导出按钮: div[data-type="md"]
        try:
            md_btn = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-type="md"]'))
            )
            print(f"  [定位] MD按钮 tooltip: '{md_btn.get_attribute('data-dssxz-tooltip')}'")

            # 检查是否可点击
            self.driver.execute_script("arguments[0].scrollIntoView(true);", md_btn)
            time.sleep(0.3)

            # 使用 JS 点击确保可靠
            self.driver.execute_script("arguments[0].click();", md_btn)
            print("  [OK] MD导出按钮已点击")

            # 验证: 加载动画是否出现 (旋转SVG)
            try:
                self.short_wait.until(
                    EC.presence_of_element_located((By.ID, "dssxz-spin-style"))
                )
                print("  [验证] 旋转加载动画CSS已注入 (#dssxz-spin-style)")
            except TimeoutException:
                print("  [INFO] 未检测到加载动画 (可能导出很快)")

            return True
        except TimeoutException:
            print("  [FAIL] MD导出按钮未找到")
            # 尝试通过 JS 直接调用
            print("  [Fallback] 尝试通过 JS 直接触发导出...")
            try:
                self.driver.execute_script("""
                    var btns = document.querySelectorAll('#dssxz-batch-export-container [data-type]');
                    for (var b of btns) {
                        if (b.dataset.type === 'md') {
                            b.click();
                            console.log('MD export triggered via JS');
                            break;
                        }
                    }
                """)
                print("  [OK] JS直接触发")
                return True
            except Exception as e:
                print(f"  [FAIL] JS触发也失败: {e}")
                return False

    # ═══════════════════════════════════════════════════════════════
    # 第6步: 等待下载完成
    # ═══════════════════════════════════════════════════════════════
    def wait_for_download(self, timeout=120):
        """
        等待下载完成。
        插件导出流程:
          1. setExportLoading("md", true) → 旋转SVG
          2. _performBatchExport() → 收集HTML
          3. chrome.runtime.sendMessage({action:"convertBatch", ...})
          4. background.js POST /v11/convert-all
          5. 返回 {success: true, data: {url: "..."}}
          6. chrome.downloads.download({url})
          7. setExportLoading("md", false)
          8. toggleBatchMode() → 退出批量模式
             → body.classList.remove("dssxz-batch-active")
             → batchUI.destroy()
             → dispatchEvent("dssxz-batch-mode-exited")
        """
        print(f"\n[步骤6] 等待下载完成 (最长 {timeout}s)...")

        # 等待批量模式退出 (body 移除 dssxz-batch-active class)
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: "dssxz-batch-active" not in d.execute_script(
                    "return document.body.className"
                )
            )
            print("  [OK] 批量模式已退出")
        except TimeoutException:
            print("  [WARN] 批量模式未在预期时间内退出")

        # 等待下载文件出现在下载目录
        time.sleep(3)
        downloads = glob.glob(os.path.join(self.download_dir, "*.md"))
        downloads += glob.glob(os.path.join(self.download_dir, "*.zip"))
        downloads += glob.glob(os.path.join(self.download_dir, "*.docx"))

        if downloads:
            latest = max(downloads, key=os.path.getctime)
            print(f"  [OK] 下载完成: {latest}")
            return latest
        else:
            # 检查是否有 .crdownload 文件 (正在下载)
            crdownload = glob.glob(os.path.join(self.download_dir, "*.crdownload"))
            if crdownload:
                print(f"  [INFO] 仍在下载中 ({crdownload[0]})")
                # 继续等待
                for _ in range(timeout):
                    time.sleep(1)
                    crdownload = glob.glob(os.path.join(self.download_dir, "*.crdownload"))
                    if not crdownload:
                        break
                downloads = glob.glob(os.path.join(self.download_dir, "*.*"))
                if downloads:
                    latest = max(downloads, key=os.path.getctime)
                    print(f"  [OK] 下载完成: {latest}")
                    return latest
            print("  [WARN] 未检测到下载文件")
            return None

    # ═══════════════════════════════════════════════════════════════
    # 完整流程
    # ═══════════════════════════════════════════════════════════════
    def run(self, chat_url=None):
        """执行完整的批量 Markdown 导出流程"""
        print("=" * 60)
        print("DS随心转 批量Markdown导出 自动化")
        print("=" * 60)

        try:
            self.init_driver()

            # 1. 导航到对话页面
            self.navigate_to_chat(chat_url)

            # 2. 点击 FAB "批量导出"
            self.click_batch_export_fab()

            # 3. 等待底部栏出现
            if not self.wait_for_batch_bar():
                print("\n[ERROR] 批量模式未能进入, 中止")
                return None

            # 3.5. ★ 关键: 等待异步消息收集完成
            #       必须在全选之前等待, 否则 isCollecting=true 会阻塞所有UI刷新
            if not self.wait_for_collection_complete():
                print("\n[WARN] 消息收集可能未完成, 继续尝试全选...")

            # 4. 全选 (通过JS直接调用平台方法, 不依赖DOM复选框)
            if not self.click_select_all():
                print("\n[ERROR] 全选失败, 中止")
                return None

            # 5. 点击 Markdown 导出
            if not self.click_markdown_export():
                print("\n[ERROR] MD导出点击失败, 中止")
                return None

            # 6. 等待下载
            result = self.wait_for_download()
            print(f"\n{'=' * 60}")
            print(f"导出完成! 文件: {result}")
            print(f"{'=' * 60}")
            return result

        except Exception as e:
            print(f"\n[ERROR] 执行异常: {e}")
            import traceback
            traceback.print_exc()
            return None

    def cleanup(self):
        """清理资源"""
        if hasattr(self, 'driver'):
            # 不关闭浏览器, 让用户查看结果
            # self.driver.quit()
            pass


# ═══════════════════════════════════════════════════════════════════════
# 独立环节函数 (可分步调用)
# ═══════════════════════════════════════════════════════════════════════

def step1_enter_batch_mode(driver, wait):
    """环节1: 进入批量模式 (派发 CustomEvent)"""
    driver.execute_script(
        "window.dispatchEvent(new CustomEvent('dssxz-toggle-batch-mode'))"
    )
    wait.until(EC.presence_of_element_located((By.ID, "dssxz-batch-bar-container")))
    return True


def step2_select_all(driver):
    """环节2: 全选所有对话"""
    cb = driver.find_element(By.ID, "dssxz-select-all")
    driver.execute_script("arguments[0].click();", cb)
    time.sleep(1)
    return driver.execute_script(
        "return document.getElementById('dssxz-select-all').checked"
    )


def step3_export_markdown(driver, wait):
    """环节3: 触发 Markdown 导出"""
    md_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-type="md"]'))
    )
    driver.execute_script("arguments[0].click();", md_btn)
    # 等待批量模式退出 (导出成功标志)
    WebDriverWait(driver, 120).until(
        lambda d: "dssxz-batch-active" not in
        d.execute_script("return document.body.className")
    )
    return True


def step4_step_by_step_batch_export(driver, wait):
    """
    分步执行完整导出 (不含导航, 假设已在对话页面).
    适用场景: 已经手动导航到 DeepSeek 对话页面后调用.
    返回: 下载文件路径
    """
    print("[1/4] 进入批量模式...")
    step1_enter_batch_mode(driver, wait)
    print("  ✓ 底部批量栏已出现")

    print("[2/4] 全选所有对话...")
    step2_select_all(driver)
    print("  ✓ 全选完成")

    print("[3/4] 点击 Markdown 导出...")
    step3_export_markdown(driver, wait)
    print("  ✓ 导出请求已发出, 批量模式已退出")

    # 等待下载
    time.sleep(3)
    downloads = glob.glob(os.path.join(DOWNLOAD_DIR, "*.md"))
    return downloads[0] if downloads else None


# ═══════════════════════════════════════════════════════════════════════
# 快捷函数: 在当前已打开的 DeepSeek 页面上直接执行 (无需 WebDriver)
# ═══════════════════════════════════════════════════════════════════════

def get_browser_console_script():
    """
    返回一段可直接粘贴到 Chrome DevTools Console 的 JavaScript 代码,
    实现一键批量导出 Markdown。

    前提: 已在 DeepSeek 对话页面, DS随心转插件已激活。

    🔴 核心修复说明:
      - 进入批量模式后, collectAllVirtualListMessages() 异步收集消息
      - 期间 isCollecting=true 会阻塞所有UI刷新
      - 必须等待收集完成后, 直接调用平台实例的 toggleSelectAll(true)
      - 不能依赖DOM复选框, 因为Fiber键与DOM键不一致导致复选框永不被勾选
    """
    return """
// === DS随心转 一键批量Markdown导出 (修复版) ===
(async function oneClickBatchMDExport() {
    async function wait(ms) { return new Promise(r => setTimeout(r, ms)); }

    // 获取平台实例
    function getPlatform() {
        const key = Object.keys(window).find(k => k.startsWith('dssxz_deepseek'));
        return key ? window[key] : null;
    }

    console.log('=== DS随心转 批量Markdown导出 ===');
    console.log('[1/5] 进入批量模式...');

    // 派发事件触发批量模式
    window.dispatchEvent(new CustomEvent('dssxz-toggle-batch-mode'));
    await wait(2000);

    // 验证底部栏
    if (!document.getElementById('dssxz-batch-bar-container')) {
        console.error('✗ 底部栏未出现, 重试...');
        const platform = getPlatform();
        if (platform && typeof platform.toggleBatchMode === 'function') {
            platform.toggleBatchMode();
            await wait(2000);
        }
    }

    if (!document.getElementById('dssxz-batch-bar-container')) {
        console.error('✗ 无法进入批量模式');
        return;
    }
    console.log('  ✓ 批量模式已激活');

    // ★ [2/5] 等待消息收集完成 (最关键的一步!)
    console.log('[2/5] 等待消息收集完成...');
    const platform = getPlatform();
    if (!platform) {
        console.error('✗ 平台实例不存在');
        return;
    }

    let waited = 0;
    const maxWait = 60;
    while (platform.isCollecting && waited < maxWait) {
        const countEl = document.getElementById('dssxz-selected-count');
        const status = countEl ? countEl.textContent : '?';
        console.log(`  [${waited}s] ${status}`);
        await wait(2000);
        waited += 2;
    }

    if (platform.isCollecting) {
        console.warn('  ⚠ 等待超时, 继续尝试...');
    }

    console.log(`  ✓ 收集完成: virtualListCache=${platform.virtualListCache.size}, `
        + `fiberDataAvailable=${platform.fiberDataAvailable}`);

    // ★ [3/5] 全选 — 直接调用平台方法, 绕过DOM复选框的bug
    console.log('[3/5] 全选所有对话...');
    platform.toggleSelectAll(true);

    // 强制刷新UI (修复isCollecting竞态)
    if (!platform.isCollecting && !platform.isExporting) {
        platform.refreshBatchCheckboxes();
    }
    await wait(1500);

    const selCount = platform.virtualListCache.size > 0
        ? platform.selectedVirtualKeys.size
        : platform.selectedMessages.size;
    const totalCount = platform.virtualListCache.size > 0
        ? platform.virtualListCache.size
        : platform.getPotentialMessages().length;
    console.log(`  ✓ 已选择 ${selCount} / ${totalCount} 条`);

    if (selCount === 0) {
        console.error('✗ 未选中任何消息');
        return;
    }

    // 手动设置复选框视觉效果 (不影响实际选中逻辑)
    const cb = document.getElementById('dssxz-select-all');
    if (cb) cb.checked = true;

    // [4/5] Markdown导出
    console.log('[4/5] 触发Markdown导出...');
    const mdBtn = document.querySelector('[data-type="md"]');
    if (mdBtn) {
        mdBtn.click();
        console.log('  ✓ 导出已触发');
    } else {
        console.error('✗ MD按钮未找到');
        return;
    }

    // [5/5] 等待导出完成
    console.log('[5/5] 等待导出完成...');
    await new Promise((resolve) => {
        const start = Date.now();
        const check = setInterval(() => {
            if (!document.body.classList.contains('dssxz-batch-active')) {
                clearInterval(check);
                console.log('  ✓ 批量模式已退出, 导出完成');
                resolve();
            }
            if (Date.now() - start > 120000) {
                clearInterval(check);
                console.warn('  ⚠ 等待超时 (120s)');
                resolve();
            }
        }, 1000);
    });

    console.log('=== 导出流程完成 ===');
})();
"""


# ═══════════════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    exporter = DSSXZBatchExporter()
    result = exporter.run()
    if result:
        print(f"\n导出文件: {result}")
    else:
        print("\n导出未成功, 请检查日志")
    input("按 Enter 关闭浏览器...")
