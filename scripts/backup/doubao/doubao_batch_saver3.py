import os
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# -------------------------- 配置区 --------------------------
CHROME_PATH = "h:/github/md/chrome-win64/chrome-win64/chrome.exe"  # 本地Chrome路径
EXTENSION_PATH = r"H:\ext\dssxz"                                    # 插件目录
DOWNLOAD_DIR = r"H:\dl\ai_md_exports"                              # 插件下载目录
INDEX_HTML = "h:/github/md/豆包链接索引.html"                       # 链接索引文件
WAIT_SECONDS = 10                                                  # 页面加载等待时间
# -----------------------------------------------------------

def sanitize_filename(title):
    illegal_chars = r'[\\/:*?"<>|]'
    sanitized = re.sub(illegal_chars, '_', title)
    sanitized = sanitized.strip()
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    return sanitized

def extract_unique_links(html_file):
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    links = re.findall(r'https://www\.doubao\.com/chat/(\d+)', content)
    unique_links = list(set(links))
    
    print(f"从 {html_file} 中找到 {len(links)} 个链接，去重后 {len(unique_links)} 个")
    
    return sorted(unique_links)

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

def export_with_extension(driver, link_id, download_dir):
    """使用DS随心转插件导出Markdown"""
    url = f"https://www.doubao.com/chat/{link_id}"
    
    try:
        driver.get(url)
        time.sleep(5)
        
        try:
            driver.find_element(By.XPATH, "//button[contains(text(),'登录')]")
            return False, "需要登录"
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
                    return True, f"插件导出成功: {filename}"
                else:
                    return False, "下载超时"
                    
            except Exception as e:
                continue
        
        return False, "未找到导出按钮"
            
    except Exception as e:
        return False, str(e)

def save_page_content(driver, link_id, save_dir, used_titles):
    """保存单个页面的HTML和Markdown内容"""
    url = f"https://www.doubao.com/chat/{link_id}"
    
    try:
        driver.get(url)
        time.sleep(WAIT_SECONDS)
        
        html_content = driver.page_source
        
        title = driver.title.replace('| 豆包', '').replace('豆包 - ', '').strip()
        if not title or title.isspace():
            title = link_id
        
        safe_title = sanitize_filename(title)
        if not safe_title:
            safe_title = link_id
        
        counter = 1
        final_title = safe_title
        while final_title in used_titles:
            final_title = f"{safe_title}_{counter}"
            counter += 1
        used_titles.add(final_title)
        
        html_filename = f"{final_title}.html"
        html_path = os.path.join(save_dir, "html", html_filename)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        body_text = re.sub(r'\n{3,}', '\n\n', body_text)
        
        lines = body_text.split('\n')
        filtered_lines = []
        
        nav_keywords = ['新对话', 'Ctrl K', 'AI', '创作', '云盘', '更多', '历史对话', '搜索',
                       '消息', '通知', '设置', '帮助', '退出', '登录', '注册', '会员',
                       'Export', '导出', '下载', 'PDF', 'JSON', 'Word', '复制', '分享',
                       '由 AI 生成，请仔细甄别', '豆包', '输入消息', '输入框']
        
        for line in lines:
            line = line.strip()
            
            if len(line) < 8:
                continue
            
            is_noise = False
            for keyword in nav_keywords:
                if keyword in line:
                    is_noise = True
                    break
            
            if is_noise:
                continue
            
            filtered_lines.append(line)
        
        markdown_content = f"# {title}\n\n"
        markdown_content += f"来源链接: {url}\n\n"
        markdown_content += "\n\n".join(filtered_lines)
        
        md_filename = f"{final_title}.md"
        md_path = os.path.join(save_dir, "markdown", md_filename)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return True, title, final_title
    
    except Exception as e:
        print(f"❌ 保存 {link_id} 失败: {e}")
        return False, None, None

def main():
    if not os.path.exists(INDEX_HTML):
        print(f"错误: 文件不存在 {INDEX_HTML}")
        return
    
    if not os.path.exists(CHROME_PATH):
        print(f"错误: Chrome不存在 {CHROME_PATH}")
        return
    
    if not os.path.exists(EXTENSION_PATH):
        print(f"错误: 插件目录不存在 {EXTENSION_PATH}")
        return
    
    link_ids = extract_unique_links(INDEX_HTML)
    
    if not link_ids:
        print("❌ 未找到任何链接")
        return
    
    save_dir = "./doubao_batch_export"
    os.makedirs(os.path.join(save_dir, "html"), exist_ok=True)
    os.makedirs(os.path.join(save_dir, "markdown"), exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    user_data_dir = "h:/github/md/chrome_profile"
    os.makedirs(user_data_dir, exist_ok=True)
    
    print("="*60)
    print("豆包批量导出工具")
    print("="*60)
    print(f"Chrome路径: {CHROME_PATH}")
    print(f"插件路径: {EXTENSION_PATH}")
    print(f"下载目录: {DOWNLOAD_DIR}")
    print(f"用户数据目录: {user_data_dir}")
    print("="*60)
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-popup-blocking")
    options.binary_location = CHROME_PATH
    
    # 加载插件
    options.add_argument(f"--load-extension={EXTENSION_PATH}")
    
    # 配置下载设置
    options.add_experimental_option("prefs", {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1
    })
    
    print("\n🔄 正在启动Chrome浏览器...")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.doubao.com/chat/")
        time.sleep(5)
        
        print("\n" + "=" * 40)
        print("请执行以下操作：")
        print("1. 在弹出的浏览器窗口中登录你的豆包账号")
        print("2. 确保DS随心转插件已加载（检查右上角扩展图标）")
        print("3. 输入插件密码（如有）")
        print("4. 按 Enter 继续...")
        print("=" * 40)
        input()
        
        print(f"\n📥 开始处理 {len(link_ids)} 个页面...")
        
        success_count = 0
        plugin_success_count = 0
        failed_links = []
        used_titles = set()
        saved_files = []
        
        for idx, link_id in enumerate(link_ids, 1):
            print(f"\n[{idx}/{len(link_ids)}] 正在处理: {link_id}")
            
            # 先尝试使用插件导出
            plugin_success, plugin_msg = export_with_extension(driver, link_id, DOWNLOAD_DIR)
            
            if plugin_success:
                print(f"✅ {plugin_msg}")
                plugin_success_count += 1
                success_count += 1
                continue
            
            # 如果插件导出失败，回退到页面内容提取
            print(f"⚠️ 插件导出失败 ({plugin_msg})，回退到页面提取")
            success, title, final_title = save_page_content(driver, link_id, save_dir, used_titles)
            
            if success:
                print(f"✅ 已保存: {title}")
                saved_files.append({"link_id": link_id, "title": title, "filename": final_title})
                success_count += 1
            else:
                print(f"❌ 保存失败")
                failed_links.append(link_id)
        
        summary = f"# 豆包页面保存汇总\n\n"
        summary += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"链接总数: {len(link_ids)}\n"
        summary += f"插件导出成功: {plugin_success_count}\n"
        summary += f"页面提取成功: {success_count - plugin_success_count}\n"
        summary += f"失败数量: {len(failed_links)}\n\n"
        
        summary += "## 会话列表\n\n"
        for item in saved_files:
            summary += f"- [{item['title']}](markdown/{item['filename']}.md)\n"
        
        if failed_links:
            summary += "\n## 失败的链接\n\n"
            for link_id in failed_links:
                summary += f"- https://www.doubao.com/chat/{link_id}\n"
        
        with open(os.path.join(save_dir, "汇总.md"), "w", encoding="utf-8") as f:
            f.write(summary)
        
        print(f"\n🎉 完成！")
        print(f"📊 插件导出: {plugin_success_count} | 页面提取: {success_count - plugin_success_count}")
        print(f"📁 页面保存目录: {os.path.abspath(save_dir)}")
        print(f"📁 插件下载目录: {os.path.abspath(DOWNLOAD_DIR)}")
        
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()