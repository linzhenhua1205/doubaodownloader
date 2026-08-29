"""路由器和卡片构建器的基础测试。"""

import pytest
from bot.router import COMMAND_PATTERNS, Intent


class TestRouterPatterns:
    """测试指令模式匹配。"""

    def test_ask_command(self):
        """/ai ask [问题]"""
        for pattern, intent in COMMAND_PATTERNS:
            m = pattern.match("/ai ask PCIe Gen6 retimer 的参数")
            if m and intent == Intent.ASK:
                assert m.group(1) == "PCIe Gen6 retimer 的参数"
                return
        pytest.fail("ASK pattern not matched")

    def test_research_command(self):
        """/ai research [topic]"""
        for pattern, intent in COMMAND_PATTERNS:
            m = pattern.match("/ai research 液冷散热方案")
            if m and intent == Intent.RESEARCH:
                assert m.group(1) == "液冷散热方案"
                return
        pytest.fail("RESEARCH pattern not matched")

    def test_help_command(self):
        """/ai help"""
        for pattern, intent in COMMAND_PATTERNS:
            m = pattern.match("/ai help")
            if m and intent == Intent.HELP:
                assert True
                return
        pytest.fail("HELP pattern not matched")

    def test_help_with_extra(self):
        """/ai help 带多余空格"""
        for pattern, intent in COMMAND_PATTERNS:
            m = pattern.match("/ai help  ")
            if m and intent == Intent.HELP:
                assert True
                return
        pytest.fail("HELP with spaces not matched")

    def test_status_with_id(self):
        """/ai status [task_id]"""
        for pattern, intent in COMMAND_PATTERNS:
            m = pattern.match("/ai status task-abc123")
            if m and intent == Intent.STATUS:
                assert m.group(1) == "task-abc123"
                return
        pytest.fail("STATUS with id pattern not matched")

    def test_status_alone(self):
        """/ai status（无参数）"""
        matched = False
        for pattern, intent in COMMAND_PATTERNS:
            m = pattern.match("/ai status")
            if m and intent == Intent.STATUS:
                matched = True
                break
        assert matched, "/ai status should match STATUS intent"

    def test_cancel_command(self):
        """/ai cancel [task_id]"""
        for pattern, intent in COMMAND_PATTERNS:
            m = pattern.match("/ai cancel task-abc123")
            if m and intent == Intent.CANCEL:
                assert m.group(1) == "task-abc123"
                return
        pytest.fail("CANCEL pattern not matched")

    def test_review_command(self):
        """/ai review [pr_id]"""
        for pattern, intent in COMMAND_PATTERNS:
            m = pattern.match("/ai review https://github.com/org/repo/pull/42")
            if m and intent == Intent.REVIEW:
                assert True
                return
        pytest.fail("REVIEW pattern not matched")

    def test_natural_language_fallback(self):
        """没有 /ai 前缀的消息不应匹配任何指令。"""
        for pattern, _intent in COMMAND_PATTERNS:
            m = pattern.match("PCIe Gen6 retimer 的参数是多少")
            if m:
                pytest.fail(f"Natural language should not match pattern: {pattern.pattern}")
