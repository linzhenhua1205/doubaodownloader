import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = "h:/github/md/chrome-win64/chrome-win64/chrome.exe"

def extract_from_page():
    """从页面中提取聊天数据"""
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
    time.sleep(3)
    
    print("\n🔍 正在搜索页面中的数据...")
    
    save_dir = "./doubao_page_extract"
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        js_get_data = """
            if (window.__INITIAL_STATE__) {
                return JSON.stringify(window.__INITIAL_STATE__);
            } else if (window.initialState) {
                return JSON.stringify(window.initialState);
            } else if (window.store) {
                try {
                    return JSON.stringify(window.store.getState ? window.store.getState() : window.store);
                } catch(e) {
                    return null;
                }
            } else {
                return null;
            }
        """
        
        result = driver.execute_script(js_get_data)
        
        if result:
            try:
                data = json.loads(result)
                print(f"✅ 找到页面数据，包含键: {list(data.keys())}")
                
                if 'chat' in data:
                    chat_data = data['chat']
                    print(f"chat数据包含键: {list(chat_data.keys())}")
                    
                    if 'threads' in chat_data:
                        threads = chat_data['threads']
                        print(f"找到 {len(threads)} 个会话")
                        
                        all_threads = []
                        
                        for thread in threads:
                            thread_id = thread.get("id")
                            title = thread.get("title", "无标题")
                            title = title.replace("/", "-").replace("\\", "-")
                            
                            print(f"\n📥 正在获取: {title}")
                            
                            driver.get(f"https://www.doubao.com/chat/{thread_id}")
                            time.sleep(2)
                            
                            js_get_messages = """
                                if (window.__INITIAL_STATE__) {
                                    return JSON.stringify(window.__INITIAL_STATE__);
                                } else if (window.initialState) {
                                    return JSON.stringify(window.initialState);
                                }
                                return null;
                            """
                            
                            msg_result = driver.execute_script(js_get_messages)
                            
                            if msg_result:
                                try:
                                    msg_data = json.loads(msg_result)
                                    if 'chat' in msg_data and 'messages' in msg_data['chat']:
                                        messages = msg_data['chat']['messages']
                                        
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
                                except json.JSONDecodeError:
                                    print(f"❌ 解析消息失败")
                            else:
                                print(f"❌ 未找到消息数据")
                        
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
                        print("❌ 未找到threads数据")
                else:
                    print("❌ 未找到chat数据")
                    
            except json.JSONDecodeError:
                print("❌ 解析JSON失败")
        else:
            print("❌ 未找到页面数据")
            
    except Exception as e:
        print(f"❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
    
    driver.quit()

if __name__ == "__main__":
    extract_from_page()