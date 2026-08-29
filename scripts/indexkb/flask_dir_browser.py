#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Local Directory Browser with Rich Text Rendering
"""

import os
import re
from pathlib import Path
from flask import Flask, render_template, abort, send_file, request
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.fenced_code import FencedCodeExtension
from markdown.extensions.tables import TableExtension
from markdown.extensions.toc import TocExtension
from datetime import datetime
from urllib.parse import quote

app = Flask(__name__)

# Add custom Jinja2 filters
@app.template_filter('date')
def format_date(timestamp):
    """Format Unix timestamp to readable date"""
    if not timestamp:
        return ''
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime('%Y-%m-%d %H:%M')

# Configuration
DEFAULT_ROOT = Path(__file__).parent.resolve()
ALLOWED_EXTENSIONS = {
    '.md', '.txt', '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml',
    '.sh', '.bat', '.ps1', '.sql', '.xml', '.toml', '.ini', '.cfg', '.conf',
    '.c', '.cpp', '.h', '.hpp', '.go', '.rs', '.java', '.kt', '.scala',
    '.rb', '.php', '.swift', '.m', '.mm', '.cs', '.vue', '.tsx', '.jsx'
}
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'}

_file_tree_cache = None


def get_file_tree():
    """Get cached file tree, build if not cached"""
    global _file_tree_cache
    if _file_tree_cache is None:
        _file_tree_cache = build_file_tree(DEFAULT_ROOT)
    return _file_tree_cache


def is_text_file(filepath):
    """Check if file is a readable text file"""
    ext = Path(filepath).suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    if ext in ALLOWED_EXTENSIONS:
        return 'text'
    # Try to detect if it's a text file
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(512)
        # Check for null bytes (binary file indicator)
        if b'\x00' in chunk:
            return None
        # Try to decode as UTF-8
        chunk.decode('utf-8')
        return 'text'
    except:
        return None


def format_file_size(size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def get_directory_contents(path, root_path):
    """Get directory contents with metadata"""
    items = []
    path = Path(path)
    root_path = Path(root_path)

    try:
        for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            try:
                stat = item.stat()
                items.append({
                    'name': item.name,
                    'path': str(item.relative_to(root_path)),
                    'is_dir': item.is_dir(),
                    'size': format_file_size(stat.st_size) if item.is_file() else None,
                    'modified': stat.st_mtime,
                    'ext': item.suffix.lower()
                })
            except PermissionError:
                continue
    except PermissionError:
        pass

    return items


def read_file_content(filepath):
    """Read and preprocess file content"""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    return content


def build_file_tree(root_path, current_path='', depth=0, max_depth=1, max_items_per_dir=50):
    """Build a shallow file tree structure for fast navigation"""
    if depth > max_depth:
        return []
    
    root = Path(root_path)
    current = root / current_path if current_path else root
    
    try:
        items = []
        files = []
        dirs = []
        
        for item in current.iterdir():
            if item.is_dir():
                dirs.append(item)
            else:
                ext = item.suffix.lower()
                if ext in ALLOWED_EXTENSIONS or ext in IMAGE_EXTENSIONS:
                    files.append(item)
        
        dirs.sort(key=lambda x: x.name.lower())
        files.sort(key=lambda x: x.name.lower())
        
        for item in dirs:
            rel_path = str(item.relative_to(root))
            children = build_file_tree(root_path, rel_path, depth + 1, max_depth, max_items_per_dir) if depth < max_depth else []
            items.append({
                'name': item.name,
                'path': rel_path,
                'is_dir': True,
                'children': children,
                'has_content': len(children) > 0
            })
        
        item_count = 0
        for item in files:
            if item_count >= max_items_per_dir:
                items.append({
                    'name': f'...  还有更多 ({max_items_per_dir}+ items)',
                    'is_dir': False,
                    'is_truncated': True,
                    'children': []
                })
                break
            rel_path = str(item.relative_to(root))
            items.append({
                'name': item.name,
                'path': rel_path,
                'is_dir': False,
                'children': [],
                'ext': item.suffix.lower()
            })
            item_count += 1
    except PermissionError:
        return []
    
    return items


def extract_toc(content):
    """Extract table of contents from markdown content"""
    toc = []
    for line in content.split('\n'):
        if line.startswith('#') and line.count('#') <= 4:
            level = len(line) - len(line.lstrip('#'))
            title = line.lstrip('#').strip()
            anchor = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]+', '-', title).lower()
            toc.append({'level': level, 'title': title, 'anchor': anchor})
    return toc


def render_markdown(content):
    """Render markdown with extensions and Mermaid support"""
    mermaid_pattern = r'```mermaid\n([\s\S]*?)```'
    
    def replace_mermaid(match):
        mermaid_content = match.group(1)
        return f'<div class="mermaid">{mermaid_content}</div>'
    
    content = re.sub(mermaid_pattern, replace_mermaid, content)
    
    md = markdown.Markdown(extensions=[
        'fenced_code',
        'tables',
        'toc',
        CodeHiliteExtension(css_class='highlight', guess_lang=False),
        'nl2br',
        'sane_lists',
    ])
    return md.convert(content)


def highlight_code(content, language=''):
    """Simple code highlighting for non-markdown files"""
    from pygments import highlight
    from pygments.lexers import get_lexer_by_name, TextLexer, guess_lexer
    from pygments.formatters import HtmlFormatter

    if not language:
        language = 'text'

    try:
        if language in ('md', 'markdown'):
            return render_markdown(content)
        lexer = get_lexer_by_name(language)
    except:
        lexer = guess_lexer(content) if content else TextLexer()

    formatter = HtmlFormatter(cssclass='highlight', nowrap=True)
    return f'<pre class="highlight"><code>{highlight(content, lexer, formatter)}</code></pre>'


@app.route('/')
def index():
    """Home page - browse from root directory"""
    return browse('')


@app.route('/browse')
@app.route('/browse/<path:subpath>')
def browse(subpath=''):
    """Browse directory contents"""
    path = subpath
    if not path:
        current_path = DEFAULT_ROOT
    else:
        current_path = DEFAULT_ROOT / path

    current_path = current_path.resolve()

    # Security check - ensure path is within root
    if not str(current_path).startswith(str(DEFAULT_ROOT.resolve())):
        abort(403)

    if not current_path.exists():
        abort(404)

    if current_path.is_file():
        return view_file(path)

    items = get_directory_contents(current_path, DEFAULT_ROOT)

    # Build breadcrumb
    breadcrumbs = []
    if path:
        parts = path.split('/')
        cumulative = ''
        for part in parts:
            cumulative = cumulative + part if not cumulative else cumulative + '/' + part
            breadcrumbs.append({'name': part, 'path': cumulative})
        breadcrumbs[-1]['active'] = True

    parent_path = '/'.join(path.split('/')[:-1]) if '/' in path else ''

    return render_template('index.html',
                         items=items,
                         current_path=path,
                         parent_path=parent_path,
                         breadcrumbs=breadcrumbs,
                         root_name=DEFAULT_ROOT.name)


@app.route('/view')
@app.route('/view/<path:subpath>')
def view_file(subpath=''):
    """View individual file with rich text rendering"""
    path = subpath
    if not path:
        abort(400)

    filepath = DEFAULT_ROOT / path
    filepath = filepath.resolve()

    # Security check
    if not str(filepath).startswith(str(DEFAULT_ROOT.resolve())):
        abort(403)

    if not filepath.exists() or filepath.is_dir():
        abort(404)

    file_type = is_text_file(filepath)
    if not file_type:
        abort(415)

    ext = filepath.suffix.lower()
    content = read_file_content(filepath)

    # Build breadcrumbs
    breadcrumbs = []
    parts = path.split('/')
    cumulative = ''
    for part in parts[:-1]:
        cumulative = cumulative + part if not cumulative else cumulative + '/' + part
        breadcrumbs.append({'name': part, 'path': cumulative})
    breadcrumbs.append({'name': filepath.name, 'path': path, 'active': True})

    parent_path = '/'.join(path.split('/')[:-1]) if '/' in path else ''

    rendered_content = None
    toc = []
    if ext == '.md':
        toc = extract_toc(content)
        rendered_content = render_markdown(content)
    elif ext in ('.txt', '.text'):
        rendered_content = f'<pre class="plain-text">{content}</pre>'
    elif ext in ('.html', '.htm'):
        rendered_content = content
    else:
        rendered_content = highlight_code(content, ext.lstrip('.'))

    return render_template('view.html',
                         content=rendered_content,
                         filename=filepath.name,
                         breadcrumbs=breadcrumbs,
                         parent_path=parent_path,
                         is_markdown=(ext == '.md'),
                         toc=toc,
                         download_path=quote(path),
                         current_file_path=path)


@app.route('/raw')
@app.route('/raw/<path:subpath>')
def raw_file(subpath=''):
    """Serve raw file content"""
    path = subpath
    if not path:
        abort(400)

    filepath = DEFAULT_ROOT / path
    filepath = filepath.resolve()

    if not str(filepath).startswith(str(DEFAULT_ROOT.resolve())):
        abort(403)

    if not filepath.exists() or filepath.is_dir():
        abort(404)

    return send_file(filepath)


@app.route('/download/<path:subpath>')
def download_file(subpath=''):
    """Download file"""
    path = subpath
    if not path:
        abort(400)

    filepath = DEFAULT_ROOT / path
    filepath = filepath.resolve()

    if not str(filepath).startswith(str(DEFAULT_ROOT.resolve())):
        abort(403)

    if not filepath.exists() or filepath.is_dir():
        abort(404)

    return send_file(filepath, as_attachment=True)


@app.route('/api/file-tree')
def api_file_tree():
    """API endpoint to get file tree as JSON"""
    import json
    tree = get_file_tree()
    return json.dumps(tree, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
