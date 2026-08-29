#!/usr/bin/env node
/**
 * markdown-lint-audit.mjs — 基于 markdownlint (MD001-MD063) 的全库格式审查与修复
 *
 * 定位：文件内部 Markdown 格式"一次到位"。用 GitHub 标准工具 markdownlint 规则库，
 * 通过 Node API 直接调用（lint + applyFix，绕开 cli2 的 glob/配置加载怪癖）。
 *
 * 规则适配中文知识库：
 *   - 禁用: MD013(行长,中文不适用) MD033(内联HTML) MD041(首行H1,头部有元信息)
 *           MD060(表格列对齐,中文CJK宽度误报) MD023(库 bug)
 *   - 调整: MD024(siblings_only) MD012(max 3 空行) MD009(br_spaces 0)
 *   - MD040(代码块缺语言): 依据 lint 行号精确加 ```text（内容级修改，单独验证）
 *   - 不修: MD001(标题跳级→改锚点破坏链接) MD025(多H1) MD034(裸URL) MD036(强调当标题)
 *           MD056(表格列数不一致,结构性)
 *
 * 用法:
 *   node scripts/check/markdown-lint-audit.mjs                # 扫描报告
 *   node scripts/check/markdown-lint-audit.mjs --fix          # 备份+迭代修复+验证
 *   node scripts/check/markdown-lint-audit.mjs --dir knowledge/02_rd
 */

import { lint } from 'file:///home/lzh/.npm-global/lib/node_modules/markdownlint-cli2/node_modules/markdownlint/lib/exports-sync.mjs';
import { applyFixes } from 'file:///home/lzh/.npm-global/lib/node_modules/markdownlint-cli2/node_modules/markdownlint/lib/exports.mjs';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, copyFileSync, mkdirSync, existsSync } from 'node:fs';
import { execSync } from 'node:child_process';
import path from 'node:path';

const DIRS = ['knowledge/02_rd', 'knowledge/03_AI', 'knowledge/04_person',
  'knowledge/05_tools', 'knowledge/06_others', 'knowledge/07_industry-research',
  'knowledge/01_survey'];
const EXCLUDE = ['weekly-reports', 'bak', 'oldbak', 'tmp', '.git'];
const MAX_LINES = 10000; // 豁免超大 raw 素材（notes-summary 71k 行等）
const MAX_ROUNDS = 5;    // applyFix 迭代轮次上限

const CONFIG = {
  default: true,
  MD013: false,          // line-length 中文不适用
  MD033: false,          // inline-html
  MD041: false,          // first-line-heading (头部元信息)
  MD060: false,          // table-column-style (中文CJK宽度误报)
  MD023: false,          // heading-start-left (库 bug)
  MD051: false,          // link-reference-definitions: 100% 误报 TOC 锚点链接 [text](#anchor)
  MD024: { siblings_only: true },
  MD012: { maximum: 3 },
  MD009: { br_spaces: 0 },
};

function collectFiles(dirs) {
  const files = [];
  for (const d of dirs) {
    if (!existsSync(d)) continue;
    const out = execSync(`find "${d}" -name "*.md" -type f`, { encoding: 'utf8' });
    for (const f of out.split('\n').filter(Boolean)) {
      const parts = path.relative('.', f).split('/');
      if (!parts.some(p => EXCLUDE.includes(p))) files.push(f);
    }
  }
  return files;
}

function contentHash(file) {
  const h = createHash('md5');
  for (const line of readFileSync(file, 'utf8').split('\n')) {
    const s = line.trimEnd();
    if (s.trim()) { h.update(s); h.update('\n'); }
  }
  return h.digest('hex');
}

function summarize(results) {
  const ruleCount = {};
  let total = 0;
  const fileCount = new Set();
  for (const [file, issues] of Object.entries(results)) {
    if (!issues || !issues.length) continue;
    total += issues.length;
    fileCount.add(file);
    for (const it of issues) ruleCount[it.ruleNames[0]] = (ruleCount[it.ruleNames[0]] || 0) + 1;
  }
  return { total, fileCount: fileCount.size, ruleCount };
}

const args = process.argv.slice(2);
const doFix = args.includes('--fix');
const dirIdx = args.indexOf('--dir');
if (dirIdx >= 0) { DIRS.length = 0; DIRS.push(args[dirIdx + 1]); }

const files = collectFiles(DIRS);
console.log(`📄 扫描文件: ${files.length} (${DIRS.join(', ')})`);
console.log(`🔧 模式: ${doFix ? 'FIX 修复' : 'SCAN 仅报告'}\n`);

// ── 备份 + 基线哈希（修复前）──
let bakDir = null;
const before = {};
if (doFix) {
  bakDir = `tmp/bak/markdownlint-${new Date().toISOString().slice(0, 10)}`;
  mkdirSync(bakDir, { recursive: true });
  for (const f of files) {
    copyFileSync(f, path.join(bakDir, f.replaceAll('/', '__')));
    before[f] = contentHash(f);
  }
  console.log(`📦 备份全部 ${files.length} 文件 → ${bakDir}/`);
}

// 分批 lint 工具（50/批，整批异常降级逐文件；filesArg 可选=只查指定文件）
function lintAll(fix, filesArg = files) {
  const results = {};
  let skipped = 0;
  const BATCH = 50;
  for (let i = 0; i < filesArg.length; i += BATCH) {
    const batch = filesArg.slice(i, i + BATCH);
    const normal = [], huge = [];
    for (const f of batch) {
      let n = 0;
      try { n = readFileSync(f, 'utf8').split('\n').length; } catch { n = 0; }
      (n > MAX_LINES ? huge : normal).push(f);
    }
    skipped += huge.length;
    try {
      const r = lint({ files: normal, config: CONFIG, fix });
      Object.assign(results, r);
    } catch (e) {
      for (const f of normal) {
        try {
          const r = lint({ files: [f], config: CONFIG, fix });
          results[f] = r[f] || [];
        } catch (e2) {
          results[f] = [{ ruleNames: ['FATAL'], errorDetail: e2.message.slice(0, 120) }];
        }
      }
    }
  }
  return { results, skipped };
}

// ── 初始扫描（修复前基线）──
const { results: initialResults, skipped } = lintAll(false);
if (skipped) console.log(`⏭️ 豁免超大文件: ${skipped} 个`);
const init = summarize(initialResults);
console.log(`📊 初始问题: ${init.total} 处 / ${init.fileCount} 文件`);

// ── 迭代修复（applyFix 官方 API；只重查上一轮有问题文件，增量收敛）──
let fixedFiles = 0, fixedIssues = 0;
if (doFix) {
  let roundFiles = files;
  for (let round = 1; round <= MAX_ROUNDS; round++) {
    const { results: r } = lintAll(false, roundFiles);
    let anyFixed = false;
    const stillIssues = [];
    for (const f of roundFiles) {
      const issues = (r[f] || []).filter(it => it.fixInfo && it.ruleNames[0] !== 'FATAL');
      if (!issues.length) continue;
      const text = readFileSync(f, 'utf8');
      const fixed = applyFixes(text, issues);
      if (fixed !== text) {
        writeFileSync(f, fixed);
        fixedIssues += issues.length;
        anyFixed = true;
        stillIssues.push(f);
      }
    }
    if (!anyFixed) { console.log(`  ✅ 迭代 ${round} 轮后无 fixable 问题`); break; }
    console.log(`  🔄 第 ${round} 轮: 修复 ${roundFiles.length - stillIssues.length + stillIssues.length} 文件中 ${stillIssues.length} 个仍有问题`);
    roundFiles = stillIssues;
    if (!roundFiles.length) { console.log(`  ✅ 第 ${round} 轮收敛`); break; }
  }
  // 统计实际修改文件数（对比备份）
  fixedFiles = files.filter(f => contentHash(f) !== before[f]).length;
  console.log(`📝 实际修改文件: ${fixedFiles}`);
}

// ── 最终扫描（修复后残余）──
const { results: finalResults } = lintAll(false);
const fin = summarize(finalResults);
console.log(`\n📊 修复后残余: ${fin.total} 处 / ${fin.fileCount} 文件 (初始 ${init.total})`);
console.log('=== 残余按规则 ===');
for (const [r, c] of Object.entries(fin.ruleCount).sort((a, b) => b[1] - a[1])) {
  console.log(`  ${r}: ${c}`);
}

// ── MD040 精确修复：裸 ``` → ```text ──
let md040Fixed = 0;
if (doFix) {
  const md040 = {};
  for (const [file, issues] of Object.entries(finalResults)) {
    const lines = issues.filter(it => it.ruleNames[0] === 'MD040').map(it => it.lineNumber);
    if (lines.length) md040[file] = lines;
  }
  if (Object.keys(md040).length) {
    console.log(`\n🔧 MD040 修复 (代码块缺语言, ${Object.keys(md040).length} 文件)...`);
    for (const [file, lines] of Object.entries(md040)) {
      const text = readFileSync(file, 'utf8');
      const arr = text.split('\n');
      const lineSet = new Set(lines);
      let cnt = 0;
      for (let i = 0; i < arr.length; i++) {
        // 支持缩进与引用块前缀：  ```  /  > ```  →  ```text
        const m = arr[i].match(/^(\s*(?:>\s*)*)(`{3,})\s*$/);
        if (lineSet.has(i + 1) && m) {
          arr[i] = `${m[1]}${m[2]}text`;
          cnt++;
        }
      }
      if (cnt) { writeFileSync(file, arr.join('\n')); md040Fixed += cnt; }
    }
    console.log(`  ✅ MD040 修复 ${md040Fixed} 处围栏 → \`\`\`text`);
  }
}

// ── 验证 ──
if (doFix) {
  console.log('\n🔍 内容不丢失验证...');
  // 通用逐行对比：任何变化文件，只允许 ``` → ```text 类的围栏语言标注
  let lost = 0, verified = 0;
  for (const f of files) {
    if (contentHash(f) === before[f]) { verified++; continue; }
    const b = readFileSync(path.join(bakDir, f.replaceAll('/', '__')), 'utf8').split('\n');
    const a = readFileSync(f, 'utf8').split('\n');
    let ok = true;
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      const x = b[i] ?? '', y = a[i] ?? '';
      // 允许: 原行是"前缀+```"（缩进/引用块），新行是"同前缀+```text"
      const mx = x.match(/^(\s*(?:>\s*)*)(`{3,})\s*$/);
      if (x !== y && !(mx && y === `${mx[1]}${mx[2]}text`)) { ok = false; break; }
    }
    ok ? verified++ : (lost++, console.log(`  ❌ 非预期变化! ${f}`));
  }
  console.log(lost === 0
    ? `  ✅ ${verified}/${files.length} 文件验证通过（纯格式零丢失；MD040 仅追加语言标注）`
    : `  🚨 ${lost} 文件非预期变化，检查 ${bakDir}/`);
  const totalFixed = files.filter(f => contentHash(f) !== before[f]).length;
  console.log(`\n修复文件: ${totalFixed} | 修复问题数: ${init.total - fin.total} | MD040: ${md040Fixed} | 残余: ${fin.total}`);
}
