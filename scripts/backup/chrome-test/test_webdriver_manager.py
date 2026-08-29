import time
import sys
print("="*60)
print("测试WebDriverManager")
print("="*60)

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    print("✅ Selenium导入成功")
    
    # 尝试使用webdriver-manager
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ WebDriverManager导入成功")
        
        chrome_path = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"
        options = Options()
        options.binary_location = chrome_path
        options.add_argument("--start-maximized")
        
        print("\n正在获取ChromeDriver...")
        service = webdriver.chrome.service.Service(ChromeDriverManager().install())
        print("✅ ChromeDriver获取成功")
        
        print("\n正在启动Chrome...")
        driver = webdriver.Chrome(service=service, options=options)
        print("✅ Chrome启动成功！")
        
        driver.get("https://www.baidu.com")
        print(f"✅ 页面打开成功！标题: {driver.title}")
        
        time.sleep(5)
        driver.quit()
        print("\n✅ 测试完成")
        
    except ImportError as e:
        print(f"❌ WebDriverManager未安装: {e}")
        print("请运行: pip install webdriver-manager")
        print("\n尝试不使用WebDriverManager直接启动...")
        
        chrome_path = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"
        options = Options()
        options.binary_location = chrome_path
        options.add_argument("--start-maximized")
        
        print("\n正在启动Chrome...")
        driver = webdriver.Chrome(options=options)
        print("✅ Chrome启动成功！")
        
        driver.get("https://www.baidu.com")
        print(f"✅ 页面打开成功！标题: {driver.title}")
        
        time.sleep(5)
        driver.quit()
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    input("\n按Enter退出...")
    sys.exit(1)

print("\n" + "="*60)
