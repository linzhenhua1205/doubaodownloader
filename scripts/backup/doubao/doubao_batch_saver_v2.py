import os
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------------------- 配置区 --------------------------
CHROME_PATH = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"
EXTENSION_PATH = r"H:\ext\dssxz"
DOWNLOAD_DIR = r"H:\dl\ai_md_exports"
INDEX_HTML = r"h:\github\md\豆包链接索引.html"
WAIT_SECONDS = 15
# -----------------------------------------------------------

def extract_unique_links(html_file):
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    links = re.findall(r'https://www\.doubao\.com/chat/(\d+)', content)
    unique_links = list(set(links))
    
    print(f"从 {html_file} 中找到 {len(links)} 个链接，去重后 {len(unique_links)} 个")
    
    return sorted(unique_links)

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

def click_ds_sxz_button(driver):
    """点击DS随心转悬浮按钮"""
    selectors = [
        "//div[contains(@class,'ds-sxz')]",
        "//div[contains(@class,'chat2file')]",
        "//button[contains(@class,'ds-sxz')]",
        "//div[@class='ds-sxz-btn']",
        "//*[contains(@class,'fab') and contains(@class,'extension')]",
        "//div[contains(@style,'fixed') and contains(@style,'right') and contains(@style,'bottom')]"
    ]
    
    for selector in selectors:
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            btn.click()
            time.sleep(2)
            return True, f"使用选择器: {selector}"
        except:
            continue
    
    return False, "未找到悬浮按钮"

def select_all_conversations(driver):
    """点击全选框"""
    selectors = [
        "//input[@type='checkbox' and @class='select-all']",
        "//input[@type='checkbox' and contains(@class,'all')]",
        "//label[contains(text(),'全选')]/preceding-sibling::input",
        "//label[contains(text(),'全选')]/input",
        "//*[contains(text(),'全选')]/parent::*/input",
        "//div[contains(@class,'select-all')]/input"
    ]
    
    for selector in selectors:
        try:
            checkbox = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            if not checkbox.is_selected():
                checkbox.click()
                time.sleep(1)
            return True, f"使用选择器: {selector}"
        except:
            continue
    
    return False, "未找到全选框"

def click_markdown_export(driver):
    """点击Markdown导出图标"""
    selectors = [
        "//*[contains(text(),'Markdown') or contains(text(),'markdown')]",
        "//span[contains(@class,'markdown')]",
        "//i[contains(@class,'markdown')]",
        "//button[contains(@class,'markdown')]",
        "//div[contains(@class,'markdown')]",
        "//*[contains(@title,'Markdown')]",
        "//*[contains(@alt,'Markdown')]"
    ]
    
    for selector in selectors:
        try:
            md_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector))
            )
            md_btn.click()
            time.sleep(2)
            return True, f"使用选择器: {selector}"
        except:
            continue
    
    return False, "未找到Markdown导出按钮"

def batch_export_with_extension(driver, download_dir):
    """使用插件批量导出"""
    try:
        print("\n🔍 尝试点击DS随心转按钮...")
        success, msg = click_ds_sxz_button(driver)
        if not success:
            print(f"❌ {msg}")
            return False, msg
        
        print(f"✅ {msg}")
        
        print("\n🔍 尝试点击全选框...")
        success, msg = select_all_conversations(driver)
        if not success:
            print(f"❌ {msg}")
            return False, msg
        
        print(f"✅ {msg}")
        
        print("\n🔍 尝试点击Markdown导出...")
        success, msg = click_markdown_export(driver)
        if not success:
            print(f"❌ {msg}")
            return False, msg
        
        print(f"✅ {msg}")
        
        print("\n⏳ 等待下载完成...")
        success, filename = wait_for_download(download_dir, 60)
        if success:
            return True, f"批量导出成功: {filename}"
        else:
            return False, "下载超时"
            
    except Exception as e:
        return False, str(e)

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
    
    link_ids = extract_unique_links(INDEX_HTML)
    
    if not link_ids:
        print("❌ 未找到任何链接")
        return
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    user_data_dir = r"h:\github\md\chrome_profile"
    os.makedirs(user_data_dir, exist_ok=True)
    
    print("="*60)
    print("豆包批量导出工具 - 插件批量模式")
    print("="*60)
    print(f"Chrome路径: {CHROME_PATH}")
    print(f"插件路径: {EXTENSION_PATH}")
    print(f"下载目录: {DOWNLOAD_DIR}")
    print(f"用户数据目录: {user_data_dir}")
    print(f"链接数量: {len(link_ids)}")
    print("="*60)
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-popup-blocking")
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
        time.sleep(5)
        
        print("\n" + "=" * 40)
        print("请执行以下操作：")
        print("1. 在弹出的浏览器窗口中登录你的豆包账号")
        print("2. 确保DS随心转插件已加载（检查右上角扩展图标）")
        print("3. 输入插件密码（如有）")
        print("4. 按 Enter 继续批量导出...")
        print("=" * 40)
        input()
        
        print("\n🚀 开始批量导出...")
        print("插件将自动：点击悬浮按钮 → 全选对话 → 导出Markdown")
        
        success, msg = batch_export_with_extension(driver, DOWNLOAD_DIR)
        
        if success:
            print(f"\n🎉 {msg}")
            print(f"📁 导出文件保存在: {DOWNLOAD_DIR}")
            
            # 检查下载的文件
            files = [f for f in os.listdir(DOWNLOAD_DIR) if f.lower().endswith('.md')]
            if files:
                print("\n📋 下载的文件列表：")
                for f in sorted(files)[-5:]:  # 显示最后5个
                    print(f"  - {f}")
        else:
            print(f"\n❌ 批量导出失败: {msg}")
            print("\n💡 请尝试手动操作：")
            print("   1. 点击页面右下角的DS随心转悬浮按钮")
            print("   2. 在弹出的面板中勾选底部的全选框")
            print("   3. 点击Markdown图标进行导出")
        
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