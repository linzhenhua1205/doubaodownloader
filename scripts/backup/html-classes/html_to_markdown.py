import os
import re
from datetime import datetime

def extract_chat_content(html_content):
    """从HTML内容中提取聊天消息"""
    messages = []
    
    patterns = [
        (r'<div[^>]*role="user"[^>]*>.*?</div>', r'<div[^>]*role="assistant"[^>]*>.*?</div>'),
        (r'<div[^>]*class="[^"]*user[^"]*"[^>]*>.*?</div>', r'<div[^>]*class="[^"]*assistant[^"]*"[^>]*>.*?</div>'),
        (r'<div[^>]*class="[^"]*chat-message[^"]*user[^"]*"[^>]*>.*?</div>', r'<div[^>]*class="[^"]*chat-message[^"]*assistant[^"]*"[^>]*>.*?</div>'),
    ]
    
    clean_text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
    clean_text = re.sub(r'<style[^>]*>.*?</style>', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'<!--.*?-->', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    if clean_text:
        lines = clean_text.split('。')
        for i, line in enumerate(lines):
            line = line.strip()
            if line and len(line) > 5:
                if i % 2 == 0:
                    messages.append(('user', line))
                else:
                    messages.append(('assistant', line))
    
    return messages

def parse_html_file(file_path):
    """解析单个HTML文件"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        messages = extract_chat_content(content)
        
        title_match = re.search(r'<title>([^<]+)</title>', content)
        title = title_match.group(1) if title_match else os.path.basename(file_path)
        title = re.sub(r'\s+', ' ', title).strip()
        
        return {
            'title': title,
            'file_name': os.path.basename(file_path),
            'messages': messages
        }
    except Exception as e:
        print(f"解析 {file_path} 失败: {e}")
        return None

def convert_to_markdown(all_chats):
    """将所有聊天转换为Markdown格式"""
    md_content = f"# 豆包聊天记录汇总\n\n"
    md_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md_content += f"会话数量: {len(all_chats)}\n\n"
    md_content += "---\n\n"
    
    for idx, chat in enumerate(all_chats, 1):
        md_content += f"## {idx}. {chat['title']}\n"
        md_content += f"来源文件: {chat['file_name']}\n\n"
        
        for msg in chat['messages']:
            role, content = msg
            if role == 'user':
                md_content += f"### 👤 我:\n{content}\n\n"
            else:
                md_content += f"### 🤖 AI:\n{content}\n\n"
        
        md_content += "---\n\n"
    
    return md_content

def main():
    html_dir = 'h:/github/md/html'
    output_file = 'h:/github/md/聊天记录汇总.md'
    
    if not os.path.exists(html_dir):
        print(f"错误: 目录不存在 {html_dir}")
        return
    
    html_files = [f for f in os.listdir(html_dir) if f.endswith('.htm')]
    print(f"找到 {len(html_files)} 个HTML文件")
    
    all_chats = []
    for file_name in html_files:
        file_path = os.path.join(html_dir, file_name)
        print(f"正在处理: {file_name}")
        chat_data = parse_html_file(file_path)
        if chat_data and chat_data['messages']:
            all_chats.append(chat_data)
    
    print(f"\n成功解析 {len(all_chats)} 个会话")
    
    if all_chats:
        markdown = convert_to_markdown(all_chats)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        print(f"\n✅ 已生成汇总文件: {output_file}")
    else:
        print("\n❌ 未找到任何聊天内容")

if __name__ == "__main__":
    main()