import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_path = "h:/github/md/chrome-win64/chrome-win64/chrome.exe"

print(f"Chrome路径: {chrome_path}")
print(f"文件存在: {os.path.exists(chrome_path)}")

try:
    options = Options()
    options.binary_location = chrome_path
    options.add_argument("--start-maximized")
    
    print("\n尝试启动Chrome...")
    driver = webdriver.Chrome(options=options)
    
    print("✅ Chrome启动成功！")
    driver.get("https://www.doubao.com/chat")
    print("✅ 已访问豆包官网")
    
    input("按Enter键关闭浏览器...")
    driver.quit()
    print("✅ 测试完成")
    
except Exception as e:
    print(f"❌ 错误: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()