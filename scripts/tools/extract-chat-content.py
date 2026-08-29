import os
import re
from datetime import datetime

def extract_meaningful_content(file_path):
    """提取有意义的聊天内容"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        title_match = re.search(r'<title>([^<]+)</title>', content)
        title = title_match.group(1) if title_match else os.path.basename(file_path)
        title = re.sub(r'\s+', ' ', title).strip()
        title = title.replace('| 豆包', '').replace('豆包 - ', '')
        
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        
        content = re.sub(r'<svg[^>]*>.*?</svg>', '', content, flags=re.DOTALL)
        content = re.sub(r'<path[^>]*>', '', content)
        content = re.sub(r'<[^>]+>', '\n', content)
        content = re.sub(r'\s+', '\n', content)
        content = re.sub(r'\n{3,}', '\n\n', content).strip()
        
        lines = content.split('\n')
        
        nav_keywords = ['新对话', 'Ctrl K', 'AI', '创作', '云盘', '更多', '历史对话', '搜索',
                       '消息', '通知', '设置', '帮助', '退出', '登录', '注册', '会员',
                       'Export', '导出', '下载', 'PDF', 'JSON', 'Word', '复制', '分享',
                       '由 AI 生成，请仔细甄别', '内容由豆包', '请仔细甄别', '豆包',
                       '×', '搜索历史对话', '清空历史', '拖拽排序', '收起', '展开']
        
        meaningful_lines = []
        for line in lines:
            line = line.strip()
            
            if len(line) < 10:
                continue
            
            is_noise = False
            for keyword in nav_keywords:
                if keyword == line or (len(keyword) > 3 and keyword in line):
                    is_noise = True
                    break
            
            if is_noise:
                continue
            
            if re.match(r'^\d+$', line):
                continue
            
            if line.count('·') > 5 or line.count('-') > 10:
                continue
            
            meaningful_lines.append(line)
        
        if len(meaningful_lines) < 2:
            return None
        
        full_content = '\n\n'.join(meaningful_lines)
        
        return {
            'title': title,
            'file_name': os.path.basename(file_path),
            'content': full_content
        }
    
    except Exception as e:
        print(f"解析 {file_path} 失败: {e}")
        return None

def convert_to_markdown(all_chats):
    """转换为简洁的Markdown格式"""
    md_content = f"# 豆包聊天记录汇总\n\n"
    md_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    md_content += f"会话数量: {len(all_chats)}\n\n"
    
    for idx, chat in enumerate(all_chats, 1):
        clean_title = chat['title'].replace('#', '').replace('*', '').replace('|', '-')
        md_content += f"---\n\n"
        md_content += f"## {idx}. {clean_title}\n\n"
        md_content += f"**来源文件:** {chat['file_name']}\n\n"
        md_content += f"{chat['content']}\n\n"
    
    return md_content

def main():
    html_dir = 'h:/github/md/html'
    output_file = 'h:/github/md/豆包聊天记录_优化版.md'
    
    if not os.path.exists(html_dir):
        print(f"错误: 目录不存在 {html_dir}")
        return
    
    html_files = sorted([f for f in os.listdir(html_dir) if f.endswith('.htm')])
    print(f"找到 {len(html_files)} 个HTML文件")
    
    all_chats = []
    for file_name in html_files:
        file_path = os.path.join(html_dir, file_name)
        print(f"正在处理: {file_name}")
        chat_data = extract_meaningful_content(file_path)
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