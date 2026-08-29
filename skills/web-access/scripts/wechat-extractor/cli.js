#!/usr/bin/env node
/**
 * wechat-extractor CLI — 微信公众号文章富元数据提取器
 * 用法:
 *   node cli.js <URL>                      # 提取全部元数据 (JSON)
 *   node cli.js <URL> --content            # 仅打印正文 HTML
 *   node cli.js <URL> --summary            # 精简摘要 (标题/公众号/类型/时间/错误)
 *   node cli.js <URL> --md <out.md>        # 转 Markdown 落盘
 *   echo "<HTML>" | node cli.js -          # 从 HTML 解析 (配合其他抓取器)
 */
const fs = require('fs');
const { extract } = require('./extract');

const args = process.argv.slice(2);
const urlArg = args[0];
const flags = args.slice(1);

if (!urlArg) {
  console.error('Usage: node cli.js <URL|-> [--content|--summary|--md out.md]');
  process.exit(1);
}

async function main() {
  let result;
  if (urlArg === '-') {
    const html = fs.readFileSync(0, 'utf-8');
    result = await extract(html);
  } else {
    result = await extract(urlArg);
  }

  if (!result.done) {
    // 错误码诊断输出（对齐 errors.js 17 种错误）
    console.log(JSON.stringify({
      done: false,
      code: result.code,
      msg: result.msg,
      url: result.url || urlArg
    }, null, 2));
    process.exit(2);
  }

  const d = result.data;

  if (flags.includes('--content')) {
    console.log(d.msg_content || '');
    return;
  }

  if (flags.includes('--summary')) {
    console.log(`标题: ${d.msg_title}`);
    console.log(`公众号: ${d.account_name} (${d.account_alias || '无别名'})`);
    console.log(`作者: ${d.msg_author || 'N/A'}`);
    console.log(`类型: ${d.msg_type} | 时间: ${d.msg_publish_time_str}`);
    console.log(`封面: ${d.msg_cover || 'N/A'}`);
    console.log(`biz: ${d.account_biz} | sn: ${d.msg_sn} | mid: ${d.msg_mid}`);
    console.log(`链接: ${d.msg_link}`);
    return;
  }

  const mdIdx = flags.indexOf('--md');
  if (mdIdx >= 0 && flags[mdIdx + 1]) {
    const md = `# ${d.msg_title}\n\n> 作者: ${d.msg_author || d.account_name}\n> 公众号: ${d.account_name}\n> 发布时间: ${d.msg_publish_time_str}\n> 原文: ${d.msg_link}\n\n${d.msg_content || ''}\n`;
    fs.writeFileSync(flags[mdIdx + 1], md, 'utf-8');
    console.log(`✅ 已保存 Markdown: ${flags[mdIdx + 1]}`);
    return;
  }

  console.log(JSON.stringify(result.data, null, 2));
}

main().catch(e => {
  console.error(JSON.stringify({ done: false, code: -1, msg: e.message }));
  process.exit(1);
});
