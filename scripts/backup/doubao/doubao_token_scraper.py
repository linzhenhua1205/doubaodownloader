import os
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

CHROME_PATH = "h:/github/md/chrome-win64/chrome-win64/chrome.exe"

def scrape_with_token():
    """从localStorage获取token并使用"""
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
    
    save_dir = "./doubao_token_export"
    os.makedirs(save_dir, exist_ok=True)
    
    try:
        print("\n🔍 正在查找认证信息...")
        
        js_get_storage = """
            const result = {};
            
            const ls = window.localStorage;
            for (let i = 0; i < ls.length; i++) {
                const key = ls.key(i);
                if (key.includes('token') || key.includes('Token') || 
                    key.includes('session') || key.includes('Session') ||
                    key.includes('auth') || key.includes('Auth')) {
                    result[key] = ls.getItem(key);
                }
            }
            
            const ss = window.sessionStorage;
            for (let i = 0; i < ss.length; i++) {
                const key = ss.key(i);
                if (key.includes('token') || key.includes('Token') || 
                    key.includes('session') || key.includes('Session') ||
                    key.includes('auth') || key.includes('Auth')) {
                    result[key] = ss.getItem(key);
                }
            }
            
            return result;
        """
        
        tokens = driver.execute_script(js_get_storage)
        
        print(f"\n✅ 找到 {len(tokens)} 个认证相关的键值对")
        for key, value in tokens.items():
            print(f"  {key}: {value[:50]}..." if len(str(value)) > 50 else f"  {key}: {value}")
        
        print("\n🔍 正在获取Cookie...")
        cookies = driver.get_cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        print(f"✅ 获取到 {len(cookies)} 个Cookie")
        
        print("\n📡 正在尝试使用浏览器上下文获取会话列表...")
        
        js_get_threads = """
            const callback = arguments[arguments.length - 1];
            
            async function getThreads() {
                try {
                    const response = await fetch('https://www.doubao.com/api/thread/list?cursor=&limit=50', {
                        credentials: 'include',
                        headers: {
                            'Accept': 'application/json, text/plain, */*',
                            'Referer': 'https://www.doubao.com/chat',
                            'User-Agent': navigator.userAgent,
                            'X-Requested-With': 'XMLHttpRequest'
                        }
                    });
                    
                    const text = await response.text();
                    callback({status: response.status, text: text});
                } catch(e) {
                    callback({error: e.message});
                }
            }
            
            getThreads();
        """
        
        result = driver.execute_async_script(js_get_threads, 30)
        
        if result:
            print(f"\n📝 响应状态码: {result.get('status')}")
            
            if result.get('text'):
                print(f"📝 响应长度: {len(result['text'])}")
                
                try:
                    data = json.loads(result['text'])
                    print(f"📝 数据结构: {list(data.keys())}")
                    
                    if 'threads' in data:
                        threads = data['threads']
                        print(f"✅ 获取到 {len(threads)} 个会话")
                        
                        summary = f"# 豆包会话列表\n\n"
                        summary += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        summary += f"会话数量: {len(threads)}\n\n"
                        
                        for thread in threads:
                            thread_id = thread.get("id")
                            title = thread.get("title", "无标题")
                            summary += f"- [{title}](https://www.doubao.com/chat/{thread_id})\n"
                        
                        with open(os.path.join(save_dir, "会话列表.md"), "w", encoding="utf-8") as f:
                            f.write(summary)
                        
                        print(f"\n✅ 已生成会话列表")
                        
                        print("\n📥 正在尝试获取详细消息...")
                        success_count = 0
                        
                        for idx, thread in enumerate(threads[:3], 1):
                            print(f"\n[{idx}/3] 正在获取: {thread.get('title', '无标题')}")
                            
                            js_get_messages = f"""
                                const callback = arguments[arguments.length - 1];
                                
                                async function getMessages() {{
                                    try {{
                                        const response = await fetch('https://www.doubao.com/api/chat/history?thread_id={thread.get('id')}&cursor=&limit=100', {{
                                            credentials: 'include',
                                            headers: {{
                                                'Accept': 'application/json, text/plain, */*',
                                                'Referer': 'https://www.doubao.com/chat'
                                            }}
                                        }});
                                        
                                        const text = await response.text();
                                        callback({{status: response.status, text: text}});
                                    }} catch(e) {{
                                        callback({{error: e.message}});
                                    }}
                                }}
                                
                                getMessages();
                            """
                            
                            msg_result = driver.execute_async_script(js_get_messages, 30)
                            
                            if msg_result and msg_result.get('text'):
                                try:
                                    msg_data = json.loads(msg_result['text'])
                                    messages = msg_data.get("messages", [])
                                    
                                    if messages:
                                        md_content = f"# {thread.get('title', '无标题')}\n\n"
                                        md_content += f"会话ID: {thread.get('id')}\n\n"
                                        
                                        for msg in messages:
                                            role = msg.get("role", "")
                                            content = msg.get("content", "")
                                            
                                            if role == "user":
                                                md_content += f"**👤 我:**\n{content}\n\n"
                                            elif role == "assistant":
                                                md_content += f"**🤖 豆包:**\n{content}\n\n"
                                        
                                        filename = f"{thread.get('id')}_{thread.get('title', '无标题')[:20]}.md"
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
                        
                        print(f"\n🎉 完成！成功获取 {success_count}/3 个会话")
                        
                    else:
                        print(f"❌ 响应中没有threads字段")
                        
                except json.JSONDecodeError:
                    print(f"❌ 响应不是JSON")
                    print(f"📝 响应内容: {result['text'][:200]}")
            else:
                print("❌ 响应为空")
        else:
            print("❌ 请求失败")
            
    except Exception as e:
        print(f"\n❌ 导出失败: {e}")
        import traceback
        traceback.print_exc()
    
    driver.quit()

if __name__ == "__main__":
    scrape_with_token()