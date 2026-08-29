import os
import sys
import time
import json

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

CHROME_PATH = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"
EXTENSION_PATH = r"h:\github\md\dssxz"
DOWNLOAD_DIR = r"H:\dl\ai_md_exports"
INDEX_HTML = r"h:\github\md\豆包链接索引.html"

def extract_unique_links(html_file):
    import re
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    links = re.findall(r'https://www\.doubao\.com/chat/(\d+)', content)
    return list(set(links))

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

def wait_for_collection_complete(driver, timeout=60):
    """
    ★ 关键步骤: 等待消息收集完成
    
    根因分析 (三处异步竞态):
    1. enableBatchUI() 最后调用 collectAllVirtualListMessages() — 异步函数
    2. toggleSelectAll() 中 isCollecting=true 时 virtualListCache 被清空
    3. refreshBatchCheckboxes() 中 if(isCollecting) return — 直接跳过UI刷新
    
    必须等待 isCollecting=false && virtualListCache.size > 0 后再执行全选
    """
    print("  [步骤3.5] 等待消息收集完成 (关键步骤)...")
    start = time.time()
    while time.time() - start < timeout:
        info = driver.execute_script("""
            var platform = null;
            var keys = Object.keys(window);
            for(var k of keys) {
                if(k.includes('doubao') || k.includes('platform') || k.includes('dssxz')) {
                    var obj = window[k];
                    if(obj && typeof obj.toggleSelectAll === 'function') {
                        platform = obj;
                        break;
                    }
                }
            }
            if(!platform) return 'no_platform';
            return JSON.stringify({
                isCollecting: platform.isCollecting || false,
                virtualListCacheSize: platform.virtualListCache ? platform.virtualListCache.size : 0,
                fiberDataAvailable: platform.fiberDataAvailable || false,
                selectedVirtualKeysSize: platform.selectedVirtualKeys ? platform.selectedVirtualKeys.size : 0,
                selectedMessagesSize: platform.selectedMessages ? platform.selectedMessages.size : 0
            });
        """)
        
        try:
            info = json.loads(info)
        except:
            time.sleep(1)
            continue
        
        if info == 'no_platform':
            print("  [WARN] 平台实例未找到, 继续等待...")
            time.sleep(2)
            continue
        
        elapsed = int(time.time() - start)
        status = "收集" if info['isCollecting'] else "完成"
        
        try:
            count_el = driver.find_element(By.ID, "dssxz-selected-count")
            count_text = count_el.text
        except:
            count_text = "?"
        
        print(f"  [{elapsed}s] isCollecting={info['isCollecting']}, "
              f"cacheSize={info['virtualListCacheSize']}, "
              f"count='{count_text}'")
        
        if not info['isCollecting'] and info['virtualListCacheSize'] > 0:
            print(f"  [OK] 消息收集完成! 共 {info['virtualListCacheSize']} 条消息")
            return True
        
        if not info['isCollecting']:
            print(f"  [INFO] 收集结束, 使用DOM扫描模式")
            return True
        
        time.sleep(2)
    
    print(f"  [WARN] 等待超时 ({timeout}s), 继续尝试...")
    return False

def click_select_all(driver):
    """
    ★ 全选 - 通过JS直接调用平台方法, 不依赖DOM复选框
    
    为什么不能直接点DOM复选框:
    - isCollecting=true 时 refreshBatchCheckboxes() 直接 return
    - collection完成后 updateBatchUIState() 比较的是 Fiber键 != DOM键
    - 导致复选框永远不被勾选
    
    正确做法: 直接调用平台实例的 toggleSelectAll(true)
    """
    print("  [步骤3] 全选所有对话...")
    
    result = driver.execute_script("""
        var platform = null;
        var keys = Object.keys(window);
        for(var k of keys) {
            if(k.includes('doubao') || k.includes('platform') || k.includes('dssxz')) {
                var obj = window[k];
                if(obj && typeof obj.toggleSelectAll === 'function') {
                    platform = obj;
                    break;
                }
            }
        }
        if(!platform) return 'no_platform';
        
        if(platform.isCollecting) return 'still_collecting';
        
        platform.toggleSelectAll(true);
        
        if(!platform.isCollecting && !platform.isExporting) {
            platform.refreshBatchCheckboxes();
        }
        
        return JSON.stringify({
            virtualListCacheSize: platform.virtualListCache ? platform.virtualListCache.size : 0,
            selectedVirtualKeysSize: platform.selectedVirtualKeys ? platform.selectedVirtualKeys.size : 0,
            selectedMessagesSize: platform.selectedMessages ? platform.selectedMessages.size : 0,
            fiberDataAvailable: platform.fiberDataAvailable || false
        });
    """)
    
    print(f"  [JS返回] {result}")
    
    if result == 'no_platform':
        print("  [FAIL] 平台实例不存在, 尝试DOM方式")
        return fallback_click_select_all(driver)
    if result == 'still_collecting':
        print("  [FAIL] 消息仍在收集")
        return False
    
    try:
        info = json.loads(result)
    except:
        print(f"  [FAIL] 解析失败")
        return fallback_click_select_all(driver)
    
    selected_count = info['selectedVirtualKeysSize'] or info['selectedMessagesSize']
    total_count = info['virtualListCacheSize']
    print(f"  [OK] 已选择 {selected_count} / {total_count} 条消息")
    
    time.sleep(1.5)
    
    try:
        driver.execute_script("document.getElementById('dssxz-select-all').checked = true;")
    except:
        pass
    
    return selected_count > 0

def fallback_click_select_all(driver):
    """备用方案: DOM方式点击全选"""
    try:
        script = '''
            var cb = document.getElementById('dssxz-select-all');
            if(cb && !cb.checked) {
                cb.click();
                return cb.checked;
            }
            return cb ? cb.checked : false;
        '''
        result = driver.execute_script(script)
        if result:
            print("  [OK] DOM方式全选成功")
        return result
    except Exception as e:
        print(f"  [FAIL] DOM方式也失败: {str(e)[:50]}")
        return False

def click_md_export(driver):
    """点击Markdown导出按钮"""
    print("  [步骤4] 点击Markdown导出按钮...")
    try:
        script = '''
            var btn = document.querySelector('[data-type="md"]');
            if(btn) {
                btn.click();
                return true;
            }
            return false;
        '''
        result = driver.execute_script(script)
        if result:
            print("  [OK] MD导出按钮已点击")
            return True
        else:
            print("  [FAIL] MD按钮未找到")
            return False
    except Exception as e:
        print(f"  [FAIL] 点击失败: {str(e)[:50]}")
        return False

def wait_for_export_complete(driver, timeout=120):
    """等待导出完成（批量模式退出）"""
    print("  [步骤5] 等待导出完成...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not is_batch_mode_active(driver):
            print("  [OK] 导出完成")
            return True
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
    options.add_argument(f"--user-data-dir={r'h:\github\md\chrome_profile'}")
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
    
    return webdriver.Chrome(options=options)

def process_single_conversation(driver, link_id):
    """处理单个对话"""
    print(f"  [步骤0] 打开对话页面")
    driver.get(f"https://www.doubao.com/chat/{link_id}")
    time.sleep(10)
    
    print("  [步骤1] 派发批量模式事件")
    dispatch_custom_event(driver, "dssxz-toggle-batch-mode")
    time.sleep(3)
    
    if not is_batch_mode_active(driver):
        print("     ✗ 批量模式未激活，请手动点击悬浮按钮")
        input("准备好后按Enter继续...")
    
    print("  [步骤2] 等待底部操作栏出现")
    if not wait_for_batch_bar(driver):
        print("     ✗ 底部栏未出现，请手动检查")
        input("准备好后按Enter继续...")
    
    # ★ 关键步骤: 等待消息收集完成
    wait_for_collection_complete(driver)
    
    # ★ 关键修复: 直接调用平台方法全选
    if not click_select_all(driver):
        print("     ✗ 全选失败，请手动勾选")
        input("勾选后按Enter继续...")
    
    if not click_md_export(driver):
        print("     ✗ MD导出按钮点击失败，请手动点击")
        input("点击后按Enter继续...")
    
    if wait_for_export_complete(driver):
        success, filename = wait_for_download(DOWNLOAD_DIR, 30)
        if success:
            print(f"     ✓ 下载成功: {filename}")
            return True, filename
        else:
            print("     ✗ 下载超时")
            return False, None
    else:
        print("     ✗ 导出超时")
        return False, None

def main():
    print("="*60)
    print("豆包批量导出工具 - 修复异步竞态版")
    print("="*60)
    
    if not os.path.exists(INDEX_HTML):
        print(f"错误: 索引文件不存在: {INDEX_HTML}")
        input("按 Enter 退出...")
        return
    
    link_ids = extract_unique_links(INDEX_HTML)
    if not link_ids:
        print("错误: 未找到任何链接")
        input("按 Enter 退出...")
        return
    print(f"找到 {len(link_ids)} 个对话链接")
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(r"h:\github\md\chrome_profile", exist_ok=True)
    
    driver = None
    success_count = 0
    test_count = min(5, len(link_ids))
    needs_login = True
    
    for idx, link_id in enumerate(link_ids[:test_count], 1):
        print(f"\n[{idx}/{test_count}] 处理对话: {link_id}")
        
        try:
            if driver is None or not is_driver_alive(driver):
                print("  [重新启动浏览器]")
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
            
            success, filename = process_single_conversation(driver, link_id)
            if success:
                success_count += 1
            
        except Exception as e:
            print(f"  ✗ 处理失败: {str(e)[:100]}")
            driver = None
    
    print(f"\n{'='*60}")
    print(f"完成！成功导出 {success_count}/{test_count} 个对话")
    print(f"下载目录: {DOWNLOAD_DIR}")
    print("="*60)
    
    if driver:
        input("\n按 Enter 关闭浏览器...")
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()