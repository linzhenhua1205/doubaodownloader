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

CHROME_PATH = r"D:\123\md\chrome-win64\chrome-win64\chrome.exe"
EXTENSION_PATH = r"D:\123\md\dssxz"
DOWNLOAD_DIR = r"D:\123\md\ai_md_exports"
INDEX_HTML = r"D:\123\md\豆包链接索引.html"
ERROR_LOG_PATH = r"D:\123\md\export_errors.json"
PROGRESS_PATH = r"D:\123\md\download_progress.json"
MD_DIR = r"D:\123\md\md"

def extract_links_with_titles(html_file):
    """从HTML索引文件中提取链接ID和标题，返回 [(link_id, title), ...] 去重列表"""
    import re
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 匹配每个 link-card 块: link-name 和 link-url
    pattern = r'<div class="link-name">(.*?)</div>\s*<div class="link-url">https://www\.doubao\.com/chat/(\d+)</div>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    seen = set()
    result = []
    for title, link_id in matches:
        title = title.strip()
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
    """检查标题是否与已有文件匹配（精确 + 子串 + 相似度）"""
    import difflib
    # 精确匹配
    if title in existing_titles:
        return True
    norm_title = normalize_title(title)
    if not norm_title or len(norm_title) < 3:
        return False
    for et in existing_titles:
        norm_et = normalize_title(et)
        if not norm_et or len(norm_et) < 3:
            continue
        # 子串匹配
        if norm_title in norm_et or norm_et in norm_title:
            return True
        # 相似度匹配（适用于标题措辞不同但主题相同的情况）
        ratio = difflib.SequenceMatcher(None, norm_title, norm_et).ratio()
        if ratio >= 0.55:
            return True
    return False

def sort_links_by_existing(links_with_titles, existing_titles):
    """
    对链接排序：未匹配已有文件的在前，匹配的在后
    links_with_titles: [(link_id, title), ...]
    返回排序后的 [(link_id, title), ...]
    """
    unmatched = []
    matched = []
    for link_id, title in links_with_titles:
        if is_title_matched(title, existing_titles):
            matched.append((link_id, title))
        else:
            unmatched.append((link_id, title))
    return unmatched + matched

def load_progress():
    """加载下载进度记录"""
    if os.path.exists(PROGRESS_PATH):
        try:
            with open(PROGRESS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {}

def save_progress(progress):
    """保存下载进度记录"""
    try:
        with open(PROGRESS_PATH, 'w', encoding='utf-8') as f:
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

def wait_for_download(download_dir, timeout=60):
    start_files = set(os.listdir(download_dir))
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - start_files
        md_files = [f for f in new_files if f.lower().endswith('.md')]
        if md_files:
            return True, md_files[0]
        time.sleep(1)
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

def wait_for_export_complete(driver, timeout=5):
    """等待导出完成（批量模式退出）"""
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
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument(f"--user-data-dir={r'D:\123\md\chrome_profile'}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-popup-blocking")
    options.binary_location = CHROME_PATH
    options.add_argument(f"--load-extension={EXTENSION_PATH}")
    
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    
    from selenium.webdriver.chrome.service import Service
    chromedriver_path = r"D:\123\md\chromedriver-win64\chromedriver.exe"
    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=options)

def record_error(link_id, error_msg):
    """记录错误到本地文件"""
    try:
        errors = []
        if os.path.exists(ERROR_LOG_PATH):
            with open(ERROR_LOG_PATH, 'r', encoding='utf-8') as f:
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
        
        with open(ERROR_LOG_PATH, 'w', encoding='utf-8') as f:
            json.dump(errors, f, ensure_ascii=False, indent=2)
        
        print(f"  [记录] 错误已记录到: {ERROR_LOG_PATH}")
    except Exception as e:
        print(f"  [WARN] 记录错误失败: {e}")

def process_single_conversation(driver, link_id):
    """处理单个对话, 返回 (success, filename, title)"""
    try:
        print(f"  [步骤0] 打开对话页面")
        driver.get(f"https://www.doubao.com/chat/{link_id}")
        time.sleep(8)
        
        title = extract_title(driver)
        print(f"  [标题] {title or '(未获取到)'}")
        
        print("  [步骤1] 派发批量模式事件")
        dispatch_custom_event(driver, "dssxz-toggle-batch-mode")
        time.sleep(3)
        
        if not is_batch_mode_active(driver):
            print("     ✗ 批量模式未激活, 尝试再次触发")
            dispatch_custom_event(driver, "dssxz-toggle-batch-mode")
            time.sleep(3)
            if not is_batch_mode_active(driver):
                raise Exception("批量模式无法激活")
        
        print("  [步骤2] 等待底部操作栏出现")
        if not wait_for_batch_bar(driver):
            raise Exception("底部栏未出现")
        
        wait_for_collection_complete(driver)
        
        if not click_select_all(driver):
            raise Exception("全选失败")
        
        if not click_md_export(driver):
            raise Exception("MD导出按钮点击失败")
        
        if wait_for_export_complete(driver):
            success, filename = wait_for_download(DOWNLOAD_DIR, 20)
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
    print("="*60)
    print("豆包批量导出工具 - 全自动优化版 (支持断点续传 + 智能排序)")
    print("="*60)
    
    if not os.path.exists(INDEX_HTML):
        print(f"错误: 索引文件不存在: {INDEX_HTML}")
        return
    
    links_with_titles = extract_links_with_titles(INDEX_HTML)
    if not links_with_titles:
        print("错误: 未找到任何链接")
        return
    print(f"找到 {len(links_with_titles)} 个对话链接")
    
    # 扫描已有 md 文件，用于排序
    existing_titles = get_existing_titles(MD_DIR)
    print(f"md 目录已有文件: {len(existing_titles)} 个")
    
    # 排序：未匹配的在前，匹配的在后
    sorted_links = sort_links_by_existing(links_with_titles, existing_titles)
    matched_count = sum(1 for _, t in sorted_links if is_title_matched(t, existing_titles))
    unmatched_count = len(sorted_links) - matched_count
    print(f"排序结果: 未匹配(优先) {unmatched_count} 个, 已匹配(后置) {matched_count} 个")
    
    # 提取排序后的 link_id 列表
    sorted_link_ids = [lid for lid, _ in sorted_links]
    title_map = {lid: t for lid, t in sorted_links}
    
    progress = load_progress()
    completed_ids = {lid for lid in sorted_link_ids if is_completed(progress, lid)}
    pending_ids = [lid for lid in sorted_link_ids if lid not in completed_ids]
    
    print(f"已完成: {len(completed_ids)} 个, 待处理: {len(pending_ids)} 个")
    if completed_ids:
        print(f"已完成ID: {', '.join(sorted(completed_ids))}")
    
    if not pending_ids:
        print("所有对话均已下载完成, 无需处理!")
        return
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(r"D:\123\md\chrome_profile", exist_ok=True)
    
    driver = None
    success_count = 0
    skip_count = len(completed_ids)
    test_count = min(5000, len(pending_ids))
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
                time.sleep(8)
                
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
    print(f"\n{'='*60}")
    print(f"完成! 本次成功: {success_count}/{test_count}, 累计已完成: {skip_count + success_count}/{total_links}")
    print(f"下载目录: {DOWNLOAD_DIR}")
    print(f"进度文件: {PROGRESS_PATH}")
    if os.path.exists(ERROR_LOG_PATH):
        print(f"错误记录: {ERROR_LOG_PATH}")
    print("="*60)
    
    if driver:
        try:
            time.sleep(3)
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
