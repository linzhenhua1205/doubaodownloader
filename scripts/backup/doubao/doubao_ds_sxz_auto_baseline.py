import os
import sys
import time
import glob

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

def click_select_all(driver):
    """点击全选复选框"""
    try:
        script = '''
            var cb = document.getElementById('dssxz-select-all');
            if (cb && !cb.checked) {
                cb.click();
                return true;
            }
            return cb ? cb.checked : false;
        '''
        result = driver.execute_script(script)
        return result
    except Exception as e:
        print(f"  点击全选失败: {str(e)[:50]}")
        return False

def click_md_export(driver):
    """点击Markdown导出按钮"""
    try:
        script = '''
            var btn = document.querySelector('[data-type="md"]');
            if (btn) {
                btn.click();
                return true;
            }
            return false;
        '''
        result = driver.execute_script(script)
        return result
    except Exception as e:
        print(f"  点击MD按钮失败: {str(e)[:50]}")
        return False

def wait_for_export_complete(driver, timeout=120):
    """等待导出完成（批量模式退出）"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not is_batch_mode_active(driver):
            return True
        time.sleep(1)
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
    
    print("  [步骤3] 点击全选框")
    if not click_select_all(driver):
        print("     ✗ 自动全选失败，请手动勾选")
        input("勾选后按Enter继续...")
    
    print("  [步骤4] 点击Markdown导出按钮")
    if not click_md_export(driver):
        print("     ✗ 自动点击失败，请手动点击")
        input("点击后按Enter继续...")
    
    print("  [步骤5] 等待导出完成")
    if wait_for_export_complete(driver):
        print("     ✓ 导出完成")
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
    print("豆包批量导出工具 - 基于插件分析报告")
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