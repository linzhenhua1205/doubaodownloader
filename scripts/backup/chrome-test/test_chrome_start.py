import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = "h:/github/md/chrome-win64/chrome-win64/chrome.exe"

def test_chrome():
    print(f"Chrome路径: {CHROME_PATH}")
    print(f"文件存在: {os.path.exists(CHROME_PATH)}")
    
    if os.path.exists(CHROME_PATH):
        print("\n尝试启动Chrome...")
        
        options = Options()
        options.binary_location = CHROME_PATH
        options.add_argument("--start-maximized")
        
        try:
            driver = webdriver.Chrome(options=options)
            print("✅ Chrome启动成功！")
            driver.get("https://www.baidu.com")
            print(f"✅ 页面标题: {driver.title}")
            driver.quit()
            print("✅ 测试完成")
        except Exception as e:
            print(f"❌ 启动失败: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Chrome路径不存在")

if __name__ == "__main__":
    test_chrome()