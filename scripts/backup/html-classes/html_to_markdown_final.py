import os
import re
from datetime import datetime

def parse_html_file(file_path):
    """解析单个HTML文件，提取聊天消息"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        title_match = re.search(r'<title>([^<]+)</title>', content)
        title = title_match.group(1) if title_match else os.path.basename(file_path)
        title = re.sub(r'\s+', ' ', title).strip()
        
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        text_content = re.sub(r'<[^>]+>', '\n', content)
        text_content = re.sub(r'\s+', '\n', text_content)
        text_content = re.sub(r'\n{3,}', '\n\n', text_content).strip()
        
        lines = text_content.split('\n')
        clean_lines = []
        
        nav_keywords = ['新对话', 'Ctrl K', 'AI', '创作', '云盘', '更多', '历史对话', '搜索', 
                       '消息', '通知', '设置', '帮助', '退出', '登录', '注册', '会员']
        
        for line in lines:
            line = line.strip()
            if len(line) < 5:
                continue
            
            is_nav = False
            for keyword in nav_keywords:
                if keyword in line:
                    is_nav = True
                    break
            
            if is_nav:
                continue
            
            if '由 AI 生成，请仔细甄别' in line:
                continue
            
            if 'Export' in line or '导出' in line or '下载' in line:
                continue
            
            if line.startswith('##') or line.startswith('#'):
                continue
            
            clean_lines.append(line)
        
        content_text = '\n'.join(clean_lines)
        
        if not content_text:
            return None
        
        return {
            'title': title,
            'file_name': os.path.basename(file_path),
            'content': content_text
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
        clean_title = chat['title'].replace('#', '').replace('*', '').replace('|', '-')
        md_content += f"## {idx}. {clean_title}\n\n"
        md_content += f"**来源文件:** {chat['file_name']}\n\n"
        md_content += f"{chat['content']}\n\n"
        md_content += "---\n\n"
    
    return md_content

def main():
    html_dir = 'h:/github/md/html'
    output_file = 'h:/github/md/聊天记录汇总_最终版.md'
    
    if not os.path.exists(html_dir):
        print(f"错误: 目录不存在 {html_dir}")
        return
    
    html_files = sorted([f for f in os.listdir(html_dir) if f.endswith('.htm')])
    print(f"找到 {len(html_files)} 个HTML文件")
    
    all_chats = []
    for file_name in html_files:
        file_path = os.path.join(html_dir, file_name)
        print(f"正在处理: {file_name}")
        chat_data = parse_html_file(file_path)
        if chat_data and chat_data['content']:
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