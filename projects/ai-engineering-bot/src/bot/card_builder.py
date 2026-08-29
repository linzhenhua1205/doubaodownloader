"""飞书消息卡片构建器 — 6 种场景卡片模板 + 通用工具函数。"""

from __future__ import annotations

import json
from typing import Any


# ══════════════════════════════════════════════════════════════════════
# 通用构建函数
# ══════════════════════════════════════════════════════════════════════


def _md(text: str) -> dict[str, str]:
    """lark_md 文本块。"""
    return {"tag": "lark_md", "content": text}


def _plain(text: str) -> dict[str, str]:
    """plain_text 文本。"""
    return {"tag": "plain_text", "content": text}


def _button(text: str, value: str = "", url: str = "", type_: str = "default") -> dict[str, Any]:
    """按钮。"""
    btn: dict[str, Any] = {
        "tag": "button",
        "text": _plain(text),
        "type": type_,
    }
    if url:
        btn["url"] = url
    if value:
        btn["value"] = {"action": value}
    return btn


def _progress_bar(percent: float, width: int = 20) -> str:
    """文本进度条。"""
    filled = int(percent * width)
    return "█" * filled + "░" * (width - filled)


# ══════════════════════════════════════════════════════════════════════
# 卡片构建函数
# ══════════════════════════════════════════════════════════════════════


def research_result_card(
    title: str,
    summary: str,
    details: list[str],
    report_url: str = "",
    task_id: str = "",
) -> dict[str, Any]:
    """
    📊 技术调研结果卡片。

    对应场景: 用户执行 /ai research 完成后推送。
    """
    detail_lines = "\n".join(f"- {d}" for d in details)
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": _plain(f"📊 {title}"),
            "template": "blue",
        },
        "elements": [
            {
                "tag": "div",
                "text": _md(f"**调研完成** ✅\n\n**核心结论**:\n{summary}\n\n**关键发现**:\n{detail_lines}"),
            },
            {
                "tag": "hr",
            },
            {
                "tag": "action",
                "actions": [
                    _button("📄 查看完整报告", url=report_url) if report_url else {},
                    _button("📋 归档知识库", value=f"archive:{task_id}", type_="primary"),
                    _button("💬 追问", value=f"followup:{task_id}"),
                ],
            },
        ],
    }
    return card


def progress_card(
    title: str,
    stages: list[tuple[str, float]],  # [(stage_name, progress_0~1), ...]
    elapsed: str = "",
    eta: str = "",
    task_id: str = "",
) -> dict[str, Any]:
    """
    ⏳ 进度追踪卡片。

    对应场景: 长耗时任务（调研/分析/审查）执行中推送。
    """
    bar_lines = "\n".join(
        f"{name} {_progress_bar(pct)} {int(pct * 100)}%"
        for name, pct in stages
    )
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": _plain(f"⏳ {title}"),
            "template": "purple",
        },
        "elements": [
            {
                "tag": "div",
                "text": _md(f"**进度**:\n```\n{bar_lines}\n```"),
            },
            {
                "tag": "note",
                "element": _md(f"⏱ 已用: {elapsed}  •  预计剩余: {eta}"),
            },
            {
                "tag": "action",
                "actions": [
                    _button("❌ 取消任务", value=f"cancel:{task_id}", type_="danger"),
                ],
            },
        ],
    }
    return card


def comparison_card(
    title: str,
    headers: list[str],
    rows: list[list[str]],
    task_id: str = "",
) -> dict[str, Any]:
    """
    📋 方案对比卡片。

    对应场景: 技术方案对比 / 竞品分析完成。
    """
    header_row = " | ".join(f"**{h}**" for h in headers)
    table_rows = "\n".join(" | ".join(row) for row in rows)
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": _plain(f"📋 {title}"),
            "template": "blue",
        },
        "elements": [
            {
                "tag": "div",
                "text": _md(f"**方案对比**:\n\n{header_row}\n{' | '.join('---' for _ in headers)}\n{table_rows}"),
            },
            {
                "tag": "hr",
            },
            {
                "tag": "action",
                "actions": [
                    _button("📄 查看完整报告", value=f"detail:{task_id}", type_="primary"),
                    _button("💬 追问", value=f"followup:{task_id}"),
                ],
            },
        ],
    }
    return card


def diagnosis_card(
    title: str,
    severity: str,
    root_cause: str,
    steps: list[str],
    task_id: str = "",
) -> dict[str, Any]:
    """
    🔍 问题诊断结果卡片。

    对应场景: /ai analyze 完成。
    """
    templates = {
        "critical": {"tag": "red", "emoji": "🔴"},
        "warning": {"tag": "yellow", "emoji": "🟡"},
        "info": {"tag": "blue", "emoji": "ℹ️"},
    }
    tmpl = templates.get(severity, templates["info"])

    step_lines = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": _plain(f"{tmpl['emoji']} {title}"),
            "template": tmpl["tag"],
        },
        "elements": [
            {
                "tag": "div",
                "text": _md(f"**根因分析**:\n{root_cause}\n\n**处理步骤**:\n{step_lines}"),
            },
            {
                "tag": "action",
                "actions": [
                    _button("📄 完整报告", value=f"detail:{task_id}", type_="primary"),
                    _button("🔄 重新诊断", value=f"rediagnose:{task_id}"),
                    _button("💬 追问", value=f"followup:{task_id}"),
                ],
            },
        ],
    }
    return card


def approval_card(
    title: str,
    summary: str,
    quality_score: int,
    risk_level: str,
    approval_code: str = "",
) -> dict[str, Any]:
    """
    📋 方案评审/审批卡片。

    对应场景: 方案生成后发起审批流。
    """
    risk_emoji = {"低": "🟢", "中": "🟡", "高": "🔴"}.get(risk_level, "⚪")
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": _plain(f"📋 {title}"),
            "template": "blue",
        },
        "elements": [
            {
                "tag": "div",
                "text": _md(
                    f"**方案摘要**:\n{summary}\n\n"
                    f"**质量评分**: {quality_score}/100\n"
                    f"**风险等级**: {risk_emoji} {risk_level}"
                ),
            },
            {
                "tag": "hr",
            },
            {
                "tag": "action",
                "actions": [
                    _button("✅ 批准", value=f"approve:{approval_code}", type_="primary"),
                    _button("❌ 驳回", value=f"reject:{approval_code}", type_="danger"),
                    _button("📝 提意见", value=f"comment:{approval_code}"),
                ],
            },
        ],
    }
    return card


def weekly_report_card(
    week: str,
    summary: str,
    stats: dict[str, int],
    highlights: list[str],
    report_url: str = "",
) -> dict[str, Any]:
    """
    📊 知识库周报卡片。

    对应场景: 每周知识报告推送。
    """
    highlights_text = "\n".join(f"✨ {h}" for h in highlights)
    stat_line = "  •  ".join(f"{k}: **{v}**" for k, v in stats.items())
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": _plain(f"📊 知识库周报 - 第{week}周"),
            "template": "blue",
        },
        "elements": [
            {
                "tag": "div",
                "text": _md(
                    f"**本周动态**:\n{summary}\n\n"
                    f"**数据统计**:\n{stat_line}\n\n"
                    f"**亮点**:\n{highlights_text}"
                ),
            },
            {
                "tag": "action",
                "actions": [
                    _button("📄 查看完整周报", url=report_url) if report_url else {},
                    _button("📋 归档", value="archive_weekly", type_="primary"),
                ],
            },
        ],
    }
    return card


def help_card() -> dict[str, Any]:
    """ℹ️ 帮助信息卡片。"""
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": _plain("🤖 AI 工程化平台 - 使用帮助"),
            "template": "blue",
        },
        "elements": [
            {"tag": "div", "text": _md("**基础指令**:\n")},
            {
                "tag": "div",
                "text": _md(
                    "/ai ask [问题]       即问即答（RAG + 知识库）\n"
                    "/ai research [主题]  启动技术调研流水线\n"
                    "/ai review [PR_ID]   触发代码审查流水线\n"
                    "/ai doc [主题]       生成技术文档\n"
                    "/ai analyze [问题]   启动问题诊断流水线\n"
                    "/ai summary [URL]    摘要并归档知识库\n"
                    "/ai plan [描述]      任务分解到多维表格\n"
                    "/ai status           查询所有任务状态\n"
                    "/ai status [TaskID]  查询指定任务\n"
                    "/ai cancel [TaskID]  取消进行中任务\n"
                    "/ai help             显示此帮助"
                ),
            },
            {"tag": "hr"},
            {
                "tag": "div",
                "text": _md("**特殊交互**:\n@机器人 [自然语言]  自由对话模式\n@机器人 + 分享链接  自动归档链接内容"),
            },
        ],
    }
    return card
