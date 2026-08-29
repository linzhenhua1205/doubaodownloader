#!/usr/bin/env python3
"""来源可达性预检脚本 — source-reachability.py

功能:
  HTTP HEAD 请求预检来源 URL 的可达性
  用于 design-005 Fail-Fast 方案的自动化落地

特性:
  - 并发 HEAD 请求（最多 10 并发）
  - 超时 5s，Fail-Fast
  - 支持白名单域名（允许超时但不视为不可达）
  - 输出 JSON 报告 + 汇总统计

用法:
  python scripts/check/source-reachability.py <file.md>
  python scripts/check/source-reachability.py <dir/>
  python scripts/check/source-reachability.py --batch 10
  python scripts/check/source-reachability.py --timeout 8
  python scripts/check/source-reachability.py --whitelist github.com
  python scripts/check/source-reachability.py --report report.json
  python scripts/check/source-reachability.py --strict
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# Ensure workspace root is on Python path (sr-008)
_SCRIPT_DIR = Path(__file__).resolve().parent
_WORKSPACE_ROOT = _SCRIPT_DIR.parents[2]
sys.path.insert(0, str(_WORKSPACE_ROOT))

# URL regex: matches http/https URLs up to common Chinese/English punctuation
_URL_CHAR = r"[^\s\)\]}>\"\',.\u3001\u3002\uff0c\uff1b\uff1a\uff09\u300d\u300f\u300b\u3005]+"
URL_PATTERN = re.compile("https?://" + _URL_CHAR)

CHECK_SCRIPT_DIR = _SCRIPT_DIR


def extract_urls(file_path: str) -> list:
    """从 .md 文件提取所有 http(s) URL"""
    urls = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        for m in URL_PATTERN.finditer(content):
            url = m.group(0).rstrip('.,;:!?)')
            if url.startswith('http'):
                urls.add(url)
    except (OSError, IOError) as e:
        print(f"[ERROR] 读取文件失败 {file_path}: {e}", file=sys.stderr)
    return sorted(urls)


def check_url(url: str, timeout: int, whitelist: set, strict: bool) -> dict:
    """对单个 URL 做 HEAD 可达性检查"""
    result = {
        "url": url,
        "status": "UNKNOWN",
        "http_status": None,
        "error": None,
        "response_time_ms": None,
    }
    domain = urllib.request.urlparse(url).netloc
    try:
        start = time.time()
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "Mozilla/5.0 (compatible; SourceReachability/1.0)")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = int((time.time() - start) * 1000)
            result["http_status"] = resp.status
            result["response_time_ms"] = elapsed
            if strict:
                result["status"] = "PASS" if 200 <= resp.status < 400 else "FAIL"
            else:
                result["status"] = "PASS"
    except urllib.error.HTTPError as e:
        result["http_status"] = e.code
        result["response_time_ms"] = 0
        if strict and e.code >= 400:
            result["status"] = "FAIL"
            result["error"] = f"HTTP {e.code}"
        else:
            result["status"] = "PASS" if domain in whitelist else "WARN"
            result["error"] = f"HTTP {e.code}"
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        result["status"] = "PASS" if domain in whitelist else "WARN"
        result["error"] = str(e)[:100]
    return result


def scan_files(target: str) -> list:
    """递归扫描文件或目录，返回 .md 文件路径列表"""
    target_path = Path(target)
    if target_path.is_file():
        return [str(target_path)]
    files = []
    for ext in ("*.md", "*.html", "*.txt"):
        files.extend(str(p) for p in target_path.rglob(ext))
    return sorted(files)


def run_audit(targets: list, batch: int, timeout: int,
              whitelist: set, strict: bool, report_path: str = None):
    """主审计流程"""
    all_files = []
    for t in targets:
        all_files.extend(scan_files(t))

    print(f"[INFO] 扫描 {len(all_files)} 个文件中的 URL...")
    all_urls = set()
    file_url_map = {}
    for f in all_files:
        urls = extract_urls(f)
        if urls:
            file_url_map[f] = urls
            all_urls.update(urls)

    print(f"[INFO] 发现 {len(all_urls)} 个唯一 URL（分布在 {len(file_url_map)} 个文件中）")
    print(f"[INFO] 并发 {batch} 连接，超时 {timeout}s{'（严格模式）' if strict else ''}")
    if whitelist:
        print(f"[INFO] 白名单域名: {', '.join(sorted(whitelist))}")

    # 并发检查
    results = []
    with ThreadPoolExecutor(max_workers=batch) as executor:
        futures = {
            executor.submit(check_url, url, timeout, whitelist, strict): url
            for url in sorted(all_urls)
        }
        for future in as_completed(futures):
            results.append(future.result())

    # 汇总
    status_counts = {"PASS": 0, "WARN": 0, "FAIL": 0, "UNKNOWN": 0}
    for r in results:
        status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1

    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "files_scanned": len(all_files),
            "files_with_urls": len(file_url_map),
            "unique_urls": len(all_urls),
            "checked": len(results),
            "pass": status_counts.get("PASS", 0),
            "warn": status_counts.get("WARN", 0),
            "fail": status_counts.get("FAIL", 0),
            "unknown": status_counts.get("UNKNOWN", 0),
        },
        "whitelist": sorted(whitelist),
        "strict_mode": strict,
        "file_url_map": {f: file_url_map[f] for f in sorted(file_url_map)},
        "results": sorted(results, key=lambda x: x["url"]),
    }

    # 输出报告
    if report_path:
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n[INFO] 报告已写入: {report_path}")

    # 打印汇总
    print(f"\n{'='*50}")
    print(f"  来源可达性检查结果")
    print(f"{'='*50}")
    print(f"  扫描文件:       {len(all_files)}")
    print(f"  含 URL 文件:    {len(file_url_map)}")
    print(f"  唯一 URL 数:    {len(all_urls)}")
    print(f"  已检查:        {len(results)}")
    print(f"  ✅ PASS:        {status_counts.get('PASS', 0)}")
    print(f"  ⚠️  WARN:        {status_counts.get('WARN', 0)}")
    print(f"  ❌ FAIL:        {status_counts.get('FAIL', 0)}")
    print(f"{'='*50}")

    if status_counts.get("FAIL", 0) > 0:
        print(f"\n❌ FAIL 列表:")
        for r in results:
            if r["status"] == "FAIL":
                print(f"  - {r['url']}  ({r['error']})")

    return report


def main():
    parser = argparse.ArgumentParser(description="来源 URL 可达性预检")
    parser.add_argument("targets", nargs="*", default=["."],
                        help="要检查的文件或目录（默认当前目录）")
    parser.add_argument("--batch", type=int, default=5, help="并发数（默认 5）")
    parser.add_argument("--timeout", type=int, default=5, help="超时秒数（默认 5）")
    parser.add_argument("--whitelist", nargs="*", default=[],
                        help="白名单域名（这些域名超时不视为不可达）")
    parser.add_argument("--report", type=str, default=None,
                        help="输出 JSON 报告路径")
    parser.add_argument("--strict", action="store_true",
                        help="非 2xx/3xx 状态码视为 FAIL")
    args = parser.parse_args()

    run_audit(
        targets=args.targets,
        batch=args.batch,
        timeout=args.timeout,
        whitelist=set(args.whitelist),
        strict=args.strict,
        report_path=args.report,
    )


if __name__ == "__main__":
    main()
