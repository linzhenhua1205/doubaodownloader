import os
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# -------------------------- 配置区 --------------------------
CHROME_PATH = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"
EXTENSION_PATH = r"h:\github\md\dssxz"
DOWNLOAD_DIR = r"H:\dl\ai_md_exports"
INDEX_HTML = r"h:\github\md\豆包链接索引.html"
WAIT_SECONDS = 15
# -----------------------------------------------------------

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
    """点击DS随心转悬浮按钮"""
    selectors = [
        "//div[contains(@class,'ds-sxz-btn')]",
        "//div[contains(@class,'ds-sxz-fab')]",
        "//div[contains(@class,'dssxz-float-btn')]",
        "//div[@class='ds-sxz-btn']",
        "//div[contains(@class,'fab') and contains(@style,'bottom') and contains(@style,'right')]",
        "//div[contains(@class,'extension-float-btn')]",
        "//*[@id='dssxz-float-button']",
        "//div[contains(text(),'DS') or contains(text(),'随心转')]"
    ]
    
    for selector in selectors:
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            btn.click()
            time.sleep(2)
            print(f"✅ 成功点击悬浮按钮，选择器: {selector}")
            return True
        except Exception as e:
            print(f"  尝试选择器 '{selector}' 失败: {str(e)[:30]}")
            continue
    
    return False

def find_and_click_select_all(driver):
    """点击全选框"""
    selectors = [
        "//input[@type='checkbox' and @class='dssxz-select-all']",
        "//input[@type='checkbox' and contains(@class,'select-all')]",
        "//label[contains(text(),'全选')]/preceding-sibling::input",
        "//label[contains(text(),'全选')]/input",
        "//*[contains(text(),'全选')]/parent::*/input[@type='checkbox']",
        "//div[contains(@class,'select-all')]/input[@type='checkbox']",
        "//span[contains(text(),'全选')]/preceding-sibling::input",
        "//*[@data-action='select-all']"
    ]
    
    for selector in selectors:
        try:
            checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            if not checkbox.is_selected():
                checkbox.click()
                time.sleep(1)
            print(f"✅ 成功点击全选框，选择器: {selector}")
            return True
        except Exception as e:
            print(f"  尝试选择器 '{selector}' 失败: {str(e)[:30]}")
            continue
    
    return False

def find_and_click_markdown_export(driver):
    """点击Markdown导出按钮"""
    selectors = [
        "//button[contains(@class,'dssxz-export-md')]",
        "//span[contains(@class,'dssxz-markdown')]",
        "//i[contains(@class,'markdown')]",
        "//button[contains(@class,'markdown')]",
        "//div[contains(@class,'markdown')]",
        "//*[contains(text(),'Markdown') or contains(text(),'markdown')]",
        "//*[contains(@title,'Markdown')]",
        "//*[@data-format='markdown']",
        "//*[@data-action='export-markdown']",
        "//div[contains(@class,'export-btn') and contains(@class,'markdown')]"
    ]
    
    for selector in selectors:
        try:
            md_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            md_btn.click()
            time.sleep(2)
            print(f"✅ 成功点击Markdown导出，选择器: {selector}")
            return True
        except Exception as e:
            print(f"  尝试选择器 '{selector}' 失败: {str(e)[:30]}")
            continue
    
    return False

def execute_js_click(driver, js_code):
    """执行JavaScript点击"""
    try:
        result = driver.execute_script(js_code)
        time.sleep(2)
        return result
    except Exception as e:
        return None

def trigger_export_via_js(driver):
    """通过JavaScript触发导出"""
    scripts = [
        "document.querySelector('.ds-sxz-btn')?.click()",
        "document.querySelector('[class*=\"ds-sxz\"]')?.click()",
        "document.querySelectorAll('[class*=\"fab\"]').forEach(el => el.click())",
        "window.dssxz?.showPopup?.()"
    ]
    
    for script in scripts:
        result = execute_js_click(driver, script)
        if result is not None:
            print(f"✅ 通过JS触发成功")
            return True
    
    return False

def main():
    if not os.path.exists(INDEX_HTML):
        print(f"错误: 文件不存在 {INDEX_HTML}")
        return
    
    if not os.path.exists(CHROME_PATH):
        print(f"错误: Chrome不存在 {CHROME_PATH}")
        return
    
    if not os.path.exists(EXTENSION_PATH):
        print(f"错误: 插件目录不存在 {EXTENSION_PATH}")
        return
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    user_data_dir = r"h:\github\md\chrome_profile"
    os.makedirs(user_data_dir, exist_ok=True)
    
    print("="*60)
    print("豆包批量导出工具 - DS随心转插件版")
    print("="*60)
    print(f"Chrome路径: {CHROME_PATH}")
    print(f"插件路径: {EXTENSION_PATH}")
    print(f"下载目录: {DOWNLOAD_DIR}")
    print(f"用户数据目录: {user_data_dir}")
    print("="*60)
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--ignore-certificate-errors")
    options.binary_location = CHROME_PATH
    
    # 加载插件
    options.add_argument(f"--load-extension={EXTENSION_PATH}")
    
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    
    print("\n🔄 正在启动Chrome浏览器...")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.doubao.com/chat/")
        time.sleep(8)
        
        print("\n" + "=" * 40)
        print("请执行以下操作：")
        print("1. 在弹出的浏览器窗口中登录你的豆包账号")
        print("2. 确保DS随心转插件已加载（检查右上角扩展图标）")
        print("3. 输入插件密码（如有）")
        print("4. 按 Enter 继续批量导出...")
        print("=" * 40)
        input()
        
        print("\n🚀 开始批量导出流程...")
        
        print("\n1️⃣ 尝试点击DS随心转悬浮按钮...")
        success = click_ds_sxz_floating_button(driver)
        if not success:
            print("⚠️ XPath点击失败，尝试JavaScript方式...")
            success = trigger_export_via_js(driver)
        
        if not success:
            print("❌ 未能触发悬浮按钮，请手动点击")
            input("点击后按Enter继续...")
        
        print("\n2️⃣ 尝试点击全选框...")
        success = find_and_click_select_all(driver)
        if not success:
            print("❌ 未能找到全选框，请手动勾选")
            input("勾选后按Enter继续...")
        
        print("\n3️⃣ 尝试点击Markdown导出...")
        success = find_and_click_markdown_export(driver)
        if not success:
            print("❌ 未能找到Markdown导出按钮，请手动点击")
            input("点击后按Enter继续...")
        
        print("\n4️⃣ 等待下载完成...")
        success, filename = wait_for_download(DOWNLOAD_DIR, 120)
        
        if success:
            print(f"\n🎉 批量导出成功！")
            print(f"📁 导出文件: {filename}")
            print(f"📂 保存位置: {DOWNLOAD_DIR}")
            
            files = [f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith('.md')]
            if files:
                print("\n📋 下载的文件列表：")
                for f in sorted(files)[-10:]:
                    print(f"  - {f}")
        else:
            print("\n❌ 下载超时")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n按 Enter 退出...")
        input()
        driver.quit()

if __name__ == "__main__":
    main()