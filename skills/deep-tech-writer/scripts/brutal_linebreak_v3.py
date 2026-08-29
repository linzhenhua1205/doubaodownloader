# -*- coding: utf-8 -*-
"""
暴力拆行 v3：针对95个仍有"标题正文挤同行"的文件做终极拆行
核心策略：任何 # 行只要 >80字，或包含"结束符+空格+后句"特征，必切
"""
import os, re, json, random
from pathlib import Path

ROOT = r"h:\github\cowkb\discover\newwiki2"
DIRS = ["AI-Agent", "AI-模型架构", "AI-训练微调", "ai-models"]
BOM = "\ufeff"

# 中文/英文标题结束符
TITLE_ENDERS = ["？", "?", "！", "!", "：", ":", "。", ".", "】", "」", "）", ")", "》", ">"]

def read_md(p):
    with open(p, "r", encoding="utf-8-sig") as f: return f.read()
def write_md(p, t):
    if not t.startswith(BOM): t = BOM + t
    with open(p, "w", encoding="utf-8") as f: f.write(t)
def split_front(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0: return text[3:end].strip(), text[end+4:].lstrip("\n")
    return "", text

# ---------- 核心：暴力拆行 ----------
def brutal_linebreak(text):
    lines = text.split("\n")
    out = []
    in_code = False
    for raw in lines:
        s = raw.strip()
        # 代码块保护
        if s.startswith("```"):
            in_code = not in_code
            out.append(raw)
            continue
        if in_code:
            out.append(raw)
            continue
        if not s:
            out.append(raw)
            continue
        
        m = re.match(r"^(#{1,6})\s+(.+?)\s*$", raw)
        if not m:
            out.append(raw)
            continue
        
        level = m.group(1)
        rest = m.group(2)
        
        # 快速路径：rest <= 80字 且 没特征 → 认为是正常标题
        if len(rest) <= 80:
            # 检查一个特征：rest 中出现 "空格 + 中文大写字母开头的新词 + 句子"
            # 例：什么是AI Agent？ AI Agent是一种能够...
            # 问号后有空格
            fast_ok = True
            for ender in TITLE_ENDERS:
                idx = rest.find(ender)
                if idx > 0 and idx < len(rest) - 2:
                    after = rest[idx+1:]
                    if after and after[0] in (" ", "\t"):
                        after = after.lstrip()
                        if len(after) >= 5:  # 后面确实有内容
                            fast_ok = False
                            break
            if fast_ok:
                out.append("%s %s" % (level, rest))
                continue
        
        # ---- 需要拆：寻找最佳切点 ----
        cut_pos = -1  # 切在 rest[cut_pos] 之后
        
        # 优先级A：找代码块起点 "```"
        idx = rest.find("```")
        if idx > 0 and cut_pos == -1:
            cut_pos = idx
        
        # 优先级B：找表格列 " | xxx | xxx |" （两个以上 |）
        if cut_pos == -1:
            pipe_count = 0
            first_pipe = -1
            for ci, ch in enumerate(rest):
                if ch == "|":
                    pipe_count += 1
                    if first_pipe == -1: first_pipe = ci
                    if pipe_count >= 2 and first_pipe > 5:
                        # 第一个 | 之前是标题
                        cut_pos = first_pipe
                        break
        
        # 优先级C：找标题结束符（TITLE_ENDERS）+ 后有内容
        if cut_pos == -1:
            best = -1
            for ender in TITLE_ENDERS:
                start = 0
                while True:
                    idx = rest.find(ender, start)
                    if idx == -1: break
                    # 检查这之后是不是"标题外"的内容
                    if idx + 1 < len(rest):
                        nxt = rest[idx+1]
                        # 结束符后面是空格、中文、英文大写 → 认为是正文开始
                        if nxt in (" ", "\t") or (nxt not in TITLE_ENDERS and nxt not in ("」", "）", "》", ".", "。")):
                            # 另外：不要切在 "v1.0" 这种小数点（后面是数字）
                            if ender == "." and idx+1 < len(rest) and rest[idx+1].isdigit():
                                start = idx + 1
                                continue
                            if idx > best: best = idx + 1  # 包含结束符
                    start = idx + 1
            if best > 0:
                cut_pos = best
        
        # 优先级D：找粗体子标题 **xxx**： 前面的位置
        if cut_pos == -1:
            bold = re.search(r"\*\*[^*]{2,20}\*\*[:：]", rest)
            if bold and bold.start() > 5:
                cut_pos = bold.start()
        
        # 优先级E：强制 80字 (找前80字中最后一个空格/标点)
        if cut_pos == -1 and len(rest) > 80:
            search_region = rest[40:90]
            # 找最后一个空格或标点
            last_break = -1
            for ci in range(min(len(rest)-1, 90), 40, -1):
                ch = rest[ci]
                if ch in (" ", "\t", "，", ",", "。", ".", "；", ";", "、"):
                    last_break = ci + 1
                    break
            if last_break > 0:
                cut_pos = last_break
            else:
                cut_pos = 80
        
        # 执行切
        if cut_pos > 0 and cut_pos < len(rest) - 2:
            title_part = rest[:cut_pos].rstrip()
            body_part = rest[cut_pos:].lstrip()
            if len(title_part) >= 1 and len(body_part) >= 2:
                out.append("%s %s" % (level, title_part))
                out.append("")
                out.append(body_part)
                continue
        
        # 切不了，原样输出
        out.append("%s %s" % (level, rest))
    
    return "\n".join(out)

# ---------- 目录重建（基于拆行后的版本）----------
def rebuild_toc(body_text):
    lines = body_text.split("\n")
    in_code = False
    h2s = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code: continue
        m2 = re.match(r"^##\s+(.+?)\s*$", ln)
        if m2: h2s.append(m2.group(1).strip())
    if not h2s: return body_text, False
    
    has_toc = any(re.match(r"^##\s*📑?\s*目录", l) for l in lines)
    if not has_toc: return body_text, False
    
    skip = {"📑 目录", "主题概述", "🔗 参考文件", "参考文件", "Changelog"}
    filtered = [h for h in h2s if h not in skip]
    
    def slugg(s):
        s = re.sub(r"[`*_#<>\[\]()]", "", s.strip())
        return re.sub(r"\s+", "", s)
    toc_lines = ["- [%s](#%s)" % (t, slugg(t)) for t in filtered]
    
    out = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        if re.match(r"^##\s*📑?\s*目录", ln):
            out.append(ln)
            out.append("")
            j = i + 1
            while j < n and not re.match(r"^##\s+[^#]", lines[j]): j += 1
            for tl in toc_lines: out.append(tl)
            if out[-1] != "": out.append("")
            i = j
        else:
            out.append(ln)
            i += 1
    return "\n".join(out), True

def ensure_tail(body_text):
    has_ref = bool(re.search(r"^##\s*🔗?\s*参考文件", body_text, re.M))
    has_cl = bool(re.search(r"^##\s*Changelog", body_text, re.M))
    if has_ref and has_cl: return body_text
    lines = body_text.rstrip().split("\n")
    new_lines = []
    for ln in lines:
        if re.match(r"^##\s*🔗?\s*参考文件", ln): continue
        if re.match(r"^##\s*Changelog", ln): continue
        new_lines.append(ln)
    while new_lines and not new_lines[-1].strip(): new_lines.pop()
    ref = ["", "## 🔗 参考文件", "", "| 文件 | 说明 |", "|:-----|:-----|",
           "| （待补充） | 相关知识文件与交叉引用见知识库 index.md |", ""]
    cl = ["## Changelog", "", "| 版本 | 日期 | 说明 |", "|:-----|:-----|:-----|",
          "| v1.0 | 2026-07-29 | 系统优化：头部概要+关键词、目录去重、模板清理、章节重组与标准化 |", ""]
    return "\n".join(new_lines + [""] + ref + cl) + "\n"

def process_file(path):
    raw = read_md(path)
    fm, body = split_front(raw)
    title = path.stem
    if fm:
        tm = re.search(r"^title:\s*(.+)$", fm, re.M)
        if tm: title = tm.group(1).strip().strip("\"'")
    
    # 暴力拆行 连做3次
    for _ in range(3):
        body = brutal_linebreak(body)
    
    body, toc = rebuild_toc(body)
    body = ensure_tail(body)
    
    if fm and not re.search(r"updated_at:", fm):
        fm = fm.rstrip() + "\nupdated_at: '2026-07-29'"
    if fm:
        final = "---\n%s\n---\n\n%s" % (fm.strip(), body.lstrip("\n"))
    else:
        final = body
    write_md(path, final)
    
    # 质量：检查坏标题
    aft = read_md(path)
    _, abody = split_front(aft)
    bad = 0
    in_code = False
    for ln in abody.split("\n"):
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code: continue
        mh = re.match(r"^#{1,6}\s+(.+)$", ln)
        if mh:
            t = mh.group(1).strip()
            if len(t) > 120: bad += 1
    s_len = 0
    sm = re.search(r">\s*\*\*概要\*\*[:：]\s*(.*?)(?:\n|$)", abody)
    if sm:
        s_len = len(re.sub(r"\[来源[:：].*?\]", "", sm.group(1)).strip())
    k_cnt = 0
    km = re.search(r">\s*\*\*关键词\*\*[:：]\s*(.*)", abody)
    if km:
        k_cnt = len([x.strip() for x in km.group(1).split("·") if x.strip()])
    return {"fn": path.name, "title": title, "bad": bad, "s_len": s_len, "k_cnt": k_cnt, "toc": toc}

def run():
    files = []
    for d in DIRS:
        p = Path(ROOT) / d
        if not p.exists(): continue
        for f in sorted(p.glob("*.md")):
            if f.name == "index.md": continue
            files.append(f)
    random.shuffle(files)
    n = len(files)
    BATCH = 20
    batches = [files[i:i+BATCH] for i in range(0, n, BATCH)]
    print("暴力拆行v3：终极分离标题+正文 (%d 文件，%d 批次)" % (n, len(batches)))
    all_d = []
    for bi, batch in enumerate(batches, 1):
        print("\n批次 %d/%d (%d文件)" % (bi, len(batches), len(batch)))
        for fi, f in enumerate(batch, 1):
            try:
                d = process_file(f)
                mb = "⚠️%d" % d["bad"] if d["bad"] > 0 else "  "
                ms = "✅" if 150 <= d["s_len"] <= 300 else "⚠️"
                mk = "✅" if 4 <= d["k_cnt"] <= 6 else "⚠️"
                mt = "📋" if d["toc"] else "  "
                print("  [%d/%d] %-40s 坏%s | 概%d%s %d词%s %s" % (
                    fi, len(batch), f.name[:40], mb, d["s_len"], ms, d["k_cnt"], mk, mt))
                all_d.append(d)
            except Exception as e:
                print("  [%d/%d] ❌ %s → %s" % (fi, len(batch), f.name, e))
                all_d.append({"fn": f.name, "error": str(e)})
    total = len(all_d)
    ok = sum(1 for x in all_d if "error" not in x)
    total_bad = sum(x.get("bad", 0) for x in all_d if "error" not in x)
    bad_files = sum(1 for x in all_d if x.get("bad", 0) > 0)
    gs = sum(1 for x in all_d if 150 <= x.get("s_len",0) <= 300)
    gk = sum(1 for x in all_d if 4 <= x.get("k_cnt",0) <= 6)
    tc = sum(1 for x in all_d if x.get("toc"))
    print("\n" + "="*60)
    print("完成：%d/%d 成功" % (ok, total))
    print("  概要150-300字： %d/%d (%.1f%%)" % (gs, total, gs/total*100 if total else 0))
    print("  关键词4-6个：  %d/%d (%.1f%%)" % (gk, total, gk/total*100 if total else 0))
    print("  目录正确：      %d 文件" % tc)
    print("  仍有坏标题：    %d 文件，合计 %d 个" % (bad_files, total_bad))
    rp = os.path.join(ROOT, "_brutal_linebreak_v3.json")
    with open(rp, "w", encoding="utf-8") as rf:
        json.dump({"time": __import__("datetime").datetime.now().isoformat(),
                   "total": total, "ok": ok, "bad_files": bad_files, "total_bad": total_bad,
                   "gs": gs, "gk": gk, "toc": tc, "details": all_d}, rf, ensure_ascii=False, indent=2)
    print("报告：", rp)

if __name__ == "__main__":
    run()
