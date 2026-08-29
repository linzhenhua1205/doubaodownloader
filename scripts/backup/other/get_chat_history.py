import requests
import json
import os
from datetime import datetime

def get_chat_history():
    print("\n📦 豆包对话历史导出工具")
    print("=" * 40)
    
    session_ids = [
        '38427637805809666', '38426963711', '38427584594056', '38427589131432962',
        '38427638865749762', '38427637826769922', '38427637820934658', '38427400915005698',
        '38427637805842946', '38427826617107714', '38427826638312450', '3842797459',
        '38427826665353474', '38427637714131202', '38424758047976194', '38427061820972290',
        '38427399254671106', '38427826613706', '38427919015290370', '38427826615751170',
        '1718552759971586', '38427939284126210', '38427584609621250', '38425595322360322',
        '38421730541203970', '38426891907621890', '38427974657209346', '38427584942108418',
        '38427850262526722', '38427809776218114', '38427602387411458', '38427637820712194',
        '384276025938', '38427386869406466', '38427826492174594', '38427602578578434',
        '384275846121', '38427186626698754', '38427602605952002', '38427370678011650',
        '38427827675548162', '38427826601558530', '38425588388449794', '38427638765944578',
        '38427903156731394', '38427808520454658', '38427808617154306', '38427440307377922',
        '38427441600090882', '38427585922978818', '15274536665085954', '38427637644438530',
        '38427827760432642', '38427808627417346', '38427584575475970', '384278266286',
        '38427533962969858', '38427370850182914', '38427638881101058', '38427584844664578',
        '38427585995635202', '384275846032', '38427637784224', '38427826562018',
        '38427637650773506', '38427584612894466', '38427603667368194', '38427251949679362',
        '38426910077387522', '38427884487302402', '38427602594264578', '38427571203019522',
        '38427602518257666', '38427809578425858', '38427827760336898', '3842551812',
        '3842758771', '38427637814405122', '38427602441850114', '38427584600458754',
        '38427808487491330', '38427637763369986', '38427884505547010', '38427826671772162',
        '38427452685858050', '38426954790184706'
    ]
    
    print(f"找到 {len(session_ids)} 个会话ID")
    
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
    
    save_dir = "./doubao_history_from_ids"
    os.makedirs(save_dir, exist_ok=True)
    
    all_threads = []
    success_count = 0
    
    for idx, thread_id in enumerate(session_ids, 1):
        print(f"\n📥 [{idx}/{len(session_ids)}] 正在获取会话: {thread_id}")
        
        url = f"https://www.doubao.com/api/chat/history?thread_id={thread_id}&cursor=&limit=100"
        
        try:
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code == 200:
                try:
                    data = r.json()
                    messages = data.get("messages", [])
                    
                    if messages:
                        title = messages[0].get("content", "")[:20] if messages else "无标题"
                        title = title.replace("/", "-").replace("\\", "-")
                        
                        md_content = f"# 会话 {thread_id}\n\n"
                        
                        for msg in messages:
                            role = msg.get("role", "")
                            content = msg.get("content", "")
                            
                            if role == "user":
                                md_content += f"**👤 我:**\n{content}\n\n"
                            elif role == "assistant":
                                md_content += f"**🤖 豆包:**\n{content}\n\n"
                        
                        filename = f"{thread_id}.md"
                        filepath = os.path.join(save_dir, filename)
                        
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(md_content)
                        
                        all_threads.append({"id": thread_id, "title": title, "messages": len(messages)})
                        success_count += 1
                        print(f"✅ 已保存，共 {len(messages)} 条消息")
                    else:
                        print(f"ℹ️ 无消息")
                except json.JSONDecodeError:
                    print(f"❌ 解析失败")
            else:
                print(f"❌ 请求失败: {r.status_code}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    summary = f"# 豆包聊天记录汇总\n\n"
    summary += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary += f"会话总数: {len(session_ids)}\n"
    summary += f"成功导出: {success_count}\n\n"
    
    for thread in all_threads:
        summary += f"- [{thread['title']}]({thread['id']}.md) - {thread['messages']} 条消息\n"
    
    with open(os.path.join(save_dir, "汇总.md"), "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"\n🎉 导出完成！共成功导出 {success_count}/{len(session_ids)} 个会话")
    print(f"📁 保存目录: {os.path.abspath(save_dir)}")

if __name__ == "__main__":
    get_chat_history()