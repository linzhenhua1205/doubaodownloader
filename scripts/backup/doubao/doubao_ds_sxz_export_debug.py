import os
import sys
import time

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

def debug_page_elements(driver):
    print("\n[调试信息] 页面元素扫描:")
    
    elements_info = []
    
    try:
        containers = driver.find_elements(By.XPATH, "//div[contains(@id,'dssxz') or contains(@class,'dssxz')]")
        print(f"\n1. dssxz相关元素 ({len(containers)}个):")
        for i, el in enumerate(containers[:10], 1):
            info = f"   {i}. id='{el.get_attribute('id')}' class='{el.get_attribute('class')[:50]}'"
            print(info)
            elements_info.append(info)
    except Exception as e:
        print(f"   扫描失败: {str(e)}")
    
    try:
        batch_bars = driver.find_elements(By.ID, "dssxz-batch-bar-container")
        print(f"\n2. 底部操作栏 ({len(batch_bars)}个):")
        for i, el in enumerate(batch_bars, 1):
            print(f"   {i}. 显示状态: {el.is_displayed()}")
            print(f"      innerHTML前200字符: {el.get_attribute('innerHTML')[:200]}")
    except Exception as e:
        print(f"   扫描失败: {str(e)}")
    
    try:
        checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
        print(f"\n3. 复选框元素 ({len(checkboxes)}个):")
        for i, el in enumerate(checkboxes[:10], 1):
            info = f"   {i}. id='{el.get_attribute('id')}' class='{el.get_attribute('class')}'"
            print(info)
    except Exception as e:
        print(f"   扫描失败: {str(e)}")
    
    try:
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(),'Markdown') or contains(text(),'全选')]")
        print(f"\n4. 包含关键字的元素 ({len(buttons)}个):")
        for i, el in enumerate(buttons, 1):
            info = f"   {i}. text='{el.text}' tag='{el.tag_name}' class='{el.get_attribute('class')[:30]}'"
            print(info)
    except Exception as e:
        print(f"   扫描失败: {str(e)}")
    
    try:
        scripts = driver.execute_script("""
            var info = [];
            if (window.__doubao) info.push('window.__doubao: 存在');
            if (window._doubaoInstance) info.push('window._doubaoInstance: 存在');
            if (window.DoubaoPlatform) info.push('window.DoubaoPlatform: 存在');
            return info;
        """)
        print(f"\n5. JS对象检查:")
        for item in scripts:
            print(f"   {item}")
    except Exception as e:
        print(f"   JS检查失败: {str(e)}")
    
    return elements_info

def main():
    print("="*60)
    print("豆包批量导出工具 - 调试版")
    print("="*60)
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-data-dir={r'h:\github\md\chrome_profile'}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-popup-blocking")
    options.binary_location = CHROME_PATH
    options.add_argument(f"--load-extension={EXTENSION_PATH}")
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Chrome启动失败: {str(e)}")
        input("按 Enter 退出...")
        return
    
    try:
        driver.get("https://www.doubao.com/chat/")
        time.sleep(8)
        
        print("\n请登录豆包账号并手动触发批量模式，然后按 Enter 继续...")
        input()
        
        print("\n" + "="*40)
        print("调试信息 - 请查看页面上的元素")
        print("="*40)
        debug_page_elements(driver)
        
        print("\n请手动检查页面，然后按 Enter 关闭浏览器...")
        input()
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()