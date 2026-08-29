import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("="*60)
print("测试系统Chrome（不设置binary_location）")
print("="*60)

options = Options()
options.add_argument("--start-maximized")

print("正在启动系统Chrome...")
try:
    driver = webdriver.Chrome(options=options)
    print("[OK] 系统Chrome启动成功！")
    
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
