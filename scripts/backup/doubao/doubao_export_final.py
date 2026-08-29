import os
import sys
import time

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
except ImportError as e:
    print(f"错误: 无法导入selenium模块 - {e}")
    print("请运行: pip install selenium")
    sys.exit(1)

CHROME_PATH = r"h:\github\md\chrome-win64\chrome-win64\chrome.exe"
EXTENSION_PATH = r"h:\github\md\dssxz"
DOWNLOAD_DIR = r"H:\dl\ai_md_exports"
INDEX_HTML = r"h:\github\md\豆包链接索引.html"

def extract_unique_links(html_file):
    import re
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    links = re.findall(r'https://www\.doubao\.com/chat/(\d+)', content)
    return list(set(links))

def main():
    print("="*60)
    print("豆包对话批量导出工具")
    print("="*60)
    
    if not os.path.exists(INDEX_HTML):
        print(f"错误: 索引文件不存在: {INDEX_HTML}")
        input("按 Enter 退出...")
        return
    
    link_ids = extract_unique_links(INDEX_HTML)
    if not link_ids:
        print("错误: 未找到任何链接")
        input("按 Enter 退出...")
        return
    print(f"找到 {len(link_ids)} 个对话链接")
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-data-dir={r'h:\github\md\chrome_profile'}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-popup-blocking")
    options.binary_location = CHROME_PATH
    options.add_argument(f"--load-extension={EXTENSION_PATH}")
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    
    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(f"Chrome启动失败: {str(e)[:100]}")
        input("按 Enter 退出...")
        return
    
    try:
        driver.get("https://www.doubao.com/chat/")
        time.sleep(8)
        
        print("\n请完成以下操作后按 Enter 继续:")
        print("1. 登录你的豆包账号")
        print("2. 确保DS随心转插件已加载（右上角扩展图标）")
        print("3. 输入插件密码（如有）")
        input()
        
        for idx, link_id in enumerate(link_ids, 1):
            print(f"\n{'='*60}")
            print(f"[{idx}/{len(link_ids)}] 处理对话")
            print(f"链接: https://www.doubao.com/chat/{link_id}")
            print("="*60)
            
            driver.get(f"https://www.doubao.com/chat/{link_id}")
            time.sleep(8)
            
            print("\n请手动完成以下操作:")
            print("1. 点击页面上的 DS随心转 悬浮按钮")
            print("2. 在弹出的底部操作栏中勾选 '全选' 复选框")
            print("3. 点击 'Markdown' 导出按钮")
            print("4. 等待文件下载完成")
            input("\n完成后按 Enter 继续下一个...")
        
        print(f"\n{'='*60}")
        print("所有对话处理完成！")
        print(f"下载目录: {DOWNLOAD_DIR}")
        print("="*60)
        
    except Exception as e:
        print(f"\n错误: {str(e)}")
    
    finally:
        input("\n按 Enter 关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    main()