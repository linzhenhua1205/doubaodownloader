import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"
EXTENSION_PATH = r"h:\github\md\dssxz"

print("="*60)
print("Chrome启动测试")
print("="*60)

options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-gpu")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")
options.binary_location = CHROME_PATH
options.add_argument(f"--load-extension={EXTENSION_PATH}")

print("正在启动Chrome...")
try:
    driver = webdriver.Chrome(options=options)
    print("[OK] Chrome启动成功！")
    
    print("\n打开豆包网站...")
    driver.get("https://www.doubao.com/chat/")
    time.sleep(5)
    print(f"[OK] 当前页面标题: {driver.title}")
    
    print("\n请手动完成:")
    print("1. 登录豆包账号")
    print("2. 检查右下角DS随心转插件是否加载")
    input("\n按 Enter 退出...")
    
    driver.quit()
    print("[OK] 浏览器已关闭")
    
except Exception as e:
    print(f"\n[ERROR] 发生错误: {e}")
    import traceback
    traceback.print_exc()
    input("\n按 Enter 退出...")
