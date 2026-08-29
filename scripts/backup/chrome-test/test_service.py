import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

CHROME_PATH = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"

print("="*60)
print("使用Service测试Chrome启动")
print("="*60)

options = Options()
options.binary_location = CHROME_PATH
options.add_argument("--start-maximized")

print("正在通过Service启动Chrome...")
try:
    driver = webdriver.Chrome(options=options)
    print("[OK] Chrome启动成功！")
    
    print("\n打开百度测试...")
    driver.get("https://www.baidu.com")
    time.sleep(3)
    print(f"[OK] 当前页面标题: {driver.title}")
    
    print("\n请手动操作，按 Enter 退出...")
    input()
    
    driver.quit()
    print("[OK] 浏览器已关闭")
    
except Exception as e:
    print(f"\n[ERROR] 发生错误: {e}")
    import traceback
    traceback.print_exc()
    input("\n按 Enter 退出...")
