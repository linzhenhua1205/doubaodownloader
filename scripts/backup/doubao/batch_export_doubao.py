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
WAIT_SECONDS = 12                                 # 等待时间
BATCH_SIZE = 10                                   # 每批处理数量
START_INDEX = 0                                   # 从第几个开始
# -----------------------------------------------------------

def extract_links(html_path):
    """从HTML文件中提取所有豆包对话链接"""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配豆包对话链接
    pattern = r'href="(https://www\.doubao\.com/chat/\d+)"'
    links = re.findall(pattern, content)
    
    # 去重并排序
    links = sorted(list(set(links)))
    print(f"✅ 从 {html_path} 提取到 {len(links)} 个链接")
    
    return links

def get_existing_files():
    """获取已下载的文件列表（用于跳过）"""
    existing = set()
    if os.path.exists(DOWNLOAD_DIR):
        for f in os.listdir(DOWNLOAD_DIR):
            if f.lower().endswith('.md'):
                existing.add(f)
    return existing

def export_chat(driver, url, download_dir):
    """导出单个对话为Markdown"""
    try:
        # 打开页面
        driver.get(url)
        time.sleep(3)
        
        # 等待页面加载完成（检查聊天内容区域）
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'chat-container'))
            )
        except:
            pass
        
        time.sleep(2)
        
        # 尝试点击DS随心转按钮
        selectors = [
            "//div[contains(@class,'ds-sxz')]",
            "//div[contains(@class,'chat2file')]",
            "//button[contains(@class,'ds-sxz')]",
            "//span[contains(text(),'DS')]",
            "//span[contains(text(),'随心转')]"
        ]
        
        button_found = False
        for selector in selectors:
            try:
                btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                btn.click()
                button_found = True
                time.sleep(2)
                break
            except:
                continue
        
        if not button_found:
            return False, "未找到导出按钮"
        
        # 点击Markdown导出
        try:
            md_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//*[contains(text(),'Markdown') or contains(text(),'markdown')]")
                )
            )
            md_btn.click()
            time.sleep(5)
            return True, "导出成功"
        except:
            return False, "未找到Markdown选项"
            
    except Exception as e:
        return False, str(e)

def main():
    print("="*60)
    print("批量导出豆包对话 - DS随心转")
    print("="*60)
    
    # 提取链接
    links = extract_links(INDEX_HTML)
    if not links:
        print("❌ 未找到任何链接")
        return
    
    # 创建下载目录
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # 获取已下载文件
    existing_files = get_existing_files()
    print(f"✅ 已存在 {len(existing_files)} 个MD文件")
    
    # 配置Chrome
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
        # 先打开扩展管理页面确认加载
        driver.get("chrome://extensions/")
        time.sleep(3)
        
        print("\n📋 请确认扩展已加载：")
        print("1. 扩展列表中是否显示 'DS随心转'")
        print("2. 如果未加载，请手动加载")
        input("\n确认后按 Enter 继续...")
        
        # 打开豆包页面登录
        driver.get("https://www.doubao.com/chat/")
        time.sleep(3)
        
        print("\n📋 请完成登录：")
        print("1. 登录豆包账号")
        print("2. 输入插件密码（如有）")
        input("\n登录完成后按 Enter 继续...")
        
        # 开始批量导出
        total_links = len(links[START_INDEX:])
        success_count = 0
        fail_count = 0
        
        for i, url in enumerate(links[START_INDEX:], start=START_INDEX+1):
            print(f"\n{'='*60}")
            print(f"正在处理 {i}/{len(links)}: {url}")
            
            # 检查是否已下载（通过URL判断）
            chat_id = url.split('/')[-1]
            exists = any(chat_id in f for f in existing_files)
            
            if exists:
                print("⚠️ 该对话已存在，跳过")
                continue
            
            # 导出
            success, msg = export_chat(driver, url, DOWNLOAD_DIR)
            
            if success:
                print(f"✅ {msg}")
                success_count += 1
            else:
                print(f"❌ {msg}")
                fail_count += 1
            
            # 每批完成后显示进度
            if i % BATCH_SIZE == 0:
                print(f"\n📊 进度: {i}/{len(links)}")
                print(f"   成功: {success_count} | 失败: {fail_count}")
        
        # 最终统计
        print(f"\n{'='*60}")
        print("📊 导出完成！")
        print(f"   总数: {total_links}")
        print(f"   成功: {success_count}")
        print(f"   失败: {fail_count}")
        print(f"   跳过: {total_links - success_count - fail_count}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n📝 操作完成")
        input("按 Enter 退出...")
        driver.quit()

if __name__ == "__main__":
    main()