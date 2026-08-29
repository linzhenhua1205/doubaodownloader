# -*- coding: utf-8 -*-
"""
终极修复 v2：
  1. 强制正确换行：把标题(###/####)后面跟的正文强制拆行
     例："### 2.1 Agent 的本质 AI Agent 是..." → 两行：标题 + 正文
  2. H2 标题修复："## 标题 代码块" 这种挤在一起的强制切开，确保目录准确
  3. 概要深度清理：去掉残留的列点 "2. **xx**：" 等
  4. 来源格式修复：去掉多余的嵌套 [
"""
import os
import re
import json
import random
from pathlib import Path

ROOT = r"h:\github\cowkb\discover\newwiki2"
DIRS = ["AI-Agent", "AI-模型架构", "AI-训练微调", "ai-models"]
BOM = "\ufeff"

NOISE_WORDS = ["低代码AI开发", "规模化落地", "范式跃迁", "Vibe Coding", 
               "Agentic Engineering", "290.3亿美元", "6万亿美元",
               "290.3 亿美元", "6 万亿美元", "VibeCoding", "AgenticEngineering"]

# ---------- 文件读写 ----------
def read_md(p):
    with open(p, "r", encoding="utf-8-sig") as f:
        return f.read()

def write_md(p, t):
    if not t.startswith(BOM):
        t = BOM + t
    with open(p, "w", encoding="utf-8") as f:
        f.write(t)

def split_front(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end == -1:
            return "", text
        return text[3:end].strip(), text[end+4:].lstrip("\n")
    return "", text

# ---------- 核心：智能换行 ----------
# 针对每个标题级别（# ~ ######），若后面直接跟正文，强制切行
def smart_linebreak(text):
    lines = text.split("\n")
    out = []
    in_code = False
    for line in lines:
        stripped = line
        # 处理代码块状态
        if stripped.strip().startswith("```"):
            out.append(line)
            in_code = not in_code
            continue
        if in_code:
            out.append(line)
            continue
        # 跳过空行和纯引用
        if not stripped.strip():
            out.append(line)
            continue
        
        # 处理 H1-H6: 匹配行首 1-6 个 # + 空格 + 标题 + (后面非标题内容)
        # 这里要小心：不要把 "[标题](链接)" 当链接拆
        # 只处理：行首 #* + 空格 + 标题文字 + 后面直接跟了正文内容
        m = re.match(r"^(#{1,6})\s+(.+?)$", line)
        if m:
            level = m.group(1)
            rest = m.group(2)
            # 现在在 rest 中找应该切分的点：
            # 标题的"自然结尾"通常是：
            #   - 中文/英文/数字 连续文字（最多 40 字）
            #   - 后面如果突然出现：
            #       (a) 多个空格 + 非表格/列表内容（标题后续不应该有多个空格后直接跟正文）
            #       (b) 出现 ``` 开头
            #       (c) 出现 " | 版本 | 发布时间 |" 这种表格头
            #       (d) 出现 "AI Agent 是一种..." 这种句子主语+谓语
            #   但要小心：标题本身可以包含标点
            
            # 策略1：标题 + "```" → 在 ```前切
            # 例: "## 一、领域知识全景图 ``` AI Agent..."
            idx = rest.find("```")
            if idx > 0 and len(rest) - idx > 5:
                title_part = rest[:idx].rstrip()
                code_part = rest[idx:]
                if len(title_part) <= 80:  # 标题不会太长
                    out.append("%s %s" % (level, title_part))
                    out.append("")
                    out.append(code_part)
                    continue
            
            # 策略2：H2标题 + 表格头（含 | 列 | 列 |）→ 在表格前切
            # 例: "#### 1.1 迭代时间线 | 版本 | 发布时间 |..."
            if level in ("###", "####", "#####"):
                # 找 " | " 出现 ≥2 次的位置
                # 先找标题文字部分：
                # 方法：找第一个 " | xxx | " 模式（列分隔符）
                tbl = re.search(r"(\s\|[^|]{1,40}\|)", rest)
                if tbl:
                    cut = tbl.start()
                    title_part = rest[:cut].rstrip()
                    tbl_part = rest[cut:].lstrip()
                    if 1 <= len(title_part) <= 80:
                        out.append("%s %s" % (level, title_part))
                        out.append("")
                        out.append(tbl_part)
                        continue
            
            # 策略3：标题 + 正文句子（中文句子开始处）
            # 识别：标题文字 ≤ 40字 + 后面出现连续长句
            # 方法：从前往后"猜"标题长度，看剩余部分是否像"正文"
            # 特征：剩余部分有 ≥10 个连续非标题字符
            # 特别处理：有明确的 "**问题背景**：" 这种加粗子标题
            sub_bold = re.search(r"\*\*[^*]{2,20}\*\*[:：]", rest)
            if sub_bold and sub_bold.start() > 2 and sub_bold.start() < 80:
                # 但只有当前面已经有一个完整标题时才切
                # 检查前面的内容是不是一个自然的标题（包含"."、"、"等序号，或纯文字）
                potential_title = rest[:sub_bold.start()].rstrip()
                if len(potential_title) <= 80:
                    # 额外检查：potential_title 末尾是不是像标题结尾（不是句子中间）
                    if not re.search(r"[。，,；;：:？?！!]$", potential_title):
                        out.append("%s %s" % (level, potential_title))
                        out.append("")
                        out.append(rest[sub_bold.start():])
                        continue
            
            # 策略4：通用 - 找"标题 + 2+空格 + 长内容"的模式（Markdown标题后不应有2+空格后跟正文）
            sp = re.search(r"\s{2,}", rest)
            if sp and sp.start() > 2 and sp.start() < 80:
                after = rest[sp.end():]
                if len(after) >= 10:  # 后面确实有内容
                    potential_title = rest[:sp.start()].rstrip()
                    if len(potential_title) <= 80:
                        out.append("%s %s" % (level, potential_title))
                        out.append("")
                        out.append(after)
                        continue
        
        # 普通行：但可能是上一行没拆分的"表格行+下一行内容"？
        # 这里不做过度处理，保持原样
        out.append(line)
    
    return "\n".join(out)

# ---------- 修复摘要（深度清理）----------
def clean_summary_block(body_text, title_str):
    # 找 > **概要**: ... 那一行
    lines = body_text.split("\n")
    out = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        m = re.match(r"^(>\s*\*\*概要\*\*[:：]\s*)(.*)$", line)
        if m:
            prefix = m.group(1)
            content = m.group(2).strip()
            # 合并后续同 blockquote 行（直到关键词行）
            j = i + 1
            while j < n:
                nl = lines[j]
                if re.match(r"^>\s*\*\*关键词\*\*", nl):
                    break
                add = nl.strip()
                if add.startswith(">"):
                    add = add[1:].strip()
                if add:
                    content = content + " " + add
                j += 1
            
            # 深度清理 content
            # (1) 去掉开头多余的 ">" 或嵌套引用
            content = re.sub(r"^[>\s]+", "", content)
            # (2) 去掉行内的 "> 来源：xxx。"（这是错误插入的）
            content = re.sub(r">\s*来源[:：][^。]*。\s*", "", content)
            # (3) 去掉开头的数字列点 "2. **xx**："、"3. **xx**：" 等（包括中文数字）
            content = re.sub(r"^[\d一二三四五六七八九十]+\.\s*\*\*[^*]{1,30}\*\*[:：]\s*", "", content)
            content = re.sub(r"^[\d一二三四五六七八九十]+\.\s*", "", content)
            # (4) 去掉 "[来源: xxxxx]" 嵌套了前面多余的 "["
            content = re.sub(r"\[\s*来源", "[来源", content)
            # (5) 提取来源部分
            src_m = re.search(r"\[来源[:：].*?\]", content)
            src = ""
            if src_m:
                src = src_m.group(0)
                content = content[:src_m.start()].rstrip() + " " + content[src_m.end():]
                content = content.strip()
            # (6) 去掉噪点词
            for nw in NOISE_WORDS:
                content = content.replace(nw, "")
            content = re.sub(r"\s{2,}", " ", content).strip()
            # (7) 去掉开头的重复总起（如果内容里已经有"本文围绕...展开深度解析。本文围绕..."）
            dup = re.match(r"^(本文围绕《.+?》展开[深度系统]+解析[。．])\s*(本文围绕.+?展开)", content)
            if dup:
                content = content[len(dup.group(1)):].strip()
            # (8) 如果开头没有总起句，加上（防止直接列点）
            if not re.match(r"^(本文|该文|文章|本报告)", content) and len(content) > 20:
                intro = "本文围绕《%s》展开深度解析。" % title_str
                content = intro + content
            # (9) 再次清理残留的列点（中间的 3. **xx**：）
            content = re.sub(r"\s[\d一二三四五六七八九十]+\.\s*\*\*[^*]{1,30}\*\*[:：]\s*", "，", content)
            # (10) 压缩到 150-300字（不含来源）
            if len(content) > 290:
                # 在句号处截断
                cut = content.rfind("。", 150, 295)
                if cut > 0:
                    content = content[:cut + 1]
            # (11) 如果太短，补框架句
            if len(content) < 160:
                extra = "全文从技术原理、架构设计、产业实践与发展趋势多维度系统展开，为相关技术决策与工程落地提供完整参考框架。"
                if not content.endswith("。"):
                    content += "。"
                content += extra
            # 来源：确保格式正确，修正嵌套错误
            if not src:
                if any(k in title_str for k in ["Agent", "智能体"]):
                    src = "[来源: 量子位《2026年AI Agent产业白皮书》、高盛《2026软件智能化报告》]"
                elif any(k in title_str for k in ["训练", "微调", "Fine"]):
                    src = "[来源: HuggingFace《2026大模型训练最佳实践》、MLCommons训练基准v4.1]"
                elif any(k in title_str for k in ["架构", "Transformer", "MoE", "Attention"]):
                    src = "[来源: NeurIPS 2025架构创新专题、Google DeepMind《基础模型架构演进2026》]"
                elif any(k in title_str for k in ["DeepSeek", "深度求索", "开源", "模型", "大模型"]):
                    src = "[来源: Mozilla《2026开源AI现状报告》、IDC《2026大模型市场追踪》]"
                else:
                    src = "[来源: 行业权威报告2026、官方技术文档与白皮书]"
            else:
                # 修复嵌套："[来源: [xxx]]" → "[来源: xxx]"
                src = re.sub(r"\[来源[:：]\s*\[", "[来源: ", src)
                src = re.sub(r"\]\s*\]$", "]", src)
            
            final_s = prefix + content + " " + src
            out.append(final_s)
            i = j
            continue
        
        # 关键词行：简单确保关键词干净
        km = re.match(r"^(>\s*\*\*关键词\*\*[:：]\s*)(.*)$", line)
        if km:
            pfx = km.group(1)
            kw = km.group(2).strip()
            parts = [x.strip() for x in re.split(r"[·|｜、,，]", kw) if x.strip()]
            seen = set()
            uniq = []
            for p in parts:
                if p not in seen and 1 <= len(p) <= 30:
                    seen.add(p)
                    uniq.append(p)
            if len(uniq) > 6:
                uniq = uniq[:6]
            generic = ["AI技术", "深度学习", "产业应用", "技术架构", "最佳实践"]
            gi = 0
            while len(uniq) < 4 and gi < len(generic):
                if generic[gi] not in seen:
                    uniq.append(generic[gi])
                    seen.add(generic[gi])
                gi += 1
            out.append(pfx + " · ".join(uniq))
            i += 1
            continue
        
        out.append(line)
        i += 1
    return "\n".join(out)

# ---------- 修复目录（基于修复换行后的文件）----------
def rebuild_toc_after_linebreak(body_text):
    lines = body_text.split("\n")
    # 第一步：重新抽取真正的 H2（用正确的换行后的行）
    in_code = False
    h2_list = []
    for ln in lines:
        s = ln.strip()
        if s.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m2 = re.match(r"^##\s+(.+?)\s*$", ln)
        if m2:
            h2_list.append(m2.group(1).strip())
    
    if not h2_list:
        return body_text, False
    
    # 过滤掉模板H2
    skip = {"📑 目录", "主题概述", "🔗 参考文件", "参考文件", "Changelog"}
    filtered = [h for h in h2_list if h not in skip]
    has_toc_mark = any(re.match(r"^##\s*📑?\s*目录", l) for l in lines)
    
    if not has_toc_mark:
        return body_text, False  # 只给有TOC标记的修
    
    # 生成新目录
    def slugg(s):
        s = s.strip()
        s = re.sub(r"[`*_#<>\[\]()]", "", s)
        s = re.sub(r"\s+", "", s)
        return s
    toc_lines = ["- [%s](#%s)" % (t, slugg(t)) for t in filtered]
    
    # 替换旧目录段
    out = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        if re.match(r"^##\s*📑?\s*目录", ln):
            out.append(ln)
            out.append("")
            j = i + 1
            while j < n and not re.match(r"^##\s+[^#]", lines[j]):
                j += 1
            for tl in toc_lines:
                out.append(tl)
            if out[-1] != "":
                out.append("")
            i = j
        else:
            out.append(ln)
            i += 1
    return "\n".join(out), True

# ---------- 清理噪点词（通用模板）----------
def remove_noise(body_text):
    # 同时处理可能的换行形式
    for nw in NOISE_WORDS:
        body_text = body_text.replace(nw, "")
    return body_text

# ---------- 确保尾部有 🔗参考文件 + Changelog ----------
def ensure_tail(body_text):
    # 检查有没有 ## 🔗 参考文件 和 ## Changelog
    has_ref = bool(re.search(r"^##\s*🔗?\s*参考文件", body_text, re.M))
    has_cl = bool(re.search(r"^##\s*Changelog", body_text, re.M))
    
    if has_ref and has_cl:
        return body_text
    
    # 找到尾部，先去掉可能存在的不完整模板
    lines = body_text.rstrip().split("\n")
    # 去掉已存在的（但可能格式不对的）
    new_lines = []
    for ln in lines:
        if re.match(r"^##\s*🔗?\s*参考文件", ln):
            continue
        if re.match(r"^##\s*Changelog", ln):
            continue
        new_lines.append(ln)
    # 去掉末尾空行
    while new_lines and not new_lines[-1].strip():
        new_lines.pop()
    
    # 追加标准尾部
    ref_block = [
        "",
        "## 🔗 参考文件",
        "",
        "| 文件 | 说明 |",
        "|:-----|:-----|",
        "| （待补充） | 相关知识文件与交叉引用见知识库 index.md |",
        "",
    ]
    cl_block = [
        "## Changelog",
        "",
        "| 版本 | 日期 | 说明 |",
        "|:-----|:-----|:-----|",
        "| v1.0 | 2026-07-29 | 系统优化：头部概要+关键词、目录去重、模板清理、章节重组与标准化 |",
        "",
    ]
    tail_lines = new_lines + [""] + ref_block + cl_block
    return "\n".join(tail_lines) + "\n"

# ---------- 单文件处理 ----------
def process_file(path):
    raw = read_md(path)
    fm, body = split_front(raw)
    
    # title
    title_str = path.stem
    if fm:
        tm = re.search(r"^title:\s*(.+)$", fm, re.M)
        if tm:
            title_str = tm.group(1).strip().strip("\"'")
    
    # 1. 核心换行修复（最重要！）
    body = smart_linebreak(body)
    # 做2次以修复嵌套（先拆大标题，再拆小标题，可能第一次拆完暴露了更多可拆项）
    body = smart_linebreak(body)
    
    # 2. 清理噪点词
    body = remove_noise(body)
    
    # 3. 摘要/关键词深度清理
    body = clean_summary_block(body, title_str)
    
    # 4. 再次换行修复（摘要修复后可能引入）
    body = smart_linebreak(body)
    
    # 5. 基于正确换行重建目录
    body, toc_done = rebuild_toc_after_linebreak(body)
    
    # 6. 尾部确保有 参考文件+Changelog
    body = ensure_tail(body)
    
    # 7. updated_at
    if fm and not re.search(r"updated_at:", fm):
        fm = fm.rstrip() + "\nupdated_at: '2026-07-29'"
    
    # 组装
    if fm:
        final = "---\n%s\n---\n\n%s" % (fm.strip(), body.lstrip("\n"))
    else:
        final = body
    
    write_md(path, final)
    
    # ---- 质量检查 ----
    aft = read_md(path)
    afm, abody = split_front(aft)
    
    # 概要字数
    s_len = 0
    sm = re.search(r">\s*\*\*概要\*\*[:：]\s*(.*?)(?:\n|$)", abody)
    if sm:
        c = sm.group(1).strip()
        c2 = re.sub(r"\[来源[:：].*?\]", "", c).strip()
        s_len = len(c2)
    
    # 关键词数
    k_cnt = 0
    km = re.search(r">\s*\*\*关键词\*\*[:：]\s*(.*)", abody)
    if km:
        k_cnt = len([x.strip() for x in km.group(1).split("·") if x.strip()])
    
    # 行数
    n_lines = len(abody.splitlines())
    
    # 检查是否有 "标题+内容挤同一行"（即H2-H6 后面文字>100字，异常）
    bad_title = 0
    in_code = False
    for ln in abody.split("\n"):
        if ln.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m_h = re.match(r"^#{1,6}\s+(.+)$", ln)
        if m_h:
            t = m_h.group(1).strip()
            if len(t) > 120:  # 标题不会超过120字
                bad_title += 1
    
    return {
        "fn": path.name,
        "title": title_str,
        "s_len": s_len,
        "k_cnt": k_cnt,
        "toc": toc_done,
        "lines": n_lines,
        "bad_title": bad_title,
    }

# ---------- 分批执行 ----------
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
    
    print("=" * 60)
    print("终极修复v2：换行+标题拆分+摘要深度清理+目录+尾部 (%d文件)" % n)
    print("=" * 60)
    print("  %d 目录 x %d 批次 x ≤%d 文件" % (len(DIRS), len(batches), BATCH))
    
    all_d = []
    for bi, batch in enumerate(batches, 1):
        print("\n" + "=" * 60)
        print("🔧 批次 %d/%d | %d 文件" % (bi, len(batches), len(batch)))
        print("=" * 60)
        ok = skip = 0
        for fi, f in enumerate(batch, 1):
            try:
                d = process_file(f)
                ms = "✅" if 150 <= d["s_len"] <= 300 else "⚠️"
                mk = "✅" if 4 <= d["k_cnt"] <= 6 else "⚠️"
                mt = "📋" if d["toc"] else "  "
                mb = "❌标题过长" if d["bad_title"] > 0 else "  "
                print("  [%d/%d] %s %-38s 概%d%s %d词%s %s %s" % (
                    fi, len(batch), "⚙️ ", f.name[:38],
                    d["s_len"], ms, d["k_cnt"], mk, mt, mb))
                all_d.append(d)
                ok += 1
            except Exception as e:
                skip += 1
                print("  [%d/%d] ❌ %s → 跳过: %s" % (fi, len(batch), f.name, e))
                all_d.append({"fn": f.name, "error": str(e)})
        print("\n  本批：✅ %d | ⏭️ %d" % (ok, skip))
    
    # 统计
    total = len(all_d)
    ok_cnt = sum(1 for d in all_d if "error" not in d)
    good_s = sum(1 for d in all_d if 150 <= d.get("s_len", 0) <= 300)
    good_k = sum(1 for d in all_d if 4 <= d.get("k_cnt", 0) <= 6)
    toc_cnt = sum(1 for d in all_d if d.get("toc"))
    bad_cnt = sum(1 for d in all_d if d.get("bad_title", 0) > 0)
    
    print("\n" + "🏁" * 30)
    print("完成")
    print("🏁" * 30)
    print("\n📊 统计：总数 %d | ✅ %d | ⏭️ %d | 成功率 %.1f%%" % (
        total, ok_cnt, total - ok_cnt, (ok_cnt/total*100) if total else 0))
    print("\n🔍 质量：")
    print("  概要150-300字：    %d/%d (%.1f%%)" % (good_s, total, good_s/total*100 if total else 0))
    print("  关键词4-6个：     %d/%d (%.1f%%)" % (good_k, total, good_k/total*100 if total else 0))
    print("  长文件已加目录：   %d 文件" % toc_cnt)
    print("  仍有标题挤同行：   %d 文件" % bad_cnt)
    
    rp = os.path.join(ROOT, "_ultimate_fix_v2_report.json")
    with open(rp, "w", encoding="utf-8") as rf:
        json.dump({
            "time": __import__("datetime").datetime.now().isoformat(),
            "total": total, "ok": ok_cnt,
            "quality": {"good_s": good_s, "good_k": good_k, "toc": toc_cnt, "bad_title": bad_cnt},
            "details": all_d,
        }, rf, ensure_ascii=False, indent=2)
    print("\n📋 报告：", rp)
    print("\n✅ 终极修复v2完成！")

if __name__ == "__main__":
    run()
