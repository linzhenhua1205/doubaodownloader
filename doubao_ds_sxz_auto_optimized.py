import os
import sys
import time
import json
from datetime import datetime

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError as e:
    print(f"错误: 无法导入selenium模块 - {e}")
    print("请运行: pip install selenium")
    sys.exit(1)

DEFAULT_CONFIG = {
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

CONFIG = None

def load_config(config_path="config.json"):
    """加载配置文件，若不存在则使用默认配置并创建配置文件"""
    global CONFIG
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            CONFIG = {**DEFAULT_CONFIG, **user_config}
            print(f"[配置] 已从 {config_path} 加载配置")
        except Exception as e:
            print(f"警告: 配置文件读取失败，使用默认配置 - {e}")
            CONFIG = DEFAULT_CONFIG.copy()
    else:
        CONFIG = DEFAULT_CONFIG.copy()
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(CONFIG, f, ensure_ascii=False, indent=4)
            print(f"[配置] 配置文件不存在，已创建默认配置: {config_path}")
        except Exception as e:
            print(f"警告: 创建默认配置文件失败 - {e}")
    
    validate_config()

def validate_config():
    """验证配置项是否完整"""
    required_keys = [
        "chrome_path", "chromedriver_path", "extension_path", 
        "download_dir", "md_dir", "progress_path", "error_log_path",
        "index_html_files", "download_timeout", "export_timeout",
        "page_load_timeout", "batch_mode_timeout", "max_concurrent_downloads"
    ]
    
    for key in required_keys:
        if key not in CONFIG:
            print(f"警告: 配置项 {key} 缺失，使用默认值")
            CONFIG[key] = DEFAULT_CONFIG.get(key)
    
    if not isinstance(CONFIG["index_html_files"], list) or len(CONFIG["index_html_files"]) == 0:
        print("警告: index_html_files 配置无效，使用默认值")
        CONFIG["index_html_files"] = DEFAULT_CONFIG["index_html_files"]
    
    print(f"[配置] Chrome路径: {CONFIG['chrome_path']}")
    print(f"[配置] 下载目录: {CONFIG['download_dir']}")
    print(f"[配置] 索引文件数: {len(CONFIG['index_html_files'])}")

def extract_links_from_single_file(html_file):
    """从单个HTML索引文件中提取链接ID和标题，返回 [(link_id, title), ...] 列表"""
    import re
    if not os.path.exists(html_file):
        print(f"警告: 文件不存在，跳过: {html_file}")
        return []
    
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 匹配每个 link-card 块: link-name 和 link-url
    pattern = r'<div class="link-name">(.*?)</div>\s*<div class="link-url">https://www\.doubao\.com/chat/(\d+)</div>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    result = []
    for title, link_id in matches:
        title = title.strip()
        result.append((link_id, title))
    return result

def extract_links_with_titles(html_files):
    """从多个HTML索引文件中提取链接ID和标题，返回 [(link_id, title), ...] 去重列表"""
    all_links = []
    for html_file in html_files:
        links = extract_links_from_single_file(html_file)
        print(f"从 {os.path.basename(html_file)} 提取到 {len(links)} 个链接")
        all_links.extend(links)
    
    seen = set()
    result = []
    for link_id, title in all_links:
        if link_id not in seen:
            seen.add(link_id)
            result.append((link_id, title))
    return result

def get_existing_titles(md_dir):
    """扫描 md 目录，提取已有文件的「规范化标题」集合"""
    import re
    titles = set()
    if not os.path.exists(md_dir):
        return titles
    for fname in os.listdir(md_dir):
        if not fname.lower().endswith('.md'):
            continue
        name = os.path.splitext(fname)[0]
        # 去掉末尾数字后缀: _0605005322, _v2, _1, 等
        name = re.sub(r'[_\s-]*\d{6,}([_\s-]*[vV]\d+)?$', '', name)
        name = re.sub(r'[_\s-]*\d{1,5}$', '', name)
        if name:
            titles.add(name)
    return titles

def normalize_title(s):
    """规范化标题，用于模糊匹配"""
    import re
    s = s.lower().strip()
    # 去掉末尾数字后缀: _0605005322, _v2, _1, 等
    s = re.sub(r'[_\s-]*\d{6,}([_\s-]*[vV]\d+)?$', '', s)
    s = re.sub(r'[_\s-]*\d{1,5}$', '', s)
    # 去掉常见标点符号（保留字母数字中文）
    s = re.sub(r'[\s\-_／／·•,，。、；;：:！!？?（）()【】\[\]{}""''「」『』〈〉《》～~@#$%^&*+=|\\/]+', '', s)
    return s

def is_title_matched(title, existing_titles):
    """检查标题是否与已有文件匹配（精确 + 子串 + 去除_后匹配 + 相似度）"""
    import difflib
    # 精确匹配
    if title in existing_titles:
        return True
    norm_title = normalize_title(title)
    if not norm_title or len(norm_title) < 3:
        return False
    # 去除_字符后的标题（额外匹配）
    title_no_underscore = title.replace('_', '')
    for et in existing_titles:
        norm_et = normalize_title(et)
        if not norm_et or len(norm_et) < 3:
            continue
        # 子串匹配
        if norm_title in norm_et or norm_et in norm_title:
            return True
        # 去除_字符后匹配
        et_no_underscore = et.replace('_', '')
        if title_no_underscore == et_no_underscore:
            return True
        # 去除_字符后的子串匹配
        if title_no_underscore in et_no_underscore or et_no_underscore in title_no_underscore:
            return True
        # 相似度匹配（适用于标题措辞不同但主题相同的情况）
        ratio = difflib.SequenceMatcher(None, norm_title, norm_et).ratio()
        if ratio >= 0.7:
            return True
    return False

def sort_links_by_existing_with_info(links_with_titles, existing_titles):
    """
    对链接排序：未匹配的在前，匹配的按相似度升序排列
    links_with_titles: [(link_id, title), ...]
    返回 (排序后的链接列表, 已匹配ID信息)
    """
    import difflib
    
    unmatched = []
    matched_with_score = []
    matched_info = {}
    
    # 预计算所有现有标题的规范化值和去除下划线值，避免重复计算
    preprocessed = []
    for et in existing_titles:
        norm_et = normalize_title(et)
        if norm_et and len(norm_et) >= 3:
            preprocessed.append((norm_et, et.replace('_', '')))
    
    for link_id, title in links_with_titles:
        norm_title = normalize_title(title)
        if not norm_title or len(norm_title) < 3:
            unmatched.append((link_id, title))
            continue
        
        matched_flag = False
        max_ratio = 0
        title_no_underscore = title.replace('_', '')
        
        # 使用预计算的值进行匹配
        for norm_et, et_no_underscore in preprocessed:
            # 快速检查1: 子串匹配
            if norm_title in norm_et or norm_et in norm_title:
                matched_flag = True
                max_ratio = 1.0
                break
            
            # 快速检查2: 去除下划线后的匹配
            if title_no_underscore == et_no_underscore or title_no_underscore in et_no_underscore or et_no_underscore in title_no_underscore:
                matched_flag = True
                max_ratio = 1.0
                break
            
            # 只有在快速检查未通过时才进行更耗时的相似度计算
            if not matched_flag:
                ratio = difflib.SequenceMatcher(None, norm_title, norm_et).ratio()
                if ratio >= 0.7:
                    matched_flag = True
                    max_ratio = ratio
                    break
        
        if matched_flag:
            matched_with_score.append((link_id, title, max_ratio))
            matched_info[link_id] = True
        else:
            unmatched.append((link_id, title))
    
    matched_sorted = sorted(matched_with_score, key=lambda x: x[2])
    matched_result = [(lid, t) for lid, t, _ in matched_sorted]
    
    return unmatched + matched_result, matched_info

def sort_links_by_existing(links_with_titles, existing_titles):
    """
    兼容性函数，保持向后兼容
    """
    sorted_links, _ = sort_links_by_existing_with_info(links_with_titles, existing_titles)
    return sorted_links

def load_progress():
    """加载下载进度记录"""
    progress_path = CONFIG.get("progress_path", DEFAULT_CONFIG["progress_path"])
    if os.path.exists(progress_path):
        try:
            with open(progress_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_progress(progress):
    """保存下载进度记录"""
    progress_path = CONFIG.get("progress_path", DEFAULT_CONFIG["progress_path"])
    try:
        with open(progress_path, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"  [WARN] 保存进度失败: {e}")

def is_completed(progress, link_id):
    """检查某个链接是否已完成下载"""
    return link_id in progress

def record_success(progress, link_id, title, filename):
    """记录成功下载的条目"""
    progress[link_id] = {
        "title": title,
        "filename": filename,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_progress(progress)
    print(f"  [记录] 已记录进度: {link_id} -> {title}")

def extract_title(driver):
    """提取对话标题"""
    try:
        title = driver.execute_script("""
            var el = document.querySelector('.chat-title, [class*="chat-title"], [class*="conversation-title"], h1');
            if (el) return el.textContent.trim();
            return '';
        """)
        if title:
            return title
    except:
        pass
    try:
        return driver.title.strip()
    except:
        return ""

def check_download_result(download_dir, start_md_files, start_md_count, timeout=None):
    """
    检查下载结果，通过判断MD文件数是否增加来确认下载成功
    download_dir: 下载目录
    start_md_files: 导出前的MD文件集合
    start_md_count: 导出前的MD文件数量
    timeout: 超时时间（秒），默认使用配置值
    """
    if timeout is None:
        timeout = CONFIG.get("download_timeout", DEFAULT_CONFIG["download_timeout"])
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        current_md_files = set([f for f in os.listdir(download_dir) if f.lower().endswith('.md')])
        current_md_count = len(current_md_files)
        
        if current_md_count > start_md_count:
            new_md_files = list(current_md_files - start_md_files)
            if new_md_files:
                return True, new_md_files[0]
            return True, list(current_md_files)[0] if current_md_files else None
        
        time.sleep(0.5)
    
    current_md_files = set([f for f in os.listdir(download_dir) if f.lower().endswith('.md')])
    current_md_count = len(current_md_files)
    if current_md_count > start_md_count:
        new_md_files = list(current_md_files - start_md_files)
        if new_md_files:
            return True, new_md_files[0]
        return True, list(current_md_files)[0] if current_md_files else None
    
    return False, None

def dispatch_custom_event(driver, event_name):
    """派发自定义事件，最可靠的触发方式"""
    script = f'window.dispatchEvent(new CustomEvent("{event_name}"))'
    return driver.execute_script(script)

def is_batch_mode_active(driver):
    """检查是否处于批量模式"""
    try:
        class_name = driver.execute_script('return document.body.className')
        return 'dssxz-batch-active' in class_name
    except:
        return False

def wait_for_batch_bar(driver, timeout=15):
    """等待底部批量操作栏出现"""
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "dssxz-batch-bar-container"))
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dssxz-select-all"))
        )
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dssxz-batch-export-container"))
        )
        return True
    except Exception as e:
        print(f"  等待底部栏失败: {str(e)[:50]}")
        return False

def wait_for_collection_complete(driver, timeout=10):
    """
    ★ 关键步骤: 等待消息收集完成 - 根据Chat2File.md分析
    """
    print("  [步骤3.5] 等待豆包API消息加载完成 (关键步骤)...")
    
    try:
        count_el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "dssxz-selected-count"))
        )
        
        start = time.time()
        last_text = ""
        
        while time.time() - start < timeout:
            txt = count_el.text.strip()
            
            if txt != last_text:
                print(f"  [{int(time.time()-start)}s] 计数: '{txt}'")
                last_text = txt
            
            if "共" in txt and "条消息" in txt:
                print(f"  [OK] API消息加载完成! 计数: '{txt}'")
                time.sleep(1.5)
                
                try:
                    api_len = driver.execute_script("""
                        return window._doubaoInstance && window._doubaoInstance._apiMessages ? 
                            window._doubaoInstance._apiMessages.length : 0;
                    """)
                    print(f"  [OK] 内部API消息数: {api_len}")
                except:
                    pass
                
                try:
                    sa = driver.find_element(By.ID, "dssxz-select-all")
                    for _ in range(10):
                        disabled = sa.get_attribute("disabled")
                        cursor = driver.execute_script("return getComputedStyle(arguments[0]).cursor;", sa)
                        if disabled is None and cursor != "not-allowed":
                            print(f"  [OK] 全选按钮已解禁")
                            break
                        time.sleep(0.5)
                except:
                    pass
                
                return True
            
            time.sleep(1)
        
        print(f"  [WARN] 等待超时 ({timeout}s), 但继续尝试...")
        return True
    except Exception as e:
        print(f"  [WARN] 等待消息加载失败: {str(e)[:50]}, 继续尝试...")
        return True

def click_select_all(driver):
    """★ 全选 - DOM 点击优先（已验证可用），JS 内部调用兜底"""
    print("  [步骤3] 全选所有对话...")
    
    success = False
    
    # 先确保全选按钮已准备好
    try:
        select_all = driver.find_element(By.ID, "dssxz-select-all")
        for _ in range(10):
            disabled = select_all.get_attribute("disabled")
            cursor = driver.execute_script("return getComputedStyle(arguments[0]).cursor;", select_all)
            if disabled is None and cursor != "not-allowed":
                print("  [OK] 全选按钮已准备好")
                break
            time.sleep(0.3)
    except Exception as e:
        print(f"  [WARN] 检查全选按钮状态时出错: {e}")
    
    # 方法1(优先): DOM 方式点击复选框
    try:
        script = '''
            var cb = document.getElementById('dssxz-select-all');
            if(cb) {
                if(cb.checked) {
                    cb.checked = false;
                    cb.dispatchEvent(new Event('change', {bubbles: true}));
                }
                cb.click();
                cb.dispatchEvent(new Event('change', {bubbles: true}));
                return cb.checked;
            }
            return false;
        '''
        result = driver.execute_script(script)
        if result:
            print("  [OK] DOM 方式全选成功")
            success = True
    except Exception as e:
        print(f"  [WARN] DOM 方式失败: {e}")
    
    # 方法2(兜底): 直接调用 toggleSelectAll
    if not success:
        try:
            result = driver.execute_script("""
                if(window._doubaoInstance && typeof window._doubaoInstance.toggleSelectAll === 'function') {
                    window._doubaoInstance.toggleSelectAll(true);
                    return true;
                }
                return false;
            """)
            if result:
                print("  [OK] 已调用 _doubaoInstance.toggleSelectAll(true)")
                success = True
        except Exception as e:
            print(f"  [WARN] JS 内部调用失败: {e}")
    
    time.sleep(1.5)
    
    try:
        count_text = driver.find_element(By.ID, "dssxz-selected-count").text
        print(f"  [OK] 当前选择计数: '{count_text}'")
    except Exception as e:
        print(f"  [WARN] 验证选择计数时出错: {e}")
    
    return success

def click_md_export(driver):
    """★ MD导出 - DOM 点击优先（已验证可用），JS 内部调用兜底"""
    print("  [步骤4] 点击Markdown导出按钮...")
    
    success = False
    
    # 方法1(优先): DOM 方式点击
    try:
        script = '''
            var container = document.getElementById('dssxz-batch-export-container');
            if(container) {
                var btn = container.querySelector('[data-type="md"]');
                if(!btn) {
                    btn = container.querySelector('.dssxz-btn-md');
                }
                if(!btn) {
                    var buttons = container.querySelectorAll('button, [role="button"]');
                    for(var i=0; i<buttons.length; i++) {
                        var text = buttons[i].textContent || buttons[i].innerText || '';
                        if(text.toLowerCase().indexOf('markdown') !== -1 || text.toLowerCase().indexOf('md') !== -1) {
                            btn = buttons[i];
                            break;
                        }
                    }
                }
                if(btn) {
                    btn.click();
                    return true;
                }
            }
            return false;
        '''
        result = driver.execute_script(script)
        if result:
            print("  [OK] DOM 方式点击成功")
            success = True
    except Exception as e:
        print(f"  [WARN] DOM 方式失败: {e}")
    
    # 方法2(兜底): 直接调用 dssxzBatchUI.exportBatch
    if not success:
        try:
            result = driver.execute_script("""
                if(window.dssxzBatchUI && typeof window.dssxzBatchUI.exportBatch === 'function') {
                    window.dssxzBatchUI.exportBatch("md");
                    return true;
                }
                return false;
            """)
            if result:
                print("  [OK] 已调用 dssxzBatchUI.exportBatch('md')")
                success = True
        except Exception as e:
            print(f"  [WARN] JS 内部调用失败: {e}")
    
    return success

def wait_for_export_complete(driver, timeout=None):
    """等待导出完成（批量模式退出）"""
    if timeout is None:
        timeout = CONFIG.get("export_timeout", DEFAULT_CONFIG["export_timeout"])
    
    print("  [步骤5] 等待导出完成...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            if not is_batch_mode_active(driver):
                print("  [OK] 导出完成")
                return True
        except:
            pass
        time.sleep(1)
    print("  [WARN] 导出超时")
    return False

def is_driver_alive(driver):
    """检查浏览器是否还活着"""
    try:
        driver.title
        return True
    except:
        return False

def create_driver():
    """创建浏览器驱动"""
    chrome_path = CONFIG.get("chrome_path", DEFAULT_CONFIG["chrome_path"])
    chromedriver_path = CONFIG.get("chromedriver_path", DEFAULT_CONFIG["chromedriver_path"])
    extension_path = CONFIG.get("extension_path", DEFAULT_CONFIG["extension_path"])
    download_dir = CONFIG.get("download_dir", DEFAULT_CONFIG["download_dir"])
    chrome_profile_dir = CONFIG.get("chrome_profile_dir", DEFAULT_CONFIG["chrome_profile_dir"])
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--user-data-dir={chrome_profile_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-popup-blocking")
    options.binary_location = chrome_path
    options.add_argument(f"--load-extension={extension_path}")
    
    options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    
    from selenium.webdriver.chrome.service import Service
    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=options)

def record_error(link_id, error_msg):
    """记录错误到本地文件"""
    error_log_path = CONFIG.get("error_log_path", DEFAULT_CONFIG["error_log_path"])
    try:
        errors = []
        if os.path.exists(error_log_path):
            with open(error_log_path, 'r', encoding='utf-8') as f:
                try:
                    errors = json.load(f)
                except:
                    pass
        
        error_info = {
            "link_id": link_id,
            "url": f"https://www.doubao.com/chat/{link_id}",
            "error": error_msg,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        errors.append(error_info)
        
        with open(error_log_path, 'w', encoding='utf-8') as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)
        
        print(f"  [记录] 错误已记录到: {error_log_path}")
    except Exception as e:
        print(f"  [WARN] 记录错误失败: {e}")

def process_single_conversation(driver, link_id):
    """处理单个对话, 返回 (success, filename, title)"""
    try:
        page_load_timeout = CONFIG.get("page_load_timeout", DEFAULT_CONFIG["page_load_timeout"])
        batch_mode_timeout = CONFIG.get("batch_mode_timeout", DEFAULT_CONFIG["batch_mode_timeout"])
        download_dir = CONFIG.get("download_dir", DEFAULT_CONFIG["download_dir"])
        
        print(f"  [步骤1/7] 打开对话页面")
        driver.get(f"https://www.doubao.com/chat/{link_id}")
        time.sleep(page_load_timeout)
        
        title = extract_title(driver)
        print(f"  [标题] {title or '(未获取到)'}")
        
        print("  [步骤2/7] 激活批量模式")
        dispatch_custom_event(driver, "dssxz-toggle-batch-mode")
        time.sleep(batch_mode_timeout)
        
        if not is_batch_mode_active(driver):
            print("     ✗ 批量模式未激活, 尝试再次触发")
            dispatch_custom_event(driver, "dssxz-toggle-batch-mode")
            time.sleep(batch_mode_timeout)
            if not is_batch_mode_active(driver):
                raise Exception("批量模式无法激活")
        
        print("  [步骤3/7] 等待底部操作栏出现")
        if not wait_for_batch_bar(driver):
            raise Exception("底部栏未出现")
        
        print("  [步骤4/7] 等待消息加载完成")
        wait_for_collection_complete(driver)
        
        print("  [步骤5/7] 全选对话内容")
        if not click_select_all(driver):
            raise Exception("全选失败")
        
        start_md_files = set([f for f in os.listdir(download_dir) if f.lower().endswith('.md')])
        start_md_count = len(start_md_files)
        print(f"  [步骤6/7] 执行MD导出 (当前目录文件数: {start_md_count})")
        
        if not click_md_export(driver):
            raise Exception("MD导出按钮点击失败")
        
        print("  [步骤7/7] 等待导出完成")
        if wait_for_export_complete(driver):
            success, filename = check_download_result(download_dir, start_md_files, start_md_count)
            if success:
                print(f"     ✓ 下载成功: {filename}")
                return True, filename, title
            else:
                raise Exception("下载超时")
        else:
            raise Exception("导出超时")
    except Exception as e:
        error_msg = str(e)
        print(f"     ✗ 处理失败: {error_msg[:100]}")
        record_error(link_id, error_msg)
        return False, None, None

def main():
    load_config()
    
    import argparse
    parser = argparse.ArgumentParser(description="豆包批量导出工具")
    parser.add_argument('--check', action='store_true', help='仅检查已下载链接数，不进行实际下载')
    parser.add_argument('--config', default='config.json', help='指定配置文件路径')
    args = parser.parse_args()
    
    if args.config != 'config.json':
        load_config(args.config)
    
    print("="*60)
    print("豆包批量导出工具 - 全自动优化版 (支持断点续传 + 智能排序)")
    print("="*60)
    
    index_html_files = CONFIG.get("index_html_files", DEFAULT_CONFIG["index_html_files"])
    md_dir = CONFIG.get("md_dir", DEFAULT_CONFIG["md_dir"])
    
    existing_files = [f for f in index_html_files if os.path.exists(f)]
    if not existing_files:
        print(f"错误: 索引文件不存在: {', '.join(index_html_files)}")
        return
    
    links_with_titles = extract_links_with_titles(index_html_files)
    if not links_with_titles:
        print("错误: 未找到任何链接")
        return
    print(f"找到 {len(links_with_titles)} 个对话链接")
    
    existing_titles = get_existing_titles(md_dir)
    print(f"md 目录已有文件: {len(existing_titles)} 个")
    
    # 排序：未匹配的在前，匹配的按相似度升序排列
    sorted_links, matched_info = sort_links_by_existing_with_info(links_with_titles, existing_titles)
    unmatched_count = len([lid for lid, t in sorted_links if lid not in matched_info])
    matched_count = len(matched_info)
    print(f"排序结果: 未匹配(优先) {unmatched_count} 个, 已匹配(后置) {matched_count} 个")
    
    progress = load_progress()
    # 第一步：先快速排除进度文件中已记录的ID
    completed_by_progress_ids = {lid for lid, _ in sorted_links if is_completed(progress, lid)}
    
    # 剩余需要检查文件名匹配的链接
    remaining_links = [(lid, t) for lid, t in sorted_links if lid not in completed_by_progress_ids]
    
    # 第二步：对剩余链接进行文件名匹配检查，使用预计算的 matched_info 快速判断
    matched_by_title_ids = set()
    for lid, title in remaining_links:
        if lid in matched_info:
            matched_by_title_ids.add(lid)
    
    # 待处理链接 = 剩余链接 - 文件名匹配的链接
    pending_ids = [lid for lid, t in remaining_links if lid not in matched_by_title_ids]
    
    # 提取排序后的完整链接信息用于统计
    sorted_link_ids = [lid for lid, _ in sorted_links]
    title_map = {lid: t for lid, t in sorted_links}
    
    print(f"第一级去重后: {len(sorted_link_ids)} 个链接")
    print(f"进度文件标记完成: {len(completed_by_progress_ids)} 个")
    print(f"文件名匹配已下载: {len(matched_by_title_ids)} 个")
    print(f"已完成(合计): {len(completed_by_progress_ids) + len(matched_by_title_ids)} 个, 待处理: {len(pending_ids)} 个")
    print(f"总进度: {len(completed_by_progress_ids) + len(matched_by_title_ids)}/{len(sorted_link_ids)} ({(len(completed_by_progress_ids) + len(matched_by_title_ids))*100/len(sorted_link_ids):.1f}%)")
    
    if args.check:
        print("\n仅检查模式，不进行下载。两级去重统计如下：")
        print(f"  第一级去重(HTML源链接): {len(sorted_link_ids)} 个链接")
        print(f"  第二级去重(文件名匹配):")
        print(f"    - 进度文件标记完成: {len(completed_by_progress_ids)} 个")
        print(f"    - 文件名匹配已下载: {len(matched_by_title_ids)} 个")
        print(f"  已完成(合计): {len(completed_by_progress_ids) + len(matched_by_title_ids)} 个")
        print(f"  待处理: {len(pending_ids)} 个")
        if completed_by_progress_ids:
            print(f"  进度文件记录的已下载ID: {', '.join(sorted(completed_by_progress_ids))}")
        return
    
    if completed_by_progress_ids:
        print(f"已完成ID: {', '.join(sorted(completed_by_progress_ids))}")
    
    if not pending_ids:
        print("所有对话均已下载完成, 无需处理!")
        return
    
    download_dir = CONFIG.get("download_dir", DEFAULT_CONFIG["download_dir"])
    chrome_profile_dir = CONFIG.get("chrome_profile_dir", DEFAULT_CONFIG["chrome_profile_dir"])
    max_concurrent_downloads = CONFIG.get("max_concurrent_downloads", DEFAULT_CONFIG["max_concurrent_downloads"])
    page_load_timeout = CONFIG.get("page_load_timeout", DEFAULT_CONFIG["page_load_timeout"])
    
    os.makedirs(download_dir, exist_ok=True)
    os.makedirs(chrome_profile_dir, exist_ok=True)
    
    driver = None
    success_count = 0
    skip_count = len(completed_by_progress_ids) + len(matched_by_title_ids)
    test_count = min(max_concurrent_downloads, len(pending_ids))
    needs_login = True
    
    for idx, link_id in enumerate(pending_ids[:test_count], 1):
        html_title = title_map.get(link_id, "")
        print(f"\n[{idx}/{test_count}] 处理对话: {link_id}")
        if html_title:
            print(f"  [HTML标题] {html_title}")
        
        try:
            if driver is None or not is_driver_alive(driver):
                print("  [重新启动浏览器]")
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                driver = create_driver()
                print("     ✓ Chrome启动成功")
                driver.get("https://www.doubao.com/chat/")
                time.sleep(page_load_timeout)
                
                if needs_login:
                    print("\n请完成以下操作后按 Enter 继续:")
                    print("1. 登录你的豆包账号")
                    print("2. 确保DS随心转插件已加载")
                    input()
                    needs_login = False
            
            success, filename, title = process_single_conversation(driver, link_id)
            if success:
                success_count += 1
                record_success(progress, link_id, title or html_title or "", filename)
            
        except Exception as e:
            print(f"  ✗ 整体处理失败: {str(e)[:100]}")
            record_error(link_id, str(e))
            import traceback
            traceback.print_exc()
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            driver = None
    
    total_links = len(sorted_link_ids)
    progress_path = CONFIG.get("progress_path", DEFAULT_CONFIG["progress_path"])
    error_log_path = CONFIG.get("error_log_path", DEFAULT_CONFIG["error_log_path"])
    
    print(f"\n{'='*60}")
    print(f"完成! 本次成功: {success_count}/{test_count}, 累计已完成: {skip_count + success_count}/{total_links}")
    print(f"下载目录: {download_dir}")
    print(f"进度文件: {progress_path}")
    if os.path.exists(error_log_path):
        print(f"错误记录: {error_log_path}")
    print("="*60)
    
    if driver:
        try:
            time.sleep(3)
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
