import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

EXTENSION_PATH = r"H:\ext\dssxz"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

print("="*60)
print("测试Chrome扩展加载")
print("="*60)

# 检查扩展目录
if not os.path.exists(EXTENSION_PATH):
    print(f"❌ 扩展目录不存在: {EXTENSION_PATH}")
    exit(1)

manifest_path = os.path.join(EXTENSION_PATH, "manifest.json")
if not os.path.exists(manifest_path):
    print(f"❌ manifest.json不存在: {manifest_path}")
    exit(1)

print(f"✅ 扩展目录: {EXTENSION_PATH}")
print(f"✅ manifest.json: 存在")

# 读取manifest检查版本
import json
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest = json.load(f)
print(f"✅ 扩展名称: {manifest.get('name', '未知')}")
print(f"✅ 扩展版本: {manifest.get('version', '未知')}")
print(f"✅ Manifest版本: {manifest.get('manifest_version', '未知')}")

print("\n" + "="*60)
print("启动Chrome并加载扩展...")
print("="*60)

chrome_options = Options()
chrome_options.binary_location = CHROME_PATH
chrome_options.add_argument(f"--load-extension={EXTENSION_PATH}")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-gpu")

try:
    driver = webdriver.Chrome(options=chrome_options)
    print("✅ Chrome启动成功！")
    
    # 打开扩展管理页面
    driver.get("chrome://extensions/")
    time.sleep(3)
    
    print("\n📋 请手动检查：")
    print("1. 扩展是否显示在列表中")
    print("2. 扩展状态是否为'已启用'")
    print("3. 如果未加载，请尝试手动加载")
    input("\n按 Enter 键继续...")
    
    # 打开豆包页面
    driver.get("https://www.doubao.com/chat/")
    time.sleep(3)
    
    print("\n📋 请手动操作：")
    print("1. 登录豆包账号")
    print("2. 检查页面上是否有'DS随心转'按钮")
    print("3. 如果有，点击按钮导出Markdown")
    input("\n操作完成后按 Enter 键退出...")
    
    driver.quit()
    print("✅ 测试完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()