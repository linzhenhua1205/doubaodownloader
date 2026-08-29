import os
import sys
import time
import traceback

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

def check_paths():
    if not os.path.exists(CHROME_PATH):
        print(f"错误: Chrome路径不存在: {CHROME_PATH}")
        return False
    if not os.path.exists(EXTENSION_PATH):
        print(f"错误: 插件目录不存在: {EXTENSION_PATH}")
        return False
    if not os.path.exists(INDEX_HTML):
        print(f"错误: 索引文件不存在: {INDEX_HTML}")
        return False
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    return True

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

def main():
    print("="*60)
    print("豆包批量导出工具 - DS随心转插件版 v5.0")
    print("="*60)
    
    if not check_paths():
        input("按 Enter 退出...")
        return
    
    link_ids = extract_unique_links(INDEX_HTML)
    if not link_ids:
        print("错误: 未找到任何链接")
        input("按 Enter 退出...")
        return
    print(f"找到 {len(link_ids)} 个对话链接")
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
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
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Chrome启动失败: {str(e)[:100]}")
        input("按 Enter 退出...")
        return
    
    try:
        driver.get("https://www.doubao.com/chat/")
        time.sleep(8)
        
        print("\n请登录豆包账号并确保插件已加载，然后按 Enter 继续...")
        input()
        
        success_count = 0
        
        for idx, link_id in enumerate(link_ids, 1):
            print(f"\n[{idx}/{len(link_ids)}] 处理对话: {link_id}")
            
            driver.get(f"https://www.doubao.com/chat/{link_id}")
            time.sleep(10)
            
            print("  步骤1: 调用toggleBatchMode()切换批量模式")
            try:
                result = driver.execute_script("""
                    if (window.__doubao && typeof window.__doubao.toggleBatchMode === 'function') {
                        window.__doubao.toggleBatchMode();
                        return 'success';
                    } else if (window._doubaoInstance && typeof window._doubaoInstance.toggleBatchMode === 'function') {
                        window._doubaoInstance.toggleBatchMode();
                        return 'success';
                    }
                    return 'failed';
                """)
                print(f"     JS执行结果: {result}")
                time.sleep(3)
            except Exception as e:
                print(f"     JS执行失败: {str(e)[:50]}")
            
            print("  步骤2: 等待底部操作栏出现")
            try:
                WebDriverWait(driver, 15).until(
                    EC.visibility_of_element_located((By.ID, 'dssxz-batch-bar-container'))
                )
                print("     ✓ 底部操作栏已显示")
            except:
                print("     ✗ 底部操作栏未自动显示")
                print("     请手动点击悬浮按钮触发批量模式")
                input("准备好后按Enter继续...")
            
            print("  步骤3: 点击全选按钮")
            try:
                checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@id='dssxz-batch-bar-container']//input[@type='checkbox']"))
                )
                if not checkbox.is_selected():
                    checkbox.click()
                print("     ✓ 全选成功")
            except Exception as e:
                print(f"     ✗ 自动全选失败: {str(e)[:50]}")
                print("     请手动勾选全选框")
                input("勾选后按Enter继续...")
            
            print("  步骤4: 点击Markdown导出按钮")
            try:
                md_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, 'export-all-md'))
                )
                md_btn.click()
                print("     ✓ Markdown导出按钮已点击")
            except Exception as e:
                print(f"     ✗ 自动导出失败: {str(e)[:50]}")
                print("     请手动点击Markdown导出按钮")
                input("点击后按Enter继续...")
            
            print("  步骤5: 等待下载完成")
            success, filename = wait_for_download(DOWNLOAD_DIR, 60)
            if success:
                print(f"     ✓ 下载成功: {filename}")
                success_count += 1
            else:
                print("     ✗ 下载超时")
        
        print(f"\n{'='*60}")
        print(f"完成！成功导出 {success_count}/{len(link_ids)} 个对话")
        print(f"下载目录: {DOWNLOAD_DIR}")
        print("="*60)
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        traceback.print_exc()
    
    finally:
        input("\n按 Enter 关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    main()