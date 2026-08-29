import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = "h:/github/md/chrome-win64/chrome-win64/chrome.exe"

def export_chat_history():
    """直接从豆包网站抓取聊天记录"""
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
    print("3. 点击任意一个会话查看消息")
    print("4. 然后回到终端按 Enter 继续导出...")
    print("=" * 40)
    input()
    
    print("\n⏳ 等待页面加载...")
    time.sleep(3)
    
    print("\n📡 正在获取会话列表...")
    save_dir = "./doubao_live_history"
    os.makedirs(save_dir, exist_ok=True)
    
    all_threads = []
    
    try:
        js_code = """
            const callback = arguments[arguments.length - 1];
            fetch('https://www.doubao.com/api/thread/list?cursor=&limit=50', {
                credentials: 'include',
                headers: {
                    'Accept': 'application/json, text/plain, */*',
                    'Referer': 'https://www.doubao.com/chat',
                    'User-Agent': navigator.userAgent
                }
            }).then(response => {
                console.log('Response status:', response.status);
                return response.text();
            }).then(data => {
                console.log('Response data:', data);
                callback(data);
            }).catch(err => {
                console.log('Error:', err);
                callback(null);
            });
        """
        
        result = driver.execute_async_script(js_code)
        
        print(f"📝 API返回长度: {len(result) if result else 0}")
        print(f"📝 API返回前200字符: {result[:200] if result else 'None'}")
        
        if result is None or result.strip() == '':
            print("❌ 获取会话列表失败 - 响应为空")
            driver.quit()
            return
        
        try:
            threads_data = json.loads(result)
            print(f"📝 解析后的数据结构: {list(threads_data.keys()) if isinstance(threads_data, dict) else '不是字典'}")
            threads = threads_data.get("threads", [])
            print(f"✅ 获取到 {len(threads)} 个会话")
            
            for thread in threads:
                thread_id = thread.get("id")
                title = thread.get("title", "无标题")
                title = title.replace("/", "-").replace("\\", "-")
                
                print(f"\n📥 正在获取: {title}")
                
                js_get_messages = f"""
                    const callback = arguments[arguments.length - 1];
                    fetch('https://www.doubao.com/api/chat/history?thread_id={thread_id}&cursor=&limit=100', {{
                        credentials: 'include'
                    }}).then(response => response.text()).then(data => callback(data)).catch(err => callback(null));
                """
                
                messages_result = driver.execute_async_script(js_get_messages)
                
                if messages_result is None:
                    print(f"❌ 获取消息失败")
                    continue
                
                try:
                    messages_data = json.loads(messages_result)
                    messages = messages_data.get("messages", [])
                    
                    if messages:
                        md_content = f"# {title}\n\n"
                        md_content += f"会话ID: {thread_id}\n\n"
                        
                        for msg in messages:
                            role = msg.get("role", "")
                            content = msg.get("content", "")
                            
                            if role == "user":
                                md_content += f"**👤 我:**\n{content}\n\n"
                            elif role == "assistant":
                                md_content += f"**🤖 豆包:**\n{content}\n\n"
                        
                        filename = f"{thread_id}_{title[:20]}.md"
                        filepath = os.path.join(save_dir, filename)
                        
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(md_content)
                        
                        all_threads.append({"id": thread_id, "title": title, "messages": len(messages)})
                        print(f"✅ 已保存: {title}")
                    else:
                        print(f"ℹ️ 会话 {title} 没有消息")
                        
                except json.JSONDecodeError:
                    print(f"❌ 解析消息失败: {messages_result[:100]}")
                    
        except json.JSONDecodeError:
            print(f"❌ 解析会话列表失败: {result[:100]}")
        
        summary = f"# 豆包聊天记录汇总\n\n"
        summary += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"会话数量: {len(all_threads)}\n\n"
        
        for thread in all_threads:
            summary += f"- [{thread['title']}]({thread['id']}_{thread['title'][:20]}.md) - {thread['messages']} 条消息\n"
        
        with open(os.path.join(save_dir, "汇总.md"), "w", encoding="utf-8") as f:
            f.write(summary)
        
        print(f"\n🎉 导出完成！共保存 {len(all_threads)} 个会话")
        print(f"📁 保存目录: {os.path.abspath(save_dir)}")
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
    
    driver.quit()

if __name__ == "__main__":
    export_chat_history()