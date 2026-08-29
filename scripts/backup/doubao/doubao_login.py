import requests
import json
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = "h:/github/md/chrome-win64/chrome-win64/chrome.exe"

def get_cookie_and_fetch_history():
    """获取Cookie并导出聊天记录"""
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
    print(f"📁 用户数据目录: {user_data_dir}")
    driver = webdriver.Chrome(options=options)
    
    print("🌐 正在访问豆包官网...")
    driver.get("https://www.doubao.com/chat")
    
    print("\n" + "=" * 40)
    print("请执行以下操作：")
    print("1. 在弹出的浏览器窗口中登录你的豆包账号")
    print("2. 确保登录成功后能看到聊天界面")
    print("3. 可以尝试发送一条消息确认登录有效")
    print("4. 然后回到终端按 Enter 继续...")
    print("=" * 40)
    input()
    
    print("\n⏳ 刷新页面确保Cookie更新...")
    driver.refresh()
    time.sleep(3)
    
    print("📋 正在获取Cookie...")
    cookies = driver.get_cookies()
    cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    
    print(f"✅ 获取到 {len(cookies)} 个Cookie")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.7778.168 Safari/537.36",
        "Cookie": cookie_str,
        "Referer": "https://www.doubao.com/chat",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Origin": "https://www.doubao.com",
        "Sec-Ch-Ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"148\", \"Google Chrome\";v=\"148\"",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    
    print("\n🔍 正在测试Cookie有效性...")
    url = "https://www.doubao.com/api/thread/list?cursor=&limit=10"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        
        print(f"\n📝 响应状态码: {r.status_code}")
        print(f"📝 响应头: {dict(r.headers) if len(r.headers) < 20 else {k: v for k, v in list(r.headers.items())[:20]}}")
        
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"📝 响应数据结构: {list(data.keys())}")
                if "threads" in data:
                    print("✅ Cookie有效！")
                    print(f"📊 找到 {len(data['threads'])} 个对话")
                    
                    save_history(data, headers, cookie_str)
                else:
                    print(f"❌ 响应异常: {json.dumps(data, ensure_ascii=False)[:500]}")
            except json.JSONDecodeError:
                print(f"❌ 响应不是JSON: {r.text[:500]}")
        else:
            print(f"❌ 请求失败，状态码: {r.status_code}")
            try:
                error_data = r.json()
                print(f"❌ 错误信息: {json.dumps(error_data, ensure_ascii=False)}")
            except:
                print(f"❌ 响应内容: {r.text[:500]}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    driver.quit()

def save_history(initial_data, headers, cookie_str):
    """保存聊天历史"""
    save_dir = "./doubao_history"
    os.makedirs(save_dir, exist_ok=True)
    
    all_threads = []
    threads = initial_data.get("threads", [])
    
    for thread in threads:
        thread_id = thread.get("id")
        title = thread.get("title", "无标题")
        title = title.replace("/", "-").replace("\\", "-")
        
        chat_url = f"https://www.doubao.com/api/chat/history?thread_id={thread_id}&cursor=&limit=100"
        
        try:
            r = requests.get(chat_url, headers=headers, timeout=10)
            if r.status_code == 200:
                chat_data = r.json()
                messages = chat_data.get("messages", [])
                
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
        except Exception as e:
            print(f"❌ 获取会话 {title} 失败: {e}")
    
    summary = f"# 豆包聊天记录汇总\n\n"
    summary += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary += f"会话数量: {len(all_threads)}\n\n"
    
    for thread in all_threads:
        summary += f"- [{thread['title']}]({thread['id']}_{thread['title'][:20]}.md) - {thread['messages']} 条消息\n"
    
    with open(os.path.join(save_dir, "汇总.md"), "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"\n🎉 导出完成！共保存 {len(all_threads)} 个会话")
    print(f"📁 保存目录: {os.path.abspath(save_dir)}")

if __name__ == "__main__":
    get_cookie_and_fetch_history()