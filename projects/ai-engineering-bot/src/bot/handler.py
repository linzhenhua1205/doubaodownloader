"""消息处理器 — 各指令/意图的具体处理逻辑。"""

from __future__ import annotations

from typing import Any

from bot.card_builder import (
    help_card,
    progress_card,
    research_result_card,
)
from bot.router import Intent, router
from utils import get_logger, feishu_client, llm, task_store

log = get_logger("handler")


async def handle_ask(
    question: str, user_id: str, chat_id: str, message_id: str
) -> str | dict[str, Any]:
    """/ai ask — 即问即答（RAG + 知识库）。"""
    log.info("handle_ask", question=question[:80])

    # 发送"处理中"提示
    task_id = await task_store.create_task("ask", user_id, chat_id, {"question": question})
    await task_store.update_task(task_id, status="running")
    await feishu_client.send_text(chat_id, f"🔍 正在检索知识库...")

    # 构建 RAG prompt
    # TODO: 接入知识库检索 (knowledge/retriever.py)
    messages = [
        {
            "role": "system",
            "content": "你是服务器研发领域的 AI 专家。基于知识库内容回答问题。"
            "如果知识库中没有相关信息，请明确告知。回答要求:\n"
            "1. 先给出结论概要\n"
            "2. 再展开详细说明\n"
            "3. 关键数据必须注明来源\n"
            "4. 使用 markdown 格式",
        },
        {"role": "user", "content": question},
    ]

    answer = await llm.chat(messages)
    await task_store.update_task(task_id, status="completed", result={"answer": answer})
    return answer


async def handle_research(
    topic: str, user_id: str, chat_id: str, message_id: str
) -> str | dict[str, Any]:
    """/ai research — 启动技术调研流水线。"""
    log.info("handle_research", topic=topic)

    task_id = await task_store.create_task("research", user_id, chat_id, {"topic": topic})
    await task_store.update_task(task_id, status="running")

    # 发送进度卡片
    card = progress_card(
        title=f"🔬 技术调研: {topic[:40]}{'...' if len(topic) > 40 else ''}",
        stages=[
            ("知识库检索", 0.0),
            ("厂商官网", 0.0),
            ("竞品对比", 0.0),
            ("报告生成", 0.0),
        ],
        elapsed="0s",
        eta="计算中...",
        task_id=task_id,
    )
    await feishu_client.send_card(chat_id, card)

    # TODO: 触发 workflow engine 执行调研流水线
    # 目前返回 prompt 让 LLM 直接作答
    messages = [
        {
            "role": "system",
            "content": "你是服务器硬件领域的资深技术调研专家。请按以下框架输出调研报告:\n\n"
            "## 调研主题\n## 核心结论\n## 关键发现（数据+来源）\n## 厂商/方案对比\n## 趋势与建议\n\n"
            "要求: 所有数据注明来源，优先引用标准规范、官方白皮书和一线报告。",
        },
        {"role": "user", "content": f"请对以下主题进行深度技术调研:\n{topic}"},
    ]

    answer = await llm.chat(messages)
    await task_store.update_task(task_id, status="completed", progress=1.0, result={"report": answer})
    return answer


async def handle_review(
    pr_id: str, user_id: str, chat_id: str, message_id: str
) -> str | dict[str, Any]:
    """/ai review — 触发代码审查流水线。"""
    log.info("handle_review", pr_id=pr_id)

    task_id = await task_store.create_task("review", user_id, chat_id, {"pr_id": pr_id})
    await task_store.update_task(task_id, status="running")

    # TODO: 接入 Git API 获取 PR diff + CodeReview 工程化体系
    return f"🔍 正在分析 PR `{pr_id}` 的代码审查...\n\n审查完成后将通过卡片推送结果。如需查询状态: `/ai status {task_id}`"


async def handle_doc(
    topic: str, user_id: str, chat_id: str, message_id: str
) -> str | dict[str, Any]:
    """/ai doc — 生成技术文档。"""
    log.info("handle_doc", topic=topic)

    task_id = await task_store.create_task("doc", user_id, chat_id, {"topic": topic})
    await task_store.update_task(task_id, status="running")

    messages = [
        {
            "role": "system",
            "content": "你是服务器领域资深技术文档撰写专家。请输出结构清晰、数据可验证的专业文档。\n"
            "文档格式要求:\n"
            "1. 目录 (TOC)\n"
            "2. 摘要/核心结论\n"
            "3. 按 MECE 原则展开\n"
            "4. 关键数据注明来源\n"
            "5. 交叉链接相关文档",
        },
        {"role": "user", "content": f"请生成技术文档:\n{topic}"},
    ]

    answer = await llm.chat(messages)
    await task_store.update_task(task_id, status="completed", result={"document": answer})
    return answer


async def handle_analyze(
    issue: str, user_id: str, chat_id: str, message_id: str
) -> str | dict[str, Any]:
    """/ai analyze — 问题诊断流水线。"""
    log.info("handle_analyze", issue=issue[:80])

    messages = [
        {
            "role": "system",
            "content": "你是服务器硬件/软件系统的故障诊断专家。请按以下框架进行分析:\n\n"
            "## 问题描述\n## 故障现象\n## 可能原因（按概率排序）\n## 诊断步骤\n"
            "## 根因分析（5W + 鱼骨图）\n## 修复方案\n## 预防措施\n\n"
            "关键原则:\n"
            "- 先排查最可能、影响最小的因素\n"
            "- 每个推断必须有依据\n"
            "- 区分现象和根因",
        },
        {"role": "user", "content": f"请分析以下问题:\n{issue}"},
    ]

    answer = await llm.chat(messages)
    return answer


async def handle_summary(
    url: str, user_id: str, chat_id: str, message_id: str
) -> str | dict[str, Any]:
    """/ai summary — 摘要并归档知识库。"""
    log.info("handle_summary", url=url)

    # TODO: 抓取 URL 内容 + 归档到 knowledge/06_others/sources/
    return f"📚 正在处理链接: {url}\n\n完成摘要后将自动归档到知识库并通知您。"


async def handle_plan(
    description: str, user_id: str, chat_id: str, message_id: str
) -> str | dict[str, Any]:
    """/ai plan — 任务分解到多维表格。"""
    log.info("handle_plan", description=description[:80])

    messages = [
        {
            "role": "system",
            "content": "你是项目经理。请将以下项目描述分解为可执行的任务列表。\n"
            "按格式输出:\n"
            "| TaskID | 任务名称 | 负责人 | 优先级 | 阶段 | 预计工时 |\n"
            "然后输出依赖关系和关键路径。",
        },
        {"role": "user", "content": f"请分解任务:\n{description}"},
    ]

    answer = await llm.chat(messages)
    return answer


async def handle_status(
    param: str, user_id: str, chat_id: str, message_id: str
) -> str | dict[str, Any]:
    """/ai status [task_id] — 查询任务状态。"""
    if param:
        task = await task_store.get_task(param)
        if not task:
            return f"⚠️ 未找到任务 `{param}`"
        return (
            f"**任务**: `{task['task_id']}`\n"
            f"**类型**: {task['type']}\n"
            f"**状态**: {task['status']}\n"
            f"**进度**: {int(task['progress'] * 100)}%\n"
            f"**创建时间**: {task['created_at']:.0f}\n"
            f"**更新时间**: {task['updated_at']:.0f}"
        )
    else:
        tasks = await task_store.list_tasks(user_id)
        if not tasks:
            return "暂无进行中的任务。"
        lines = []
        for t in tasks[:10]:
            status_emoji = {
                "pending": "⏳", "running": "🔄", "completed": "✅",
                "failed": "❌", "cancelled": "🚫",
            }
            emoji = status_emoji.get(t["status"], "❓")
            lines.append(f"{emoji} `{t['task_id']}` {t['type']}  [{int(t['progress']*100)}%]")
        return "\n".join(lines)


async def handle_help(
    _param: str, user_id: str, chat_id: str, message_id: str
) -> str | dict[str, Any]:
    """/ai help — 显示帮助信息。"""
    return help_card()


async def handle_chat(
    text: str, user_id: str, chat_id: str, message_id: str
) -> str | dict[str, Any]:
    """@机器人 自由对话（兜底）。"""
    log.info("handle_chat", text=text[:80])

    messages = [
        {
            "role": "system",
            "content": "你是服务器研发领域的 AI 助手。请回答用户的技术问题。"
            "使用中文，先给结论再展开。",
        },
        {"role": "user", "content": text},
    ]

    answer = await llm.chat(messages)
    return answer


# ── 注册所有指令处理器 ──────────────────────────────────────────────

def register_handlers() -> None:
    """将所有处理器注册到路由器。"""
    router.register(Intent.ASK, handle_ask)
    router.register(Intent.RESEARCH, handle_research)
    router.register(Intent.REVIEW, handle_review)
    router.register(Intent.DOC, handle_doc)
    router.register(Intent.ANALYZE, handle_analyze)
    router.register(Intent.SUMMARY, handle_summary)
    router.register(Intent.PLAN, handle_plan)
    router.register(Intent.STATUS, handle_status)
    router.register(Intent.HELP, handle_help)
    router.register(Intent.CHAT, handle_chat)
    log.info("all_handlers_registered")
