#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doubao-import.py — 豆包分享链接导入器（确定性部分自动化）

职责（确定性工作，供大模型后处理）：
  1. 分层提取对话内容（HTML-SSR / HTML-CSR / API 三层策略）
  2. 完整性验证（消息数/字符数/关键词抽样）
  3. 生成元数据（标题/时间/消息数/slug）
  4. 生成报告骨架（统计+高频词+知识库关联检索建议，供大模型补深度洞察）
  5. 输出中间产物到指定目录（JSON + TXT + META + REPORT 骨架）

失败处理：
  - 任一提取层失败 → 逐层降级；全部失败 → exit code 2，SKILL.md 指引 fallback 人工流程
  - 验证未通过 → exit code 3（提示大模型人工补全或放弃）

用法:
  python3 scripts/tools/doubao-import.py --url "https://www.doubao.com/thread/xxx" [--out /tmp/doubao_out]
  python3 scripts/tools/doubao-import.py --share-id xxx [--out ...]

输出:
  <out>/<slug>.json     原始 API 数据（若有）
  <out>/<slug>.txt      提取的对话纯文本（含角色标记）
  <out>/<slug>.meta.json 元数据
  <out>/<slug>.report.md 报告骨架（统计/高频词/关联建议，深度洞察留待大模型）
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"


# ---------------------------------------------------------------- 工具函数

def log(msg):
    print(msg, file=sys.stderr)


def slugify(title: str, max_len: int = 80) -> str:
    """中文标题 → kebab-case slug（内置映射表 + 未映射单字拼音兜底）"""
    mapping = {
        # 语言学/字源
        "汉语": "chinese", "并列": "parallel", "复合词": "compound-words",
        "字源": "etymology", "解读": "interpretation", "汇总": "collection",
        "词汇": "vocabulary", "词汇总": "vocabulary", "古义": "archaic-meanings",
        "偏义": "partial-meaning", "联绵": "alliterative", "训诂": "exegesis",
        "说文": "shuowen", "字词": "words", "词义": "word-meanings",
        "词源": "word-origins", "汉字": "hanzi", "本义": "original-meaning",
        # 通用分析
        "深度": "deep", "分析": "analysis", "报告": "report",
        "对话": "conversation", "归档": "archive", "豆包": "doubao",
        "笔记": "notes", "总结": "summary", "方法": "method",
        "原理": "principles", "机制": "mechanism", "演进": "evolution",
        # 技术/服务器
        "服务器": "server", "存储": "storage", "内存": "memory",
        "大模型": "llm", "智能": "ai", "技术": "tech", "架构": "architecture",
        "互联": "interconnect", "芯片": "chip", "算力": "compute",
        "集群": "cluster", "训练": "training", "推理": "inference",
        # 人物/时间
        "复盘": "retrospective", "周报": "weekly", "月报": "monthly",
        "日报": "daily", "调研": "research", "追踪": "tracking",
    }
    words = []
    # 优先最长匹配（3字 → 2字 → 单字拼音兜底）
    i = 0
    while i < len(title):
        three = title[i:i + 3]
        two = title[i:i + 2]
        ch = title[i]
        if three in mapping:
            words.append(mapping[three])
            i += 3
        elif two in mapping:
            words.append(mapping[two])
            i += 2
        elif ch in mapping:
            words.append(mapping[ch])
            i += 1
        elif re.match(r'[\w\-]', ch):
            words.append(ch.lower())
            i += 1
        elif unicodedata.category(ch) == 'Lo':  # 未映射中文 → 拼音兜底
            words.append(_pinyin_simple(ch))
            i += 1
        else:
            i += 1
    slug = re.sub(r'-+', '-', '-'.join(words)).strip('-')
    if not slug:
        slug = "doubao-conversation"
    return slug[:max_len]


_PINYIN_MAP = {}


def _pinyin_simple(ch: str) -> str:
    """极简拼音兜底：仅覆盖常见字，未覆盖返回 'zi'（脚本侧 slug 不要求精确）"""
    table = {
        '并': 'bing', '列': 'lie', '复': 'fu', '合': 'he', '词': 'ci', '总': 'zong',
        '古': 'gu', '义': 'yi', '解': 'jie', '读': 'du', '字': 'zi',
        '的': 'de', '与': 'yu', '和': 'he', '之': 'zhi', '及': 'ji',
        '中': 'zhong', '国': 'guo', '人': 'ren', '年': 'nian', '月': 'yue',
        '日': 'ri', '新': 'xin', '问': 'wen', '题': 'ti', '论': 'lun',
        '文': 'wen', '史': 'shi', '学': 'xue', '研': 'yan', '究': 'jiu',
        '数': 'shu', '据': 'ju', '库': 'ku', '系': 'xi', '统': 'tong',
        '工': 'gong', '程': 'cheng', '设': 'she', '计': 'ji', '开': 'kai',
        '发': 'fa', '用': 'yong', '户': 'hu', '应': 'ying', '网': 'wang',
        '络': 'luo', '安': 'an', '全': 'quan', '密': 'mi', '钥': 'yue',
        '硬': 'ying', '件': 'jian', '软': 'ruan', '云': 'yun', '端': 'duan',
        '训': 'xun', '练': 'lian', '集': 'ji', '群': 'qun', '优': 'you',
        '服': 'fu', '务': 'wu', '器': 'qi', '模': 'mo', '推': 'tui',
        '理': 'li', '化': 'hua', '学': 'xue', '术': 'shu', '领': 'ling',
        '域': 'yu', '研': 'yan', '究': 'jiu', '行': 'xing', '走': 'zou',
        '居': 'ju', '宿': 'su', '疾': 'ji', '病': 'bing', '闻': 'wen',
        '听': 'ting', '饥': 'ji', '渴': 'ke', '朋': 'peng', '友': 'you',
        '道': 'dao', '路': 'lu', '财': 'cai', '宝': 'bao', '年': 'nian',
        '岁': 'sui', '时': 'shi', '刻': 'ke', '饮': 'yin', '食': 'shi',
        '学': 'xue', '习': 'xi', '应': 'ying', '程': 'cheng', '环': 'huan',
        '境': 'jing', '管': 'guan', '测': 'ce', '试': 'shi', '调': 'tiao',
        '与': 'yu', '和': 'he', '优': 'you', '化': 'hua', '对': 'dui',
        '照': 'zhao', '表': 'biao', '评': 'ping', '估': 'gu', '方': 'fang',
        '案': 'an', '规': 'gui', '划': 'hua', '战': 'zhan', '略': 'lue',
        '复': 'fu', '临': 'lin', '时': 'shi', '暂': 'zan', '长': 'chang',
        '久': 'jiu', '移': 'yi', '动': 'dong', '迁': 'qian', '生': 'sheng',
        '态': 'tai', '效': 'xiao', '率': 'lv', '能': 'neng', '力': 'li',
    }
    return table.get(ch, 'zi')


# ---------------------------------------------------------------- 提取层

def fetch_html(share_id: str, session=None) -> str:
    """第0层：获取 HTML（带 ttwid cookie）"""
    import requests
    if session is None:
        session = requests.Session()
        session.headers.update({"User-Agent": UA})
    url = f"https://www.doubao.com/thread/{share_id}"
    r = session.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def extract_from_html(html: str, session=None, share_id: str = "") -> dict:
    """第1层：HTML 提取（SSR post-body / CSR 混合文本）"""
    result = {"method": "html", "messages": [], "title": ""}

    # 判断 SSR post-body 数据（data-fn-args 流式渲染）
    body_end = html.find('</body>')
    post_body = html[body_end + 7:] if body_end > 0 else ''
    args = re.findall(r'data-fn-args="([^"]+)"', post_body)
    if args:
        total = sum(len(a) for a in args)
        log(f"  [HTML-SSR] post-body 流式数据 {total} bytes")
        texts = []
        for a in args:
            try:
                decoded = json.loads(a.replace('&quot;', '"').replace('\\u0026', '&'))
                texts.append(json.dumps(decoded, ensure_ascii=False))
            except Exception:
                texts.append(a)
        result["messages"] = [{"user_type": 2, "content": json.dumps({"text": t}, ensure_ascii=False)} for t in texts]
        return result

    # 通用混合文本提取（中文+拉丁+数字+数学符号）
    # 注意：使用双引号 raw string（单引号版本会因 \' 提前终止字符串）
    text_re = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\w\d\\$^{}_+=*/\-()\[\]<>|~@#%&!?:;'\"\.,]{30,}")
    texts = text_re.findall(html)
    seen = set()
    chunks = []
    for t in sorted(texts, key=len, reverse=True):
        clean = t.strip()
        if len(clean) > 30 and clean not in seen and not re.match(r'^[\s<>&#;/\x5c]+$', clean):
            seen.add(clean)
            chunks.append(clean)
    if chunks:
        log(f"  [HTML-CSR] 混合提取 {len(chunks)} chunks")
        result["messages"] = [{"user_type": 2, "content": json.dumps({"text": "\n\n".join(chunks)}, ensure_ascii=False)}]
        return result

    return result


def extract_from_api(share_id: str, session=None) -> dict:
    """第2层：API 提取（x 前缀 → im/message/share/get；其他 → samantha/thread/share/snapshot/get）"""
    import requests
    if session is None:
        session = requests.Session()
        session.headers.update({
            "User-Agent": UA,
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.doubao.com",
            "Referer": f"https://www.doubao.com/thread/{share_id}",
        })
        # 先 GET landing page 获取 ttwid
        session.get(f"https://www.doubao.com/thread/{share_id}", timeout=30)

    if share_id.startswith("x"):
        api_url = "https://www.doubao.com/im/message/share/get"
        payload = {"share_id": share_id, "need_bot_info": True}
    else:
        api_url = "https://www.doubao.com/samantha/thread/share/snapshot/get"
        payload = {"share_id": share_id, "need_bot_info": False}

    resp = session.post(api_url, json=payload, timeout=60)
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"API 失败: code={data.get('code')}, msg={data.get('msg')}")

    d = data.get("data", {})
    share_info = d.get("share_info", {})
    msg_list = d.get("message_snapshot", {}).get("message_list", [])
    result = {
        "method": "api",
        "title": share_info.get("share_name", ""),
        "share_time": share_info.get("share_time", ""),
        "user": share_info.get("user", {}).get("nick_name", ""),
        "bot": share_info.get("bot", {}).get("name", ""),
        "raw_json": data,
        "messages": msg_list,
    }
    log(f"  [API] 成功: {len(msg_list)} 条消息")
    return result


# ---------------------------------------------------------------- 解析/验证

def messages_to_text(messages: list) -> str:
    """消息列表 → 对话纯文本"""
    lines = []
    for i, msg in enumerate(messages, 1):
        utype = msg.get("user_type")
        role = "👤 用户" if utype == 1 else "🤖 豆包"
        try:
            content = json.loads(msg.get("content", "{}"))
            text = content.get("text", "")
        except Exception:
            text = msg.get("content", "")
        if not text:
            text = msg.get("tts_content", "")
        thinking = msg.get("thinking_content", "")
        lines.append(f"[{i}] {role}:\n{text}\n")
        if thinking and len(thinking) > 50:
            lines.append(f"  💭 [深度思考]: {thinking[:2000]}\n")
    return "\n".join(lines)


def verify(text: str, messages: list, expect_keywords: list = None) -> dict:
    """完整性验证：字符数 + 消息数 + 关键词抽样"""
    n_msg = len(messages)
    n_chars = len(text)
    checks = {
        "messages": n_msg,
        "chars": n_chars,
        "pass": True,
        "warnings": [],
    }
    if n_msg == 0:
        checks["pass"] = False
        checks["warnings"].append("0 条消息")
    if n_msg > 0 and n_chars < 100:
        checks["pass"] = False
        checks["warnings"].append(f"字符过少 ({n_chars})")
    if expect_keywords:
        missing = [k for k in expect_keywords if k not in text]
        if missing:
            checks["warnings"].append(f"关键词缺失: {missing}")
            checks["pass"] = False
    return checks


def top_terms(text: str, n: int = 15) -> list:
    """高频词提取（简单启发式：2-4字词频）"""
    import collections
    # 提取中文字符串
    cn_terms = re.findall(r'[\u4e00-\u9fff]{2,4}', text)
    stop = {"这个", "一个", "什么", "没有", "就是", "可以", "我们", "他们", "因为",
            "所以", "但是", "如果", "已经", "现在", "还是", "这样", "怎么", "不是",
            "一下", "一种", "两个", "之后", "时候", "那个", "自己", "这里", "对于"}
    cnt = collections.Counter(t for t in cn_terms if t not in stop)
    return [w for w, _ in cnt.most_common(n)]


def kb_association(text: str) -> list:
    """知识库关联检索建议：扫描知识库索引，找与主题相关的已有文档关键词"""
    idx_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "knowledge", "index.md")
    if not os.path.exists(idx_path):
        return []
    with open(idx_path, encoding="utf-8") as f:
        idx = f.read()
    # 用高频词在 index 中粗查
    hits = []
    for term in top_terms(text, 30):
        if term in idx:
            # 找到包含该词的 index 行
            for line in idx.split("\n"):
                if term in line and ("|" in line):
                    hits.append((term, line.strip()[:120]))
                    break
    return hits[:8]


# ---------------------------------------------------------------- 主流程

def main():
    p = argparse.ArgumentParser(description="豆包分享链接导入器（确定性部分）")
    p.add_argument("--url", help="豆包分享 URL")
    p.add_argument("--share-id", help="share_id（与 --url 二选一）")
    p.add_argument("--out", default="/tmp/doubao_out", help="输出目录（默认 /tmp/doubao_out）")
    p.add_argument("--keywords", default="", help="期望关键词（逗号分隔），用于完整性验证")
    p.add_argument("--json-only", action="store_true", help="仅输出提取结果 JSON，不生成报告骨架")
    args = p.parse_args()

    share_id = args.share_id or ""
    if not share_id and args.url:
        m = re.search(r'/thread/([A-Za-z0-9]+)', args.url)
        share_id = m.group(1) if m else args.url.strip().rstrip('/').split('/')[-1]
    if not share_id:
        print("❌ 需要 --url 或 --share-id")
        sys.exit(1)

    log(f"🔗 share_id: {share_id} | 前缀: {share_id[:1]}")

    os.makedirs(args.out, exist_ok=True)
    result = None

    # 提取策略：
    #   x 前缀 → 已知为 CSR/SPA 壳，优先 API（SKILL.md 验证结论）
    #   其他前缀 → 先 HTML（SSR 可直提），失败/质量差再 API
    is_x = share_id.startswith("x")

    # 第1层：HTML 提取（仅非 x 前缀或 x 前缀先探测）
    try:
        log("[1/3] 尝试 HTML 提取...")
        html = fetch_html(share_id)
        log(f"  HTML 大小: {len(html)} bytes")
        if len(html) < 20000 and "shareInfo" in html and "{}" in html:
            log("  → SPA 壳，跳过 HTML 提取")
        else:
            r1 = extract_from_html(html)
            # 质量检查：HTML 整页提取常把页面当 1 块大文本（无标题/消息数=1）
            if r1["messages"] and not (is_x and (not r1.get("title") or len(r1["messages"]) <= 1)):
                result = r1
            elif is_x:
                log("  → x 前缀 HTML 结果质量差（整页文本），回退 API")
    except Exception as e:
        log(f"  ⚠️ HTML 提取失败: {e}")

    # 第2层：API 提取
    if result is None:
        try:
            log("[2/3] 尝试 API 提取...")
            result = extract_from_api(share_id)
        except Exception as e:
            log(f"  ⚠️ API 提取失败: {e}")

    # 全部失败
    if result is None or not result.get("messages"):
        print("❌ 全部提取层失败")
        print("→ 按 skills/doubao-share/SKILL.md fallback 流程：人工（大模型）逐步处理")
        sys.exit(2)

    # 生成 slug 与文本
    title = result.get("title", "豆包对话")
    slug = slugify(title)
    text = messages_to_text(result["messages"])

    # 写入中间产物
    base = os.path.join(args.out, slug)
    with open(base + ".txt", "w", encoding="utf-8") as f:
        f.write(text)
    if result.get("raw_json"):
        with open(base + ".json", "w", encoding="utf-8") as f:
            json.dump(result["raw_json"], f, ensure_ascii=False)

    # 验证
    kw = [k.strip() for k in args.keywords.split(",") if k.strip()] if args.keywords else None
    v = verify(text, result["messages"], kw)
    print(f"✅ 提取成功 | 方法: {result.get('method')} | 消息: {v['messages']} | 字符: {v['chars']}")
    print(f"📄 标题: {title}")
    print(f"🔤 slug: {slug}")
    for w in v["warnings"]:
        print(f"⚠️ 验证警告: {w}")

    meta = {
        "share_id": share_id,
        "title": title,
        "slug": slug,
        "method": result.get("method"),
        "share_time": result.get("share_time", ""),
        "user": result.get("user", ""),
        "bot": result.get("bot", ""),
        "verify": v,
        "outputs": {
            "txt": base + ".txt",
            "json": base + ".json" if result.get("raw_json") else None,
        },
    }
    with open(base + ".meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    # 报告骨架（供大模型补深度洞察）
    if not args.json_only:
        terms = top_terms(text)
        assoc = kb_association(text)
        share_ts = ""
        if result.get("share_time"):
            try:
                share_ts = datetime.fromtimestamp(int(result["share_time"]) / 1000).strftime("%Y-%m-%d %H:%M")
            except Exception:
                pass
        report = f"""# {title} — 深度分析报告（骨架）

> **来源**: 豆包对话分享（share_id: `{share_id}`） · {share_ts or '日期未知'}
> **提取**: doubao-import.py（方法: {result.get('method')}） · {v['messages']} 条消息 / {v['chars']} 字符
> **⚠️ 本骨架由脚本生成，深度洞察需大模型填充**：核心命题 / 关键洞察 / 补齐知识点 / 结论

## 数据概览（脚本自动统计）

| 维度 | 值 |
|:-----|:---|
| 消息数 | {v['messages']} |
| 总字符 | {v['chars']} |
| 提取方法 | {result.get('method')} |
| 对话者 | {result.get('user', '-')} → {result.get('bot', '-')} |

## 高频主题词（脚本提取，供参考）

{', '.join(terms) if terms else '-（无法提取）'}

## 知识库关联建议（脚本粗查，供大模型确认）

{"\n".join(f"- `{t}` → {line}" for t, line in assoc) if assoc else "-（无强关联）"}

---

## 一、核心命题（待大模型填充）

> 1-2 句话概括对话核心论点

## 二、关键洞察（待大模型填充）

1. **洞察1** — 说明
2. **洞察2** — 说明

## 三、补齐知识点（待大模型填充）

- 概念/方法/框架延伸

## 四、结论与可复用价值（待大模型填充）

- 对知识库的沉淀价值、后续可扩展方向

---

## 完整对话原文

见同目录 `{slug}.txt`。
"""
        with open(base + ".report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print(f"📋 报告骨架: {base}.report.md")

    if not v["pass"]:
        print("⚠️ 验证未通过，建议人工检查或按 SKILL.md 处理")
        sys.exit(3)
    sys.exit(0)


if __name__ == "__main__":
    main()
