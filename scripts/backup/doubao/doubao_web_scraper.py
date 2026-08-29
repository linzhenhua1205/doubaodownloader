import os
import json
import time
import base64
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CHROME_PATH = "h:/github/md/chrome-win64/chrome-win64/chrome.exe"

def scrape_doubao_chats():
    """从豆包网站直接抓取聊天记录"""
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
    options.add_argument("--auto-open-devtools-for-tabs")
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
    
    save_dir = "./doubao_web_export"
    os.makedirs(save_dir, exist_ok=True)
    
    all_threads = []
    
    try:
        print("\n📡 方法1: 尝试从页面获取数据...")
        
        js_extract_data = """
            let result = {};
            
            if (window.__INITIAL_STATE__) {
                result.initialState = JSON.stringify(window.__INITIAL_STATE__);
            }
            
            if (window.initialState) {
                result.initialState = JSON.stringify(window.initialState);
            }
            
            if (window.store && window.store.getState) {
                try {
                    result.store = JSON.stringify(window.store.getState());
                } catch(e) {}
            }
            
            const scripts = document.querySelectorAll('script');
            for (let script of scripts) {
                if (script.textContent.includes('threads') || script.textContent.includes('messages')) {
                    const match = script.textContent.match(/"threads":\\s*(\\[.*?\\])/);
                    if (match) result.threads = match[1];
                    
                    const msgMatch = script.textContent.match(/"messages":\\s*(\\[.*?\\])/);
                    if (msgMatch) result.messages = msgMatch[1];
                }
            }
            
            return result;
        """
        
        data = driver.execute_script(js_extract_data)
        
        if data.get('threads'):
            try:
                threads = json.loads(data['threads'])
                print(f"✅ 找到 {len(threads)} 个会话")
                
                for thread in threads[:10]:
                    thread_id = thread.get("id")
                    title = thread.get("title", "无标题")
                    print(f"  - {title}")
                
                all_threads.extend([{"id": t.get("id"), "title": t.get("title", "无标题")} for t in threads])
            except:
                pass
        
        print("\n📡 方法2: 尝试获取localStorage数据...")
        
        local_storage_data = driver.execute_script("return JSON.stringify(window.localStorage);")
        if local_storage_data:
            try:
                ls = json.loads(local_storage_data)
                print(f"✅ localStorage包含 {len(ls)} 个键")
                for key in list(ls.keys())[:5]:
                    print(f"  - {key}")
            except:
                pass
        
        print("\n📡 方法3: 尝试获取sessionStorage数据...")
        
        session_storage_data = driver.execute_script("return JSON.stringify(window.sessionStorage);")
        if session_storage_data:
            try:
                ss = json.loads(session_storage_data)
                print(f"✅ sessionStorage包含 {len(ss)} 个键")
            except:
                pass
        
        print("\n📡 方法4: 尝试通过fetch API获取数据...")
        
        js_fetch = """
            const callback = arguments[arguments.length - 1];
            fetch('https://www.doubao.com/api/thread/list?cursor=&limit=50', {
                credentials: 'include',
                headers: {
                    'Accept': 'application/json, text/plain, */*',
                    'Referer': 'https://www.doubao.com/chat',
                    'User-Agent': navigator.userAgent
                }
            })
            .then(response => {
                return response.text().then(text => ({
                    status: response.status,
                    text: text
                }));
            })
            .then(data => callback(data))
            .catch(err => callback({error: err.message}));
        """
        
        fetch_result = driver.execute_async_script(js_fetch, 30)
        
        if fetch_result:
            print(f"📝 响应状态码: {fetch_result.get('status')}")
            if fetch_result.get('text'):
                print(f"📝 响应长度: {len(fetch_result['text'])}")
                print(f"📝 响应前200字符: {fetch_result['text'][:200]}")
                
                try:
                    fetch_data = json.loads(fetch_result['text'])
                    if 'threads' in fetch_data:
                        threads = fetch_data['threads']
                        print(f"✅ 获取到 {len(threads)} 个会话")
                        all_threads.extend([{"id": t.get("id"), "title": t.get("title", "无标题")} for t in threads])
                except:
                    pass
        
        if all_threads:
            unique_threads = []
            seen_ids = set()
            for t in all_threads:
                if t['id'] not in seen_ids:
                    seen_ids.add(t['id'])
                    unique_threads.append(t)
            
            print(f"\n📊 共找到 {len(unique_threads)} 个唯一会话")
            
            summary = f"# 豆包会话列表\n\n"
            summary += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            summary += f"会话数量: {len(unique_threads)}\n\n"
            
            for thread in unique_threads:
                summary += f"- [{thread['title']}](https://www.doubao.com/chat/{thread['id']})\n"
            
            with open(os.path.join(save_dir, "会话列表.md"), "w", encoding="utf-8") as f:
                f.write(summary)
            
            print(f"\n✅ 已生成会话列表: {os.path.abspath(os.path.join(save_dir, '会话列表.md'))}")
            
            print("\n📥 正在尝试获取详细消息...")
            success_count = 0
            
            for idx, thread in enumerate(unique_threads[:5], 1):
                print(f"\n[{idx}/5] 正在获取: {thread['title']}")
                
                js_get_messages = f"""
                    const callback = arguments[arguments.length - 1];
                    fetch('https://www.doubao.com/api/chat/history?thread_id={thread['id']}&cursor=&limit=100', {{
                        credentials: 'include'
                    }})
                    .then(response => response.text())
                    .then(text => callback(text))
                    .catch(err => callback(null));
                """
                
                try:
                    messages_text = driver.execute_async_script(js_get_messages, 30)
                    
                    if messages_text:
                        try:
                            messages_data = json.loads(messages_text)
                            messages = messages_data.get("messages", [])
                            
                            if messages:
                                md_content = f"# {thread['title']}\n\n"
                                md_content += f"会话ID: {thread['id']}\n\n"
                                
                                for msg in messages:
                                    role = msg.get("role", "")
                                    content = msg.get("content", "")
                                    
                                    if role == "user":
                                        md_content += f"**👤 我:**\n{content}\n\n"
                                    elif role == "assistant":
                                        md_content += f"**🤖 豆包:**\n{content}\n\n"
                                
                                filename = f"{thread['id']}_{thread['title'][:20]}.md"
                                filepath = os.path.join(save_dir, filename)
                                
                                with open(filepath, "w", encoding="utf-8") as f:
                                    f.write(md_content)
                                
                                success_count += 1
                                print(f"✅ 已保存")
                            else:
                                print(f"ℹ️ 无消息")
                        except:
                            print(f"❌ 解析失败")
                    else:
                        print(f"❌ 获取失败")
                except:
                    print(f"❌ 请求失败")
            
            print(f"\n🎉 完成！成功获取 {success_count}/5 个会话的详细内容")
            
        else:
            print("\n❌ 未找到会话数据")
            
    except Exception as e:
        print(f"\n❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
    
    driver.quit()

if __name__ == "__main__":
    scrape_doubao_chats()