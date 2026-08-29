import os
import re
from datetime import datetime

def extract_chat_pairs(file_path):
    """智能提取聊天消息对"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        title_match = re.search(r'<title>([^<]+)</title>', content)
        title = title_match.group(1) if title_match else os.path.basename(file_path)
        title = re.sub(r'\s+', ' ', title).strip()
        
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        
        clean_content = re.sub(r'<[^>]+>', '\n', content)
        clean_content = re.sub(r'\s+', '\n', clean_content)
        clean_content = re.sub(r'\n{3,}', '\n\n', clean_content).strip()
        
        lines = clean_content.split('\n')
        
        nav_keywords = ['新对话', 'Ctrl K', 'AI', '创作', '云盘', '更多', '历史对话', '搜索',
                       '消息', '通知', '设置', '帮助', '退出', '登录', '注册', '会员',
                       'Export', '导出', '下载', 'PDF', 'JSON', 'Word', '复制', '分享']
        
        valid_lines = []
        for line in lines:
            line = line.strip()
            if len(line) < 5:
                continue
            
            is_noise = False
            for keyword in nav_keywords:
                if keyword in line:
                    is_noise = True
                    break
            
            if is_noise:
                continue
            
            if '由 AI 生成，请仔细甄别' in line:
                continue
            
            valid_lines.append(line)
        
        if len(valid_lines) < 2:
            return None
        
        chat_pairs = []
        current_pair = []
        
        for line in valid_lines:
            if line.endswith('？') or line.endswith('？') or line.endswith('!') or line.endswith('！'):
                if current_pair:
                    chat_pairs.append(('\n'.join(current_pair), ''))
                    current_pair = []
                current_pair.append(line)
            else:
                if current_pair:
                    current_pair.append(line)
                else:
                    chat_pairs.append(('', line))
        
        if current_pair:
            if len(chat_pairs) > 0 and not chat_pairs[-1][1]:
                chat_pairs[-1] = (chat_pairs[-1][0], '\n'.join(current_pair))
            else:
                chat_pairs.append(('\n'.join(current_pair), ''))
        
        clean_pairs = []
        for user, assistant in chat_pairs:
            user = user.strip()
            assistant = assistant.strip()
            if user or assistant:
                clean_pairs.append((user, assistant))
        
        return {
            'title': title,
            'file_name': os.path.basename(file_path),
            'pairs': clean_pairs
        }
    
    except Exception as e:
        print(f"解析 {file_path} 失败: {e}")
        return None

def convert_to_markdown(all_chats):
    """转换为清晰的Markdown格式"""
    md_content = f"# 豆包聊天记录汇总\n\n"
    md_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md_content += f"会话数量: {len(all_chats)}\n\n"
    md_content += "---\n\n"
    
    for idx, chat in enumerate(all_chats, 1):
        clean_title = chat['title'].replace('#', '').replace('*', '').replace('|', '-')
        md_content += f"## {idx}. {clean_title}\n\n"
        
        for user_msg, ai_msg in chat['pairs']:
            if user_msg:
                md_content += f"**👤 我:**\n{user_msg}\n\n"
            if ai_msg:
                md_content += f"**🤖 豆包:**\n{ai_msg}\n\n"
        
        md_content += "---\n\n"
    
    return md_content

def main():
    html_dir = 'h:/github/md/html'
    output_file = 'h:/github/md/聊天记录_清晰版.md'
    
    if not os.path.exists(html_dir):
        print(f"错误: 目录不存在 {html_dir}")
        return
    
    html_files = sorted([f for f in os.listdir(html_dir) if f.endswith('.htm')])
    print(f"找到 {len(html_files)} 个HTML文件")
    
    all_chats = []
    for file_name in html_files:
        file_path = os.path.join(html_dir, file_name)
        print(f"正在处理: {file_name}")
        chat_data = extract_chat_pairs(file_path)
        if chat_data and chat_data['pairs']:
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