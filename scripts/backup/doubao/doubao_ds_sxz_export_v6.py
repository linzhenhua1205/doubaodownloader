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
    print("豆包批量导出工具 - DS随心转插件版 v6.0")
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
            
            print("  [步骤1] 切换到批量模式")
            batch_mode_success = False
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
                print(f"     JS调用结果: {result}")
                time.sleep(3)
                
                batch_bar = driver.find_element(By.ID, 'dssxz-batch-bar-container')
                if batch_bar.is_displayed():
                    print("     ✓ 批量模式已激活，底部操作栏显示")
                    batch_mode_success = True
            except Exception as e:
                print(f"     JS调用失败: {str(e)[:50]}")
            
            if not batch_mode_success:
                print("     ✗ 自动切换失败，请手动点击悬浮按钮")
                input("点击后按Enter继续...")
            
            print("  [步骤2] 全选所有消息")
            select_all_success = False
            try:
                driver.execute_script("""
                    if (window.__doubao && typeof window.__doubao.toggleSelectAll === 'function') {
                        window.__doubao.toggleSelectAll(true);
                    } else if (window._doubaoInstance && typeof window._doubaoInstance.toggleSelectAll === 'function') {
                        window._doubaoInstance.toggleSelectAll(true);
                    }
                """)
                time.sleep(2)
                print("     ✓ 通过JS调用全选成功")
                select_all_success = True
            except Exception as e:
                print(f"     JS调用全选失败: {str(e)[:50]}")
            
            if not select_all_success:
                try:
                    checkboxes = driver.find_elements(By.XPATH, "//div[@id='dssxz-batch-bar-container']//input[@type='checkbox']")
                    if checkboxes:
                        checkbox = checkboxes[0]
                        if not checkbox.is_selected():
                            checkbox.click()
                        print("     ✓ 通过点击全选框成功")
                        select_all_success = True
                except Exception as e:
                    print(f"     点击全选框失败: {str(e)[:50]}")
            
            if not select_all_success:
                print("     ✗ 自动全选失败，请手动勾选全选框")
                input("勾选后按Enter继续...")
            
            print("  [步骤3] 导出为Markdown")
            export_success = False
            try:
                driver.execute_script("""
                    if (window.__doubao && window.__doubao.batchUI) {
                        window.__doubao.batchUI.exportBatch(window.__doubao.selectedMessages, window.__doubao.config, 'markdown', {});
                    } else if (window._doubaoInstance && window._doubaoInstance.batchUI) {
                        window._doubaoInstance.batchUI.exportBatch(window._doubaoInstance.selectedMessages, window._doubaoInstance.config, 'markdown', {});
                    }
                """)
                time.sleep(2)
                print("     ✓ 通过JS调用导出成功")
                export_success = True
            except Exception as e:
                print(f"     JS调用导出失败: {str(e)[:50]}")
            
            if not export_success:
                try:
                    md_btn = driver.find_element(By.ID, 'export-all-md')
                    md_btn.click()
                    print("     ✓ 通过点击导出按钮成功")
                    export_success = True
                except Exception as e:
                    print(f"     点击导出按钮失败: {str(e)[:50]}")
            
            if not export_success:
                try:
                    md_btn = driver.find_element(By.XPATH, "//*[contains(text(),'Markdown')]")
                    md_btn.click()
                    print("     ✓ 通过文本查找点击导出按钮成功")
                    export_success = True
                except Exception as e:
                    print(f"     通过文本查找失败: {str(e)[:50]}")
            
            if not export_success:
                print("     ✗ 自动导出失败，请手动点击Markdown导出按钮")
                input("点击后按Enter继续...")
            
            print("  [步骤4] 等待下载完成")
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