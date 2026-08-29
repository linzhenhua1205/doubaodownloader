import time
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

print("="*60)
print("Chrome启动测试（带详细错误）")
print("="*60)

chrome_path = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"

options = Options()
options.binary_location = chrome_path
options.add_argument("--start-maximized")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

print("配置完成，正在启动Chrome...")

try:
    driver = webdriver.Chrome(options=options)
    print("✅ Chrome启动成功！")
    
    print("\n打开测试页面...")
    driver.get("https://www.baidu.com")
    time.sleep(3)
    print(f"✅ 页面打开成功！标题: {driver.title}")
    
    print("\n等待5秒后自动关闭...")
    time.sleep(5)
    
    driver.quit()
    print("\n✅ 测试完成，浏览器已关闭")
    
except Exception as e:
    print(f"\n❌ 错误: {e}")
    print("\n错误详情:")
    import traceback
    traceback.print_exc()
    print("\n按Enter退出...")
    input()
    sys.exit(1)

print("\n" + "="*60)
