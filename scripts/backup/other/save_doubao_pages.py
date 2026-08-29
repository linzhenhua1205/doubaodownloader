import os
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = "h:/github/md/chrome-win64/chrome-win64/chrome.exe"

def extract_unique_links(html_file):
    """从HTML文件中提取唯一的豆包聊天链接"""
    with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    links = re.findall(r'https://www\.doubao\.com/chat/(\d+)', content)
    unique_links = list(set(links))
    
    print(f"从 {html_file} 中找到 {len(links)} 个链接，去重后 {len(unique_links)} 个")
    
    return sorted(unique_links)

def save_page_content(driver, link_id, save_dir):
    """保存单个页面的HTML和Markdown内容"""
    url = f"https://www.doubao.com/chat/{link_id}"
    
    try:
        driver.get(url)
        time.sleep(10)
        
        html_content = driver.page_source
        
        html_filename = f"{link_id}.html"
        html_path = os.path.join(save_dir, "html", html_filename)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        title = driver.title.replace('| 豆包', '').replace('豆包 - ', '').strip()
        
        body_text = driver.find_element(By.TAG_NAME, 'body').text
        body_text = re.sub(r'\n{3,}', '\n\n', body_text)
        
        lines = body_text.split('\n')
        filtered_lines = []
        
        nav_keywords = ['新对话', 'Ctrl K', 'AI', '创作', '云盘', '更多', '历史对话', '搜索',
                       '消息', '通知', '设置', '帮助', '退出', '登录', '注册', '会员',
                       'Export', '导出', '下载', 'PDF', 'JSON', 'Word', '复制', '分享',
                       '由 AI 生成，请仔细甄别', '豆包', '输入消息']
        
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
        
        md_filename = f"{link_id}.md"
        md_path = os.path.join(save_dir, "markdown", md_filename)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return True, title
    
    except Exception as e:
        print(f"❌ 保存 {link_id} 失败: {e}")
        return False, None

def main():
    html_file = "h:/github/md/豆包链接索引.html"
    
    if not os.path.exists(html_file):
        print(f"错误: 文件不存在 {html_file}")
        return
    
    link_ids = extract_unique_links(html_file)
    
    if not link_ids:
        print("❌ 未找到任何链接")
        return
    
    save_dir = "./doubao_pages"
    os.makedirs(os.path.join(save_dir, "html"), exist_ok=True)
    os.makedirs(os.path.join(save_dir, "markdown"), exist_ok=True)
    
    user_data_dir = "h:/github/md/chrome_profile"
    os.makedirs(user_data_dir, exist_ok=True)
    
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--profile-directory=Default")
    options.binary_location = CHROME_PATH
    
    print("\n🔄 正在启动Chrome浏览器...")
    driver = webdriver.Chrome(options=options)
    
    print("\n" + "=" * 40)
    print("请执行以下操作：")
    print("1. 在弹出的浏览器窗口中登录你的豆包账号")
    print("2. 确保登录成功")
    print("3. 按 Enter 继续保存页面...")
    print("=" * 40)
    input()
    
    print(f"\n📥 开始保存 {len(link_ids)} 个页面...")
    success_count = 0
    failed_links = []
    
    for idx, link_id in enumerate(link_ids, 1):
        print(f"\n[{idx}/{len(link_ids)}] 正在处理: {link_id}")
        
        success, title = save_page_content(driver, link_id, save_dir)
        
        if success:
            print(f"✅ 已保存: {title if title else link_id}")
            success_count += 1
        else:
            print(f"❌ 保存失败")
            failed_links.append(link_id)
    
    summary = f"# 豆包页面保存汇总\n\n"
    summary += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary += f"链接总数: {len(link_ids)}\n"
    summary += f"成功保存: {success_count}\n"
    summary += f"失败数量: {len(failed_links)}\n\n"
    
    if failed_links:
        summary += "## 失败的链接\n\n"
        for link_id in failed_links:
            summary += f"- https://www.doubao.com/chat/{link_id}\n"
    
    with open(os.path.join(save_dir, "汇总.md"), "w", encoding="utf-8") as f:
        f.write(summary)
    
    driver.quit()
    
    print(f"\n🎉 完成！成功保存 {success_count}/{len(link_ids)} 个页面")
    print(f"📁 保存目录: {os.path.abspath(save_dir)}")

if __name__ == "__main__":
    from selenium.webdriver.common.by import By
    main()