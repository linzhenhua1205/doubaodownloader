import requests
import json
import os
from datetime import datetime

def test_api_and_export():
    print("\n📦 豆包对话历史导出工具")
    print("=" * 40)
    
    print("\n请手动获取Cookie：")
    print("1. 打开Chrome浏览器，访问 https://www.doubao.com/chat")
    print("2. 登录你的账号")
    print("3. 按 F12 打开开发者工具")
    print("4. 切换到 Network 面板")
    print("5. 刷新页面")
    print("6. 找到任意请求，复制 Cookie 值")
    print("\n" + "=" * 40)
    
    cookie = input("请粘贴Cookie: ").strip()
    
    if not cookie:
        print("❌ Cookie不能为空")
        return
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.7778.168 Safari/537.36",
        "Cookie": cookie,
        "Referer": "https://www.doubao.com/chat",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Origin": "https://www.doubao.com"
    }
    
    print("\n🔍 正在测试API...")
    url = "https://www.doubao.com/api/thread/list?cursor=&limit=50"
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        
        print(f"\n📝 响应状态码: {r.status_code}")
        print(f"📝 响应长度: {len(r.text)}")
        print(f"📝 响应内容前500字符:\n{r.text[:500]}")
        
        if r.status_code == 200:
            try:
                data = r.json()
                print(f"\n📝 数据结构: {list(data.keys())}")
                
                if "threads" in data:
                    threads = data["threads"]
                    print(f"✅ 找到 {len(threads)} 个会话")
                    
                    save_dir = "./doubao_api_export"
                    os.makedirs(save_dir, exist_ok=True)
                    
                    all_threads = []
                    
                    for thread in threads:
                        thread_id = thread.get("id")
                        title = thread.get("title", "无标题")
                        title = title.replace("/", "-").replace("\\", "-")
                        
                        print(f"\n📥 正在获取: {title}")
                        
                        chat_url = f"https://www.doubao.com/api/chat/history?thread_id={thread_id}&cursor=&limit=100"
                        chat_r = requests.get(chat_url, headers=headers, timeout=10)
                        
                        if chat_r.status_code == 200:
                            try:
                                chat_data = chat_r.json()
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
                                    print(f"✅ 已保存")
                                else:
                                    print(f"ℹ️ 无消息")
                            except json.JSONDecodeError:
                                print(f"❌ 解析失败")
                        else:
                            print(f"❌ 请求失败: {chat_r.status_code}")
                    
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
                    print(f"❌ 响应中没有threads字段")
                    
            except json.JSONDecodeError:
                print(f"❌ 响应不是JSON格式")
        else:
            print(f"❌ 请求失败，状态码: {r.status_code}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")

if __name__ == "__main__":
    test_api_and_export()