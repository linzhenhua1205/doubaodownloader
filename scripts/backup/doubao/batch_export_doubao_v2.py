import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------------------- 配置区 --------------------------
INDEX_HTML = r"H:\github\md\豆包链接索引.html"    # 链接索引文件
EXTENSION_PATH = r"H:\ext\dssxz"                  # 插件目录
DOWNLOAD_DIR = r"H:\dl\ai_md_exports"            # 下载目录
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
WAIT_SECONDS = 10                                 # 等待时间
MAX_RETRIES = 3                                   # 最大重试次数
# -----------------------------------------------------------

def extract_links(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'href="(https://www\.doubao\.com/chat/\d+)"'
    links = re.findall(pattern, content)
    links = sorted(list(set(links)))
    print(f"✅ 提取到 {len(links)} 个链接")
    return links

def export_chat(driver, url):
    try:
        driver.get(url)
        time.sleep(3)
        
        selectors = [
            "//div[contains(@class,'ds-sxz')]",
            "//div[contains(@class,'chat2file')]",
            "//button[contains(@class,'ds-sxz')]",
            "//span[contains(text(),'DS')]",
            "//span[contains(text(),'随心转')]"
        ]
        
        for selector in selectors:
            try:
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                btn.click()
                time.sleep(2)
                
                md_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//*[contains(text(),'Markdown')]")
                    )
                )
                md_btn.click()
                time.sleep(5)
                return True, "导出成功"
            except:
                continue
        
        return False, "未找到导出按钮"
            
    except Exception as e:
        return False, str(e)

def main():
    print("="*60)
    print("批量导出豆包对话 - DS随心转")
    print("="*60)
    
    links = extract_links(INDEX_HTML)
    if not links:
        print("❌ 未找到链接")
        return
    
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # 检查已存在的文件
    existing_files = set()
    if os.path.exists(DOWNLOAD_DIR):
        for f in os.listdir(DOWNLOAD_DIR):
            if f.lower().endswith('.md'):
                existing_files.add(f)
    print(f"✅ 已存在 {len(existing_files)} 个MD文件")
    
    # Chrome配置
    chrome_options = Options()
    chrome_options.binary_location = CHROME_PATH
    chrome_options.add_argument(f"--load-extension={EXTENSION_PATH}")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 打开豆包页面
        driver.get("https://www.doubao.com/chat/")
        time.sleep(5)
        
        print("\n⏳ 等待登录...")
        print("请在弹出的浏览器窗口中完成以下操作：")
        print("1. 登录豆包账号")
        print("2. 确保DS随心转插件已加载")
        print("3. 如果插件需要密码，请输入")
        
        # 自动检测登录状态（等待1分钟）
        logged_in = False
        for i in range(60):
            try:
                # 检查是否有聊天列表
                driver.find_element(By.CLASS_NAME, 'chat-list')
                logged_in = True
                print("\n✅ 检测到已登录！")
                break
            except:
                time.sleep(1)
                if i % 10 == 0:
                    print(f"   等待中 ({i}/60秒)...")
        
        if not logged_in:
            print("\n⚠️ 未检测到登录状态，继续尝试...")
        
        # 开始批量导出
        success_count = 0
        fail_count = 0
        
        for i, url in enumerate(links, 1):
            chat_id = url.split('/')[-1]
            
            # 检查是否已存在
            exists = any(chat_id in f for f in existing_files)
            if exists:
                print(f"🔄 {i}/{len(links)}: 已存在，跳过 - {url}")
                continue
            
            print(f"\n📥 {i}/{len(links)}: {url}")
            
            # 尝试导出
            success = False
            for retry in range(MAX_RETRIES):
                success, msg = export_chat(driver, url)
                if success:
                    break
                time.sleep(2)
            
            if success:
                print(f"✅ {msg}")
                success_count += 1
            else:
                print(f"❌ {msg}")
                fail_count += 1
            
            # 进度报告
            if i % 10 == 0:
                print(f"\n📊 进度: {i}/{len(links)}")
                print(f"   成功: {success_count} | 失败: {fail_count}")
        
        print(f"\n{'='*60}")
        print("📊 导出完成！")
        print(f"   总数: {len(links)}")
        print(f"   成功: {success_count}")
        print(f"   失败: {fail_count}")
        print(f"   跳过: {len(links) - success_count - fail_count}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()