import requests
import json
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = "h:/github/md/chrome-win64/chrome-win64/chrome.exe"

def get_chats_with_selenium():
    """使用Selenium自动登录并获取聊天记录"""
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
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-infobars")
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
    time.sleep(3)
    
    print("\n📡 正在获取会话列表...")
    
    save_dir = "./doubao_auto_export"
    os.makedirs(save_dir, exist_ok=True)
    
    all_threads = []
    
    try:
        js_code = """
            const callback = arguments[arguments.length - 1];
            fetch('https://www.doubao.com/api/thread/list?cursor=&limit=100', {
                credentials: 'include',
                headers: {
                    'Accept': 'application/json, text/plain, */*',
                    'Referer': 'https://www.doubao.com/chat'
                }
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.text();
            })
            .then(text => {
                console.log('Response text:', text.substring(0, 500));
                try {
                    const data = JSON.parse(text);
                    callback({success: true, data: data});
                } catch(e) {
                    callback({success: false, error: 'JSON parse error: ' + e.message, raw: text});
                }
            })
            .catch(error => callback({success: false, error: error.message}));
        """
        
        result = driver.execute_async_script(js_code, 30)
        
        print(f"📝 API响应: {result}")
        
        if result and result.get('success'):
            data = result.get('data', {})
            threads = data.get('threads', [])
            print(f"✅ 获取到 {len(threads)} 个会话")
            
            for idx, thread in enumerate(threads, 1):
                thread_id = thread.get("id")
                title = thread.get("title", "无标题")
                title = title.replace("/", "-").replace("\\", "-")
                
                print(f"\n📥 [{idx}/{len(threads)}] 正在获取: {title}")
                
                js_get_messages = f"""
                    const callback = arguments[arguments.length - 1];
                    fetch('https://www.doubao.com/api/chat/history?thread_id={thread_id}&cursor=&limit=100', {{
                        credentials: 'include',
                        headers: {{
                            'Accept': 'application/json, text/plain, */*',
                            'Referer': 'https://www.doubao.com/chat'
                        }}
                    }})
                    .then(response => response.json())
                    .then(data => callback({{success: true, data: data}}))
                    .catch(error => callback({{success: false, error: error.message}}));
                """
                
                try:
                    msg_result = driver.execute_async_script(js_get_messages, 30)
                    
                    if msg_result and msg_result.get('success'):
                        messages_data = msg_result.get('data', {})
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
                            print(f"✅ 已保存")
                        else:
                            print(f"ℹ️ 无消息")
                    else:
                        print(f"❌ 获取消息失败")
                        
                except Exception as e:
                    print(f"❌ 处理会话失败: {e}")
            
            summary = f"# 豆包聊天记录汇总\n\n"
            summary += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            summary += f"会话数量: {len(all_threads)}\n\n"
            
            for thread in all_threads:
                summary += f"- [{thread['title']}]({thread['id']}_{thread['title'][:20]}.md) - {thread['messages']} 条消息\n"
            
            with open(os.path.join(save_dir, "汇总.md"), "w", encoding="utf-8") as f:
                f.write(summary)
            
            print(f"\n🎉 导出完成！共保存 {len(all_threads)} 个会话")
            print(f"📁 保存目录: {os.path.abspath(save_dir)}")
            
        else:
            print(f"❌ 获取会话列表失败: {result.get('error') if result else '未知错误'}")
        
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
    
    driver.quit()

if __name__ == "__main__":
    get_chats_with_selenium()