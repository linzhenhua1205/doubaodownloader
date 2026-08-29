import re
import os
from datetime import datetime

def parse_mhtml_file(file_path):
    """解析mhtml文件提取会话列表"""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    print("正在搜索会话链接...")
    
    thread_pattern = r'https://www\.doubao\.com/chat/(\d+)'
    threads = re.findall(thread_pattern, content)
    threads = list(set(threads))
    print(f"找到 {len(threads)} 个会话ID")
    
    if threads:
        print("\n会话ID列表:")
        for tid in threads[:10]:
            print(f"  {tid}")
        if len(threads) > 10:
            print(f"  ... 还有 {len(threads) - 10} 个")
    
    print("\n正在搜索用户和AI消息...")
    
    content = re.sub(r'=\r\n', '', content)
    content = re.sub(r'=3D', '=', content)
    
    user_pattern = re.compile(r'(?:user|User|我|提问):?\s*([^\n<>]{20,})', re.IGNORECASE)
    ai_pattern = re.compile(r'(?:assistant|AI|豆包|回答):?\s*([^\n<>]{20,})', re.IGNORECASE)
    
    user_matches = user_pattern.findall(content)[:10]
    ai_matches = ai_pattern.findall(content)[:10]
    
    print("\n用户消息片段:")
    for i, msg in enumerate(user_matches, 1):
        print(f"{i}. {msg[:50]}...")
    
    print("\nAI消息片段:")
    for i, msg in enumerate(ai_matches, 1):
        print(f"{i}. {msg[:50]}...")
    
    return threads

def extract_json_data(content):
    """从HTML中提取JSON数据"""
    print("\n正在搜索JSON数据...")
    
    json_pattern = r'window\.initialState\s*=\s*({.*?});'
    match = re.search(json_pattern, content, re.DOTALL)
    
    if match:
        try:
            import json
            data = json.loads(match.group(1))
            print(f"找到initialState，包含键: {list(data.keys())}")
            
            if 'chat' in data:
                chat_data = data['chat']
                print(f"chat数据包含键: {list(chat_data.keys())}")
                
                if 'threads' in chat_data:
                    threads = chat_data['threads']
                    print(f"找到 {len(threads)} 个会话")
                    return threads
        except Exception as e:
            print(f"解析JSON失败: {e}")
    
    return None

def main():
    file_path = 'h:/github/md/豆包 - 字节跳动旗下 AI 智能助手.mhtml'
    
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    content = re.sub(r'=\r\n', '', content)
    content = re.sub(r'=3D', '=', content)
    
    threads = extract_json_data(content)
    
    if threads:
        save_dir = "./doubao_mhtml_export"
        os.makedirs(save_dir, exist_ok=True)
        
        all_threads_info = []
        
        for thread in threads:
            thread_id = thread.get("id")
            title = thread.get("title", "无标题")
            title = title.replace("/", "-").replace("\\", "-")
            
            print(f"\n📥 会话: {title}")
            
            all_threads_info.append({"id": thread_id, "title": title})
        
        summary = f"# 豆包会话列表\n\n"
        summary += f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"会话数量: {len(all_threads_info)}\n\n"
        
        for thread in all_threads_info:
            summary += f"- [{thread['title']}](https://www.doubao.com/chat/{thread['id']})\n"
        
        with open(os.path.join(save_dir, "会话列表.md"), "w", encoding="utf-8") as f:
            f.write(summary)
        
        print(f"\n✅ 已生成会话列表: {os.path.abspath(save_dir)}")
    else:
        print("\n❌ 未找到会话数据")

if __name__ == "__main__":
    main()