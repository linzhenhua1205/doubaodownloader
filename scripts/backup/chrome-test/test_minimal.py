import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"

print("="*60)
print("最简化Chrome启动测试")
print("="*60)

options = Options()
options.binary_location = CHROME_PATH

print("正在启动Chrome（不带用户数据、不带插件、不带额外参数）...")
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
