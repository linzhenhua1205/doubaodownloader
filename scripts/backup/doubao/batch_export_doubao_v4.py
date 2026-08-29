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
USER_DATA_DIR = r"H:\chrome_doubao_profile"       # 持久化用户数据目录
WAIT_SECONDS = 8                                 # 等待时间
MAX_RETRIES = 2                                  # 最大重试次数
BATCH_SIZE = 5                                   # 每批处理数量
# -----------------------------------------------------------

def extract_links(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    pattern = r'href="(https://www\.doubao\.com/chat/\d+)"'
    links = re.findall(pattern, content)
    links = sorted(list(set(links)))
    print(f"✅ 提取到 {len(links)} 个链接")
    return links

def wait_for_download(download_dir, timeout=30):
    start_files = set(os.listdir(download_dir))
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - start_files
        md_files = [f for f in new_files if f.lower().endswith('.md')]
        if md_files:
            return True, md_files[0]
        time.sleep(1)
    
    return False, None

def export_chat(driver, url, download_dir):
    try:
        driver.get(url)
        time.sleep(3)
        
        try:
            login_btn = driver.find_element(By.XPATH, "//button[contains(text(),'登录')]")
            return False, "需要登录"
        except:
            pass
        
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'message-item'))
            )
        except:
            pass
        
        selectors = [
            "//div[contains(@class,'ds-sxz')]",
            "//div[contains(@class,'chat2file')]",
            "//button[contains(@class,'ds-sxz')]",
            "//div[@class='ds-sxz-btn']"
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
                        (By.XPATH, "//*[contains(text(),'Markdown') or contains(text(),'markdown')]")
                    )
                )
                md_btn.click()
                
                success, filename = wait_for_download(download_dir, 20)
                if success:
                    return True, f"导出成功: {filename}"
                else:
                    return False, "下载超时"
                    
            except Exception as e:
                continue
        
        return False, "未找到导出按钮"
            
    except Exception as e:
        return False, str(e)

def main():
    print("="*60)
    print("批量导出豆包对话 - DS随心转 v4")
    print("="*60)
    
    # 创建必要目录
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    
    links = extract_links(INDEX_HTML)
    if not links:
        print("❌ 未找到链接")
        return
    
    existing_files = set()
    if os.path.exists(DOWNLOAD_DIR):
        for f in os.listdir(DOWNLOAD_DIR):
            if f.lower().endswith('.md'):
                existing_files.add(f)
    print(f"✅ 已存在 {len(existing_files)} 个MD文件")
    print(f"✅ 用户数据目录: {USER_DATA_DIR}")
    print(f"✅ 插件目录: {EXTENSION_PATH}")
    
    # Chrome配置 - 使用持久化用户数据目录
    chrome_options = Options()
    chrome_options.binary_location = CHROME_PATH
    
    # 关键：使用持久化用户数据目录保存登录状态
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    chrome_options.add_argument("--profile-directory=Default")
    
    # 加载扩展
    chrome_options.add_argument(f"--load-extension={EXTENSION_PATH}")
    
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-gpu")
    
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://www.doubao.com/chat/")
        time.sleep(5)
        
        # 检查是否已登录
        is_logged_in = False
        try:
            driver.find_element(By.CLASS_NAME, 'chat-list')
            is_logged_in = True
            print("\n✅ 检测到已登录状态！")
        except:
            pass
        
        if not is_logged_in:
            print("\n📋 需要登录豆包账号")
            print("请在浏览器中完成：")
            print("1. 登录豆包账号")
            print("2. 确保DS随心转插件已加载")
            print("3. 输入插件密码（如有）")
            print("\n登录信息将保存在用户数据目录中")
            
            print("\n按 Enter 键继续...")
            import sys
            if sys.platform.startswith('win'):
                os.system('pause')
            else:
                input()
        else:
            print("\n📋 检测到已有登录状态，直接开始导出")
        
        # 开始批量导出
        success_count = 0
        fail_count = 0
        skipped_count = 0
        
        for i, url in enumerate(links, 1):
            chat_id = url.split('/')[-1]
            
            exists = any(chat_id in f for f in existing_files)
            if exists:
                print(f"🔄 {i}/{len(links)}: 已存在，跳过")
                skipped_count += 1
                continue
            
            print(f"\n📥 {i}/{len(links)}: {url}")
            
            success = False
            msg = ""
            for retry in range(MAX_RETRIES):
                success, msg = export_chat(driver, url, DOWNLOAD_DIR)
                if success:
                    break
                print(f"   重试 {retry+1}/{MAX_RETRIES}...")
                time.sleep(2)
            
            if success:
                print(f"✅ {msg}")
                success_count += 1
            else:
                print(f"❌ {msg}")
                fail_count += 1
            
            if i % BATCH_SIZE == 0:
                print(f"\n📊 进度: {i}/{len(links)}")
                print(f"   成功: {success_count} | 失败: {fail_count} | 跳过: {skipped_count}")
        
        print(f"\n{'='*60}")
        print("📊 导出完成！")
        print(f"   总数: {len(links)}")
        print(f"   成功: {success_count}")
        print(f"   失败: {fail_count}")
        print(f"   跳过: {skipped_count}")
        print(f"\n💡 登录信息已保存到: {USER_DATA_DIR}")
        print("下次运行时将自动使用已保存的登录状态")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n按 Enter 退出...")
        import sys
        if sys.platform.startswith('win'):
            os.system('pause')
        else:
            input()
        driver.quit()

if __name__ == "__main__":
    main()