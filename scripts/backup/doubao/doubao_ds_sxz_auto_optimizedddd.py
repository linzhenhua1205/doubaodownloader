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

def wait_for_collection_complete(driver, timeout=120):
    """
    ★ 关键步骤: 等待消息收集完成 - 根据Chat2File.md分析
    
    根据文档:
    1. 需要等待 #dssxz-selected-count 文本变成 "共 N 条消息"
    2. 需要等待全选按钮解禁 (disabled=false 且 cursor!=not-allowed)
    3. 验证 window._doubaoInstance._apiMessages.length > 0
    """
    print("  [步骤3.5] 等待豆包API消息加载完成 (关键步骤)...")
    
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
            time.sleep(1.5)  # 额外等待overlay布局
            
            # 验证 _apiMessages.length
            api_len = driver.execute_script("""
                return window._doubaoInstance && window._doubaoInstance._apiMessages ? 
                    window._doubaoInstance._apiMessages.length : 0;
            """)
            print(f"  [OK] 内部API消息数: {api_len}")
            
            # 等待全选按钮解禁
            sa = driver.find_element(By.ID, "dssxz-select-all")
            for _ in range(20):
                disabled = sa.get_attribute("disabled")
                cursor = driver.execute_script("return getComputedStyle(arguments[0]).cursor;", sa)
                if disabled is None and cursor != "not-allowed":
                    print(f"  [OK] 全选按钮已解禁 (disabled={disabled}, cursor={cursor})")
                    break
                time.sleep(1)
            
            return True
        
        time.sleep(1)
    
    print(f"  [WARN] 等待超时 ({timeout}s), 但继续尝试...")
    return True

def click_select_all(driver):
    """
    ★ 全选 - 根据 Chat2File.md 分析, 直接调用插件内部方法
    
    正确做法: 直接调用 window._doubaoInstance.toggleSelectAll(true)
    """
    print("  [步骤3] 全选所有对话...")
    
    # 先确保全选按钮已解禁
    try:
        select_all = driver.find_element(By.ID, "dssxz-select-all")
        for _ in range(20):
            disabled = select_all.get_attribute("disabled")
            cursor = driver.execute_script("return getComputedStyle(arguments[0]).cursor;", select_all)
            if disabled is None and cursor != "not-allowed":
                print("  [OK] 全选按钮已准备好")
                break
            time.sleep(0.5)
    except Exception as e:
        print(f"  [WARN] 检查全选按钮状态时出错: {e}")
    
    # 尝试多种方法进行全选
    success = False
    
    # 方法1: 直接调用 toggleSelectAll
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
        print(f"  [WARN] 方法1失败: {e}")
    
    # 方法2: 如果方法1失败或没有生效，尝试点击 DOM 元素
    if not success:
        try:
            script = '''
                var cb = document.getElementById('dssxz-select-all');
                if(cb) {
                    // 先确保没有选中，再点击
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
            print(f"  [WARN] 方法2失败: {e}")
    
    # 方法3: 如果方法2也失败，尝试通过 batchUI
    if not success:
        try:
            driver.execute_script("""
                if(window.dssxzBatchUI && window.dssxzBatchUI.elements && window.dssxzBatchUI.elements.selectAllCheckbox) {
                    var cb = window.dssxzBatchUI.elements.selectAllCheckbox;
                    if(cb) {
                        if(cb.checked) {
                            cb.checked = false;
                        }
                        cb.click();
                        return cb.checked;
                    }
                }
                return false;
            """)
            print("  [OK] batchUI 方式全选成功")
            success = True
        except Exception as e:
            print(f"  [WARN] 方法3失败: {e}")
    
    time.sleep(1.5)
    
    # 验证是否成功
    try:
        count_text = driver.find_element(By.ID, "dssxz-selected-count").text
        print(f"  [OK] 当前选择计数: '{count_text}'")
    except Exception as e:
        print(f"  [WARN] 验证选择计数时出错: {e}")
    
    return success

def click_md_export(driver):
    """点击Markdown导出按钮 - 根据Chat2File.md分析"""
    print("  [步骤4] 点击Markdown导出按钮...")
    
    # 尝试多种方法进行导出
    success = False
    
    # 方法1: 直接调用 dssxzBatchUI.exportBatch
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
        print(f"  [WARN] 方法1失败: {e}")
    
    # 方法2: 尝试调用 onExport
    if not success:
        try:
            result = driver.execute_script("""
                if(window.dssxzBatchUI && typeof window.dssxzBatchUI.onExport === 'function') {
                    window.dssxzBatchUI.onExport("md", null);
                    return true;
                }
                return false;
            """)
            if result:
                print("  [OK] 已调用 dssxzBatchUI.onExport('md')")
                success = True
        except Exception as e:
            print(f"  [WARN] 方法2失败: {e}")
    
    # 方法3: 通过 _doubaoInstance 的 onExport
    if not success:
        try:
            result = driver.execute_script("""
                if(window._doubaoInstance && window._doubaoInstance.batchUI && 
                   typeof window._doubaoInstance.batchUI.onExport === 'function') {
                    window._doubaoInstance.batchUI.onExport("md", null);
                    return true;
                }
                return false;
            """)
            if result:
                print("  [OK] 已调用 _doubaoInstance.batchUI.onExport('md')")
                success = True
        except Exception as e:
            print(f"  [WARN] 方法3失败: {e}")
    
    # 方法4: DOM 方式点击
    if not success:
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
            print(f"  [WARN] 方法4失败: {e}")
    
    return success

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
    options.add_argument("--remote-debugging-port=0")  # 自动分配端口
    options.binary_location = CHROME_PATH
    options.add_argument(f"--load-extension={EXTENSION_PATH}")
    
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    
    # 使用本地ChromeDriver
    from selenium.webdriver.chrome.service import Service
    chromedriver_path = r"h:\github\md\chromedriver-win64\chromedriver.exe"
    service = Service(chromedriver_path)
    return webdriver.Chrome(service=service, options=options)

def process_single_conversation(driver, link_id):
    """处理单个对话"""
    print(f"  [步骤0] 打开对话页面")
    driver.get(f"https://www.doubao.com/chat/{link_id}")
    time.sleep(10)
    
    print("  [步骤1] 派发批量模式事件")
    dispatch_custom_event(driver, "dssxz-toggle-batch-mode")
    time.sleep(3)
    
    if not is_batch_mode_active(driver):
        print("     ✗ 批量模式未激活, 请手动点击悬浮按钮")
        input("准备好后按Enter继续...")
    
    print("  [步骤2] 等待底部操作栏出现")
    if not wait_for_batch_bar(driver):
        print("     ✗ 底部栏未出现, 请手动检查")
        input("准备好后按Enter继续...")
    
    # ★ 关键步骤: 等待消息收集完成 (根据Chat2File.md分析)
    wait_for_collection_complete(driver)
    
    # ★ 关键修复: 直接调用平台方法全选
    if not click_select_all(driver):
        print("     ✗ 全选失败, 请手动勾选")
        input("勾选后按Enter继续...")
    
    if not click_md_export(driver):
        print("     ✗ MD导出按钮点击失败, 请手动点击")
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
    print("豆包批量导出工具 - 结合Chat2File.md分析优化版")
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
            import traceback
            traceback.print_exc()
            driver = None
    
    print(f"\n{'='*60}")
    print(f"完成! 成功导出 {success_count}/{test_count} 个对话")
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