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

# -------------------------- 配置区 --------------------------
CHROME_PATH = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"
EXTENSION_PATH = r"h:\github\md\dssxz"
DOWNLOAD_DIR = r"H:\dl\ai_md_exports"
INDEX_HTML = r"h:\github\md\豆包链接索引.html"
WAIT_SECONDS = 15
# -----------------------------------------------------------

def check_paths():
    errors = []
    
    if not os.path.exists(CHROME_PATH):
        errors.append(f"Chrome路径不存在: {CHROME_PATH}")
    else:
        print(f"[OK] Chrome路径有效: {CHROME_PATH}")
    
    if not os.path.exists(EXTENSION_PATH):
        errors.append(f"插件目录不存在: {EXTENSION_PATH}")
    else:
        manifest_path = os.path.join(EXTENSION_PATH, "manifest.json")
        if os.path.exists(manifest_path):
            print(f"[OK] 插件目录有效: {EXTENSION_PATH}")
        else:
            errors.append(f"插件目录不完整，缺少manifest.json: {EXTENSION_PATH}")
    
    if not os.path.exists(INDEX_HTML):
        errors.append(f"索引文件不存在: {INDEX_HTML}")
    else:
        print(f"[OK] 索引文件存在: {INDEX_HTML}")
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print(f"[OK] 下载目录已创建: {DOWNLOAD_DIR}")
    
    return errors

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

def trigger_batch_mode(driver):
    print("  [步骤1/4] 触发批量模式")
    
    js_scripts = [
        "if (window.__doubao && window.__doubao.toggleBatchMode) { window.__doubao.toggleBatchMode(); }",
        "if (window._doubaoInstance && window._doubaoInstance.toggleBatchMode) { window._doubaoInstance.toggleBatchMode(); }",
        "if (window.doubaoPlatform && window.doubaoPlatform.toggleBatchMode) { window.doubaoPlatform.toggleBatchMode(); }",
    ]
    
    for script in js_scripts:
        try:
            driver.execute_script(script)
            time.sleep(3)
            
            try:
                batch_bar = driver.find_element(By.ID, 'dssxz-batch-bar-container')
                if batch_bar.is_displayed():
                    print(f"  [OK] 通过JS脚本触发成功")
                    return True
            except:
                pass
        except:
            continue
    
    selectors = [
        "//div[@id='custom-popup']",
        "//div[contains(@class,'dssxz-sidebar-btn')]",
        "//div[contains(@class,'dssxz-export-container')]",
        "//div[contains(@class,'dssxz-split-button-wrapper')]",
        "//div[contains(@class,'ds-sxz-btn')]",
    ]
    
    for selector in selectors:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            btn.click()
            time.sleep(3)
            
            batch_bar = driver.find_element(By.ID, 'dssxz-batch-bar-container')
            if batch_bar.is_displayed():
                print(f"  [OK] 使用选择器: {selector}")
                return True
        except:
            continue
    
    return False

def wait_for_batch_bar(driver):
    print("  [步骤2/4] 等待底部操作栏显示")
    try:
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, 'dssxz-batch-bar-container'))
        )
        print("  [OK] 底部操作栏已显示")
        return True
    except:
        return False

def find_and_click_select_all(driver):
    print("  [步骤3/4] 点击全选框")
    
    selectors = [
        "//input[@type='checkbox' and contains(@class,'select-all')]",
        "//input[@type='checkbox' and @id='dssxz-select-all']",
        "//div[@id='dssxz-batch-bar-container']//input[@type='checkbox']",
        "//div[contains(@class,'batch-bar')]//input[@type='checkbox']",
        "//*[contains(text(),'全选')]/parent::*/input[@type='checkbox']",
        "//label[contains(text(),'全选')]/preceding-sibling::input",
        "//label[contains(text(),'全选')]/input",
    ]
    
    for selector in selectors:
        try:
            checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            if not checkbox.is_selected():
                checkbox.click()
                time.sleep(1)
            print(f"  [OK] 使用选择器: {selector}")
            return True
        except:
            continue
    
    return False

def find_and_click_markdown_export(driver):
    print("  [步骤4/4] 点击Markdown导出")
    
    selectors = [
        "//*[@id='export-all-md']",
        "//*[contains(text(),'Markdown')]",
        "//*[contains(@title,'Markdown')]",
        "//button[contains(@class,'markdown')]",
        "//div[contains(@class,'markdown')]",
        "//*[contains(@class,'export') and contains(text(),'Markdown')]",
        "//div[contains(@class,'dssxz-template-popup')]//*[contains(text(),'Markdown')]",
    ]
    
    for selector in selectors:
        try:
            md_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            md_btn.click()
            time.sleep(2)
            print(f"  [OK] 使用选择器: {selector}")
            return True
        except:
            continue
    
    return False

def extract_unique_links(html_file):
    import re
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    links = re.findall(r'https://www\.doubao\.com/chat/(\d+)', content)
    unique_links = list(set(links))
    
    print(f"从索引文件中找到 {len(links)} 个链接，去重后 {len(unique_links)} 个")
    
    return sorted(unique_links)

def main():
    print("="*60)
    print("豆包批量导出工具 - DS随心转插件版 v3.0")
    print("="*60)
    
    print("\n[检查配置]")
    errors = check_paths()
    
    if errors:
        print("\n[错误] 配置检查失败:")
        for error in errors:
            print(f"  - {error}")
        print("\n请修复以上问题后重新运行")
        input("按 Enter 退出...")
        return
    
    user_data_dir = r"h:\github\md\chrome_profile"
    os.makedirs(user_data_dir, exist_ok=True)
    print(f"[OK] 用户数据目录: {user_data_dir}")
    
    link_ids = extract_unique_links(INDEX_HTML)
    if not link_ids:
        print("\n[错误] 未找到任何链接")
        input("按 Enter 退出...")
        return
    
    print(f"\n[OK] 共找到 {len(link_ids)} 个对话链接")
    
    print("\n[配置Chrome选项]")
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-data-dir={user_data_dir}")
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
    
    print("\n[启动Chrome浏览器]")
    try:
        driver = webdriver.Chrome(options=options)
        print("  [OK] Chrome启动成功")
    except Exception as e:
        print(f"  [ERROR] Chrome启动失败: {str(e)[:150]}")
        print("\n可能的解决方案:")
        print("  1. 检查Chrome路径是否正确")
        print("  2. 确保已安装与Chrome版本匹配的chromedriver")
        print("  3. 关闭所有Chrome窗口后重试")
        input("\n按 Enter 退出...")
        return
    
    try:
        print("\n[打开豆包页面]")
        driver.get("https://www.doubao.com/chat/")
        time.sleep(8)
        print("  [OK] 页面加载完成")
        
        print("\n" + "=" * 40)
        print("请执行以下操作：")
        print("1. 在弹出的浏览器窗口中登录你的豆包账号")
        print("2. 确保DS随心转插件已加载（检查右上角扩展图标）")
        print("3. 输入插件密码（如有）")
        print("4. 按 Enter 继续批量导出...")
        print("=" * 40)
        input()
        
        success_count = 0
        
        for idx, link_id in enumerate(link_ids, 1):
            print(f"\n[{idx}/{len(link_ids)}] 正在处理: {link_id}")
            
            try:
                driver.get(f"https://www.doubao.com/chat/{link_id}")
                time.sleep(8)
                
                if not trigger_batch_mode(driver):
                    print("  [WARN] 未能自动触发批量模式，请手动点击悬浮按钮")
                    input("点击后按Enter继续...")
                
                if not wait_for_batch_bar(driver):
                    print("  [WARN] 底部操作栏未显示，请手动触发批量模式")
                    input("准备好后按Enter继续...")
                
                if not find_and_click_select_all(driver):
                    print("  [WARN] 未找到全选框，请手动勾选")
                    input("勾选后按Enter继续...")
                
                if not find_and_click_markdown_export(driver):
                    print("  [WARN] 未找到Markdown导出按钮，请手动点击")
                    input("点击后按Enter继续...")
                
                print("  等待下载...")
                success, filename = wait_for_download(DOWNLOAD_DIR, 60)
                
                if success:
                    print(f"  ✅ 导出成功: {filename}")
                    success_count += 1
                else:
                    print(f"  ⚠️ 下载超时")
                
            except Exception as e:
                print(f"  ❌ 处理失败: {str(e)[:100]}")
        
        print(f"\n" + "=" * 60)
        print(f"完成！成功导出 {success_count}/{len(link_ids)} 个对话")
        print("=" * 60)
        
        files = [f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith('.md')]
        if files:
            print(f"\n[下载列表] 共 {len(files)} 个文件:")
            for f in sorted(files)[-10:]:
                print(f"  - {f}")
            print(f"  更多文件请查看: {DOWNLOAD_DIR}")
        
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {str(e)}")
        traceback.print_exc()
    
    finally:
        print("\n[退出]")
        input("按 Enter 关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    main()