import sys
import os
import time

print("="*60)
print("          Chrome和Selenium详细测试")
print("="*60)

print(f"\n1. Python版本: {sys.version}")

try:
    import selenium
    print(f"2. Selenium版本: {selenium.__version__}")
except ImportError:
    print("2. Selenium未安装")
    sys.exit(1)

chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe"
print(f"3. Chrome路径: {chrome_path}")
print(f"   路径存在: {os.path.exists(chrome_path)}")

print("\n4. 尝试启动Chrome...")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    print("   创建Options对象...")
    options = Options()
    options.add_argument("--start-maximized")
    options.binary_location = chrome_path
    
    print("   创建WebDriver...")
    driver = webdriver.Chrome(options=options)
    
    print("   ✅ Chrome启动成功！")
    print(f"   当前URL: {driver.current_url}")
    print(f"   窗口标题: {driver.title}")
    
    print("\n   等待5秒...")
    time.sleep(5)
    
    print("   访问豆包官网...")
    driver.get("https://www.doubao.com/chat")
    
    print(f"   ✅ 页面加载完成")
    print(f"   当前URL: {driver.current_url}")
    print(f"   窗口标题: {driver.title}")
    
    print("\n   获取Cookie...")
    cookies = driver.get_cookies()
    print(f"   ✅ 获取到 {len(cookies)} 个Cookie")
    for cookie in cookies[:3]:
        print(f"     - {cookie['name']}: {cookie['value'][:30]}...")
    
    print("\n   等待用户确认...")
    input("   按Enter键关闭浏览器...")
    
    driver.quit()
    print("   ✅ 测试完成！")
        
except Exception as e:
    print(f"   ❌ 错误: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    print("\n   尝试检查常见问题...")
    
    # 检查Chrome版本
    try:
        import subprocess
        result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True)
        print(f"   Chrome版本: {result.stdout.strip()}")
    except:
        print("   无法获取Chrome版本")
    
    # 检查ChromeDriver
    try:
        from selenium.webdriver.chrome.service import Service
        service = Service()
        print(f"   ChromeDriver路径: {service.path}")
    except Exception as ce:
        print(f"   ChromeDriver错误: {ce}")
