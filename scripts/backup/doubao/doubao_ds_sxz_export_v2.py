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
    """检查所有必要路径"""
    errors = []
    
    if not os.path.exists(CHROME_PATH):
        errors.append(f"Chrome路径不存在: {CHROME_PATH}")
    else:
        print(f"✓ Chrome路径有效: {CHROME_PATH}")
    
    if not os.path.exists(EXTENSION_PATH):
        errors.append(f"插件目录不存在: {EXTENSION_PATH}")
    else:
        manifest_path = os.path.join(EXTENSION_PATH, "manifest.json")
        if os.path.exists(manifest_path):
            print(f"✓ 插件目录有效: {EXTENSION_PATH}")
        else:
            errors.append(f"插件目录不完整，缺少manifest.json: {EXTENSION_PATH}")
    
    if not os.path.exists(INDEX_HTML):
        errors.append(f"索引文件不存在: {INDEX_HTML}")
    else:
        print(f"✓ 索引文件存在: {INDEX_HTML}")
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print(f"✓ 下载目录已创建: {DOWNLOAD_DIR}")
    
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

def click_ds_sxz_floating_button(driver):
    selectors = [
        "//div[contains(@class,'ds-sxz-btn')]",
        "//div[contains(@class,'ds-sxz-fab')]",
        "//div[contains(@class,'dssxz-float-btn')]",
        "//div[@class='ds-sxz-btn']",
        "//div[contains(@class,'fab') and contains(@style,'bottom')]",
        "//*[@id='dssxz-float-button']",
        "//div[contains(text(),'DS')]"
    ]
    
    for selector in selectors:
        try:
            btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            btn.click()
            time.sleep(2)
            print(f"  [OK] 使用选择器: {selector}")
            return True
        except:
            continue
    
    return False

def find_and_click_select_all(driver):
    selectors = [
        "//input[@type='checkbox' and contains(@class,'select-all')]",
        "//label[contains(text(),'全选')]/preceding-sibling::input",
        "//label[contains(text(),'全选')]/input",
        "//*[contains(text(),'全选')]/parent::*/input[@type='checkbox']"
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
    selectors = [
        "//button[contains(@class,'markdown')]",
        "//div[contains(@class,'markdown')]",
        "//*[contains(text(),'Markdown')]",
        "//*[contains(@title,'Markdown')]",
        "//*[@data-format='markdown']"
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

def main():
    print("="*60)
    print("豆包批量导出工具 - DS随心转插件版 v2.0")
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
    print(f"✓ 用户数据目录: {user_data_dir}")
    
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
        print(f"  [ERROR] Chrome启动失败: {str(e)[:100]}")
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
        
        print("\n[步骤1/4] 点击DS随心转悬浮按钮")
        if not click_ds_sxz_floating_button(driver):
            print("  [WARN] 未找到悬浮按钮，请手动点击")
            input("点击后按Enter继续...")
        
        print("\n[步骤2/4] 点击全选框")
        if not find_and_click_select_all(driver):
            print("  [WARN] 未找到全选框，请手动勾选")
            input("勾选后按Enter继续...")
        
        print("\n[步骤3/4] 点击Markdown导出")
        if not find_and_click_markdown_export(driver):
            print("  [WARN] 未找到Markdown导出按钮，请手动点击")
            input("点击后按Enter继续...")
        
        print("\n[步骤4/4] 等待下载完成")
        success, filename = wait_for_download(DOWNLOAD_DIR, 120)
        
        if success:
            print(f"\n[SUCCESS] 批量导出成功！")
            print(f"  文件: {filename}")
            print(f"  位置: {DOWNLOAD_DIR}")
            
            files = [f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith('.md')]
            if files:
                print(f"\n[下载列表] 共 {len(files)} 个文件:")
                for f in sorted(files)[-5:]:
                    print(f"  - {f}")
        else:
            print("\n[ERROR] 下载超时")
        
    except Exception as e:
        print(f"\n[ERROR] 发生错误: {str(e)}")
        traceback.print_exc()
    
    finally:
        print("\n[退出]")
        input("按 Enter 关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    main()