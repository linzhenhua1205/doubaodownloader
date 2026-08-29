import requests
import json
import time
import os
from datetime import datetime

# ===================== 配置区 =====================
# 请手动获取Cookie并填写在这里
# 获取方法：
# 1. 打开Chrome浏览器，访问 https://www.doubao.com/chat
# 2. 登录账号后按 F12 打开开发者工具
# 3. 切换到 Network 面板，刷新页面
# 4. 找到任意请求，复制 Request Headers 中的 Cookie 值
COOKIE = ""

# 保存目录
SAVE_DIR = "./doubaoall"
# ===================================================

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.7778.168 Safari/537.36",
    "Cookie": COOKIE,
    "Referer": "https://www.doubao.com/chat",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
}

def test_cookie():
    """测试Cookie是否有效"""
    url = "https://www.doubao.com/api/thread/list?cursor=&limit=1"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            try:
                data = r.json()
                if "threads" in data:
                    print("✅ Cookie有效！")
                    return True
                else:
                    print(f"❌ 响应异常: {json.dumps(data, ensure_ascii=False)[:200]}")
                    return False
            except json.JSONDecodeError:
                print(f"❌ 响应不是JSON: {r.text[:200]}")
                return False
        elif r.status_code == 401:
            print("❌ Cookie已过期或无效")
            return False
        else:
            print(f"❌ 请求失败，状态码: {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def get_all_threads():
    """获取所有会话列表"""
    all_threads = []
    cursor = ""
    page = 1

    print("正在获取所有会话列表...")

    while True:
        url = f"https://www.doubao.com/api/thread/list?cursor={cursor}&limit=30"
        try:
            r = requests.get(url, headers=headers, timeout=10)
            
            if r.status_code != 200:
                print(f"[ERROR] HTTP状态码: {r.status_code}")
                break
            
            data = r.json()
            threads = data.get("threads", [])
            if not threads:
                break

            all_threads.extend(threads)
            cursor = data.get("next_cursor", "")
            print(f"第 {page} 页 → 已获取 {len(all_threads)} 个会话")
            page += 1
            time.sleep(0.5)

            if not cursor:
                break
        except Exception as e:
            print(f"[ERROR] 请求失败: {e}")
            break

    return all_threads

def get_thread_detail(thread_id):
    """获取单个会话的完整对话内容"""
    url = f"https://www.doubao.com/api/chat/history?thread_id={thread_id}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
        else:
            print(f"[ERROR] 获取对话失败，状态码: {r.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] 获取对话失败: {e}")
        return None

def save_all_messages(threads):
    """保存所有会话"""
    os.makedirs(SAVE_DIR, exist_ok=True)
    dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")

    all_data = []
    md_all = "# 豆包全量历史对话备份\n\n"

    print("\n开始导出对话详情...")

    for idx, thread in enumerate(threads, 1):
        tid = thread.get("id")
        title = thread.get("title", "无标题")
        create_time = thread.get("create_time", "")

        print(f"[{idx}/{len(threads)}] 导出：{title}")

        detail = get_thread_detail(tid)
        if not detail:
            continue

        all_data.append({
            "title": title,
            "thread_id": tid,
            "create_time": create_time,
            "messages": detail
        })

        md_all += f"# {title}\n"
        md_all += f"会话ID：{tid}\n创建时间：{create_time}\n\n"

        messages = detail if isinstance(detail, list) else detail.get("messages", [])
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")

            if role == "user":
                md_all += f"### 👤 我：\n{content}\n\n"
            elif role == "assistant":
                md_all += f"### 🤖 AI：\n{content}\n\n"

        md_all += "---\n\n"
        time.sleep(0.3)

    json_path = os.path.join(SAVE_DIR, f"全量备份_{dt_str}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    md_path = os.path.join(SAVE_DIR, f"全量备份_{dt_str}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_all)

    print(f"\n✅ 导出完成！共 {len(threads)} 个会话")
    print(f"📂 保存路径：{os.path.abspath(SAVE_DIR)}")

def show_cookie_guide():
    """显示获取Cookie的指南"""
    guide = """
╔══════════════════════════════════════════════════════════════════════╗
║                      获取豆包Cookie指南                              ║
╚══════════════════════════════════════════════════════════════════════╝

步骤1：打开Chrome浏览器，访问豆包官网
       https://www.doubao.com/chat

步骤2：登录你的账号

步骤3：按 F12 打开开发者工具

步骤4：切换到 Network 面板

步骤5：刷新页面（按 F5）

步骤6：在 Network 面板中找到任意一个请求
       推荐找 thread/list 或 chat/history 相关的请求

步骤7：点击该请求，在右侧找到 Request Headers

步骤8：找到 Cookie 字段，复制其值

步骤9：将复制的Cookie粘贴到脚本第13行的 COOKIE = "" 中

示例：
COOKIE = "i18next=zh; sid_tt=abc123; sessionid=xyz789; ..."

注意：Cookie会定期过期，需要重新获取
"""
    print(guide)

if __name__ == "__main__":
    print("="*60)
    print("          豆包对话历史备份工具")
    print("="*60)
    
    if not COOKIE or COOKIE.strip() == "":
        show_cookie_guide()
        print("\n[ERROR] 请先在配置区填写有效的Cookie！")
        exit(1)
    
    print(f"\n📋 Cookie长度: {len(COOKIE)} 字符")
    print("🔍 正在测试Cookie有效性...")
    
    if not test_cookie():
        print("\n❌ Cookie无效，请重新获取")
        show_cookie_guide()
        exit(1)
    
    print("\n🚀 开始获取对话历史...")
    threads = get_all_threads()
    
    if threads:
        save_all_messages(threads)
    else:
        print("\n❌ 未获取到任何会话")
