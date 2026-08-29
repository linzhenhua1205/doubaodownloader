import os
import re
from datetime import datetime

class ImprovedDoubaoParser:
    """改进的豆包HTML解析器"""
    
    def __init__(self):
        self.nav_keywords = [
            '新对话', 'Ctrl K', 'AI', '创作', '云盘', '更多', '历史对话', '搜索',
            '消息', '通知', '设置', '帮助', '退出', '登录', '注册', '会员',
            'Export', '导出', '下载', 'PDF', 'JSON', 'Word', '复制', '分享',
            '由 AI 生成，请仔细甄别', '内容由豆包', '请仔细甄别', '豆包',
            '×', '搜索历史对话', '清空历史', '拖拽排序', '收起', '展开',
            '豆包 - 字节跳动旗下 AI 智能助手', '聊天', '发送', '输入消息',
            '输入框', '输入你的问题', '问豆包'
        ]
        
        self.user_indicators = ['我:', '提问:', '用户:', '问：', '问:', '请问:', '如何', '什么是', '为什么']
        self.assistant_indicators = ['豆包:', 'AI:', '回答:', '助手:', '总结:', '分析:', '首先', '其次', '最后', '一、', '二、', '三、', '四、', '五、']
    
    def clean_html(self, content):
        """清理HTML标签和脚本"""
        content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
        content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
        content = re.sub(r'<svg[^>]*>.*?</svg>', '', content, flags=re.DOTALL)
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        content = re.sub(r'<[^>]+>', '\n', content)
        content = re.sub(r'=\r\n', '', content)
        content = re.sub(r'=3D', '=', content)
        content = re.sub(r'\s+', '\n', content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        return content.strip()
    
    def is_noise(self, line):
        """判断是否为噪音内容"""
        line = line.strip()
        
        if len(line) < 8:
            return True
        
        for keyword in self.nav_keywords:
            if keyword == line or (len(keyword) > 3 and keyword in line):
                return True
        
        if re.match(r'^\d+$', line):
            return True
        
        if line.count('·') > 5 or line.count('-') > 10:
            return True
        
        return False
    
    def extract_title(self, content):
        """提取标题"""
        title_match = re.search(r'<title>([^<]+)</title>', content)
        if title_match:
            title = title_match.group(1)
            title = title.replace('| 豆包', '').replace('豆包 - ', '').strip()
            return title
        return "无标题"
    
    def parse_conversations(self, lines):
        """智能解析对话内容"""
        conversations = []
        current_role = None
        current_content = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
            
            new_role = self.detect_role(line, i, lines)
            
            if new_role:
                if current_role and current_content:
                    conversations.append((current_role, '\n'.join(current_content)))
                
                current_role = new_role
                current_content = [line]
                i += 1
            else:
                if current_role:
                    current_content.append(line)
                i += 1
        
        if current_role and current_content:
            conversations.append((current_role, '\n'.join(current_content)))
        
        return self.merge_short_messages(conversations)
    
    def detect_role(self, line, index, lines):
        """智能检测角色"""
        line_lower = line.lower()
        
        for indicator in self.user_indicators:
            if line.startswith(indicator) or (indicator in line_lower[:15] and (line.endswith('？') or line.endswith('?'))):
                return 'user'
        
        for indicator in self.assistant_indicators:
            if line.startswith(indicator):
                return 'assistant'
        
        if line.endswith('？') or line.endswith('?'):
            if index > 0:
                prev_line = lines[index-1].strip() if index > 0 else ''
                if prev_line and not prev_line.endswith('？') and not prev_line.endswith('?'):
                    return 'user'
        
        return None
    
    def merge_short_messages(self, conversations):
        """合并短消息"""
        merged = []
        
        for role, content in conversations:
            content = content.strip()
            
            if not content:
                continue
            
            if merged and merged[-1][0] == role:
                merged[-1] = (role, merged[-1][1] + '\n\n' + content)
            else:
                merged.append((role, content))
        
        return merged
    
    def parse_file(self, file_path):
        """解析单个HTML文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            title = self.extract_title(content)
            clean_content = self.clean_html(content)
            lines = [line.strip() for line in clean_content.split('\n') if line.strip()]
            lines = [line for line in lines if not self.is_noise(line)]
            
            conversations = self.parse_conversations(lines)
            
            if not conversations:
                conversations = self.parse_by_qa_pattern(lines)
            
            return {
                'title': title,
                'file_name': os.path.basename(file_path),
                'conversations': conversations
            }
        
        except Exception as e:
            print(f"解析 {file_path} 失败: {e}")
            return None
    
    def parse_by_qa_pattern(self, lines):
        """备用：通过问答模式解析"""
        conversations = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.endswith('？') or line.endswith('?'):
                user_content = line
                
                i += 1
                assistant_content = []
                
                while i < len(lines):
                    next_line = lines[i]
                    
                    if next_line.endswith('？') or next_line.endswith('?'):
                        break
                    
                    if self.is_noise(next_line):
                        i += 1
                        continue
                    
                    assistant_content.append(next_line)
                    i += 1
                
                if assistant_content:
                    conversations.append(('user', user_content))
                    conversations.append(('assistant', '\n'.join(assistant_content)))
                else:
                    i += 1
            else:
                i += 1
        
        return conversations
    
    def convert_to_markdown(self, chat_data):
        """转换为Markdown格式"""
        title = chat_data['title'].replace('#', '').replace('*', '').replace('|', '-')
        md_content = f"# {title}\n\n"
        md_content += f"来源文件: {chat_data['file_name']}\n\n"
        
        for role, content in chat_data['conversations']:
            if role == 'user':
                md_content += f"**👤 我:**\n{content}\n\n"
            elif role == 'assistant':
                md_content += f"**🤖 豆包:**\n{content}\n\n"
        
        return md_content
    
    def batch_parse(self, html_dir):
        """批量解析HTML文件"""
        if not os.path.exists(html_dir):
            print(f"错误: 目录不存在 {html_dir}")
            return []
        
        html_files = sorted([f for f in os.listdir(html_dir) if f.endswith('.html') or f.endswith('.htm')])
        print(f"找到 {len(html_files)} 个HTML文件")
        
        all_chats = []
        for file_name in html_files:
            file_path = os.path.join(html_dir, file_name)
            print(f"正在处理: {file_name}")
            chat_data = self.parse_file(file_path)
            if chat_data and chat_data['conversations']:
                all_chats.append(chat_data)
        
        return all_chats

def main():
    parser = ImprovedDoubaoParser()
    
    save_dir = "./doubao_improved_export"
    os.makedirs(save_dir, exist_ok=True)
    
    all_chats = []
    
    single_file = 'h:/github/md/用逻辑分析拆解复杂问题的方法 - 豆包.html'
    if os.path.exists(single_file):
        print(f"\n📥 正在解析单个文件: {single_file}")
        chat_data = parser.parse_file(single_file)
        if chat_data:
            md_content = parser.convert_to_markdown(chat_data)
            filename = os.path.basename(single_file).replace('.html', '.md')
            filepath = os.path.join(save_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_content)
            all_chats.append({"title": chat_data['title'], "file": filename, "messages": len(chat_data['conversations'])})
            print(f"✅ 已保存: {filename}")
    
    html_dir = 'h:/github/md/html'
    if os.path.exists(html_dir):
        print(f"\n📥 正在批量解析目录: {html_dir}")
        dir_chats = parser.batch_parse(html_dir)
        
        for chat_data in dir_chats:
            md_content = parser.convert_to_markdown(chat_data)
            filename = f"{chat_data['file_name'][:-4]}.md"
            filepath = os.path.join(save_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(md_content)
            all_chats.append({"title": chat_data['title'], "file": filename, "messages": len(chat_data['conversations'])})
    
    summary = f"# 豆包聊天记录汇总\n\n"
    summary += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    summary += f"会话数量: {len(all_chats)}\n\n"
    
    for chat in all_chats:
        summary += f"- [{chat['title']}]({chat['file']}) - {chat['messages']} 条消息\n"
    
    with open(os.path.join(save_dir, "汇总.md"), "w", encoding="utf-8") as f:
        f.write(summary)
    
    print(f"\n🎉 导出完成！共保存 {len(all_chats)} 个会话")
    print(f"📁 保存目录: {os.path.abspath(save_dir)}")

if __name__ == "__main__":
    main()