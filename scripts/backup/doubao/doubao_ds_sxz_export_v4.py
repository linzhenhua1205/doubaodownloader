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
    print("豆包批量导出工具 - DS随心转插件版 v4.0")
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
            print(f"\n[{idx}/{len(link_ids)}] 处理: {link_id}")
            driver.get(f"https://www.doubao.com/chat/{link_id}")
            time.sleep(8)
            
            print("  1. 触发批量模式")
            try:
                driver.execute_script("""
                    if (window.__doubao) {
                        window.__doubao.toggleBatchMode();
                    } else if (window._doubaoInstance) {
                        window._doubaoInstance.toggleBatchMode();
                    }
                """)
                time.sleep(3)
            except:
                print("     JS触发失败，继续尝试")
            
            print("  2. 等待底部操作栏")
            try:
                WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, 'dssxz-batch-bar-container'))
                )
                print("     底部操作栏已显示")
            except:
                print("     底部操作栏未显示，请手动触发批量模式")
                input("准备好后按Enter继续...")
            
            print("  3. 点击全选框")
            select_all_found = False
            selectors = [
                "//div[@id='dssxz-batch-bar-container']//input[@type='checkbox']",
                "//input[@id='dssxz-select-all']",
                "//input[contains(@class,'select-all')]",
                "//*[contains(text(),'全选')]/../input[@type='checkbox']",
            ]
            for selector in selectors:
                try:
                    checkbox = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if not checkbox.is_selected():
                        checkbox.click()
                    print(f"     [OK] 全选成功: {selector}")
                    select_all_found = True
                    break
                except:
                    continue
            if not select_all_found:
                print("     未找到全选框，请手动勾选")
                input("勾选后按Enter继续...")
            
            print("  4. 点击Markdown导出")
            md_found = False
            selectors = [
                "//*[@id='export-all-md']",
                "//*[contains(text(),'Markdown')]",
                "//button[contains(@class,'markdown')]",
            ]
            for selector in selectors:
                try:
                    md_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    md_btn.click()
                    print(f"     [OK] 导出成功: {selector}")
                    md_found = True
                    break
                except:
                    continue
            if not md_found:
                print("     未找到Markdown按钮，请手动点击")
                input("点击后按Enter继续...")
            
            print("  5. 等待下载")
            success, filename = wait_for_download(DOWNLOAD_DIR, 60)
            if success:
                print(f"     ✅ 下载完成: {filename}")
                success_count += 1
            else:
                print("     ⚠️ 下载超时")
        
        print(f"\n完成！成功导出 {success_count}/{len(link_ids)} 个对话")
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        traceback.print_exc()
    
    finally:
        input("\n按 Enter 关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    main()