import sys
import os
import subprocess

print("="*60)
print("检查Chrome和ChromeDriver信息")
print("="*60)

# 检查Chrome版本
chrome_path = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"
if os.path.exists(chrome_path):
    try:
        result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"Chrome版本: {result.stdout.strip()}")
        else:
            print(f"Chrome版本检查失败，返回码: {result.returncode}")
    except Exception as e:
        print(f"检查Chrome版本时出错: {e}")
else:
    print(f"Chrome不存在: {chrome_path}")

print()

# 检查Selenium版本
try:
    import selenium
    print(f"Selenium版本: {selenium.__version__}")
    
    # 尝试使用Selenium获取ChromeDriver
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    print("Selenium已导入")
    
    # 尝试获取ChromeDriver信息
    from selenium.webdriver.chrome.service import Service
    print("Service已导入")
    
except Exception as e:
    print(f"Selenium相关导入错误: {e}")
    import traceback
    traceback.print_exc()

print()
print("="*60)
