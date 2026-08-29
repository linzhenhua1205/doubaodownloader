import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHROME_PATH = "h:/github/md/chrome-win64/chrome-win64/chrome.exe"

def scrape_chat_history():
    """直接从页面提取聊天记录"""
    print("\n📦 豆包对话历史导出工具")
    print("=" * 40)
    
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
    
    print("🌐 正在访问豆包官网...")
    driver.get("https://www.doubao.com/chat")
    
    print("\n" + "=" * 40)
    print("请执行以下操作：")
    print("1. 在弹出的浏览器窗口中登录你的豆包账号")
    print("2. 确保登录成功后能看到聊天列表")
    print("3. 按 Enter 继续导出...")
    print("=" * 40)
    input()
    
    print("\n⏳ 等待页面加载...")
    time.sleep(5)
    
    print("\n🔍 正在查找会话列表...")
    save_dir = "./doubao_scraped"
    os.makedirs(save_dir, exist_ok=True)
    
    all_chats = []
    
    try:
        conversation_items = driver.find_elements(By.CSS_SELECTOR, '[data-testid^="conversation-item"]')
        print(f"✅ 找到 {len(conversation_items)} 个会话")
        
        for idx, item in enumerate(conversation_items):
            try:
                title_element = item.find_element(By.CSS_SELECTOR, '.title')
                title = title_element.text.strip()
                title = title.replace("/", "-").replace("\\", "-").replace(":", "-")
                
                print(f"\n📥 [{idx+1}/{len(conversation_items)}] 正在获取: {title}")
                
                item.click()
                time.sleep(2)
                
                messages = driver.find_elements(By.CSS_SELECTOR, '[data-testid^="message-"]')
                
                if messages:
                    md_content = f"# {title}\n\n"
                    
                    for msg in messages:
                        try:
                            role_element = msg.find_element(By.CSS_SELECTOR, '.role')
                            content_element = msg.find_element(By.CSS_SELECTOR, '.content')
                            
                            role = role_element.text.strip()
                            content = content_element.text.strip()
                            
                            if role == '我':
                                md_content += f"**👤 我:**\n{content}\n\n"
                            else:
                                md_content += f"**🤖 豆包:**\n{content}\n\n"
                        except:
                            continue
                    
                    filename = f"{idx+1:03d}_{title[:20]}.md"
                    filepath = os.path.join(save_dir, filename)
                    
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(md_content)
                    
                    all_chats.append({"title": title, "file": filename})
                    print(f"✅ 已保存: {title}")
                else:
                    print(f"ℹ️ 会话 {title} 没有消息")
                    
            except Exception as e:
                print(f"❌ 处理会话失败: {e}")
        
        summary = f"# 豆包聊天记录汇总\n\n"
        summary += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"会话数量: {len(all_chats)}\n\n"
        
        for chat in all_chats:
            summary += f"- [{chat['title']}]({chat['file']})\n"
        
        with open(os.path.join(save_dir, "汇总.md"), "w", encoding="utf-8") as f:
            f.write(summary)
        
        print(f"\n🎉 导出完成！共保存 {len(all_chats)} 个会话")
        print(f"📁 保存目录: {os.path.abspath(save_dir)}")
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
    
    driver.quit()

if __name__ == "__main__":
    scrape_chat_history()