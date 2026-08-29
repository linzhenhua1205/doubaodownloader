#!/usr/bin/env python3
"""
errorcodes.py — 工程通用错误码标准

基于 sr-006 X-11 建议，定义所有脚本的标准化退出码。
其他脚本应: `from scripts.tools.errorcodes import EC, exit_with`

退出码范围:
  0         成功
  1-9       通用
  10-19     搜索相关
  20-29     文件I/O
  30-39     数据/内容
  40-49     配置/参数
  50-59     外部依赖
  60-69     约束/合规
  70-79     定时任务
  80-89     质量/检查
  90-99     保留

使用示例:
  from scripts.tools.errorcodes import EC, exit_with
  exit_with(EC.SUCCESS)
  exit_with(EC.NO_OUTPUT, "未找到有效信息")
"""
import sys

class ErrorCode:
    """错误码枚举类（纯数字，便于脚本链式调用判断）"""
    # ── 成功 ──
    SUCCESS = 0          # 完全成功

    # ── 通用 1-9 ──
    GENERAL_ERR = 1      # 通用错误（未分类）
    NO_OUTPUT = 2        # 执行成功但无产出
    PARTIAL_FAIL = 3     # 部分失败
    USER_ABORT = 4       # 用户中断/跳过
    TIMEOUT = 5          # 超时

    # ── 搜索 10-19 ──
    SEARCH_NO_RESULT = 10    # 搜索无结果
    SEARCH_SOURCE_FAIL = 11  # 搜索源不可用
    SEARCH_RATE_LIMIT = 12   # 频率限制
    SEARCH_CACHED = 13       # 命中缓存无更新

    # ── 文件 I/O 20-29 ──
    FILE_NOT_FOUND = 20      # 文件不存在
    FILE_READ_ERR = 21       # 读取失败
    FILE_WRITE_ERR = 22      # 写入失败
    FILE_MOVE_ERR = 23       # 移动失败
    DIR_NOT_FOUND = 24       # 目录不存在
    DUPLICATE = 25           # 目标已存在（去重命中）

    # ── 数据/内容 30-39 ──
    DATA_INVALID = 30        # 数据格式错误
    DATA_EMPTY = 31          # 数据为空
    DATA_INCOMPLETE = 32     # 数据不完整
    CONTENT_LOW_QUALITY = 33 # 内容质量不达标

    # ── 配置/参数 40-49 ──
    INVALID_ARGS = 40        # 参数错误
    MISSING_ARG = 41         # 缺少必选参数
    CONFIG_ERR = 42          # 配置错误
    ENV_MISSING = 43         # 环境变量缺失

    # ── 外部依赖 50-59 ──
    API_ERR = 50             # API 调用失败
    NETWORK_ERR = 51         # 网络错误
    DEP_MISSING = 52         # 依赖缺失（如未安装的包/工具）
    AUTH_ERR = 53            # 鉴权失败

    # ── 约束/合规 60-69 ──
    CONSTRAINT_VIOLATION = 60  # 约束违规
    FORMAT_ERR = 61            # 格式不规范
    LINK_BROKEN = 62           # 链接损坏
    INDEX_MISSING = 63         # index/log 缺失

    # ── 定时任务 70-79 ──
    TASK_FAIL = 70             # 任务执行失败
    TASK_EMPTY = 71            # 任务空产出
    TASK_STALE = 72            # 任务过期未执行
    TASK_DEGRADED = 73         # 任务降级执行

    # ── 质量/检查 80-89 ──
    QA_FAIL = 80               # 质量检查不通过
    QA_WARN = 81               # 质量检查警告
    COVERAGE_LOW = 82          # 覆盖率不足

    # ── 描述映射 ──
    _DESCRIPTIONS = {
        0:  "SUCCESS",
        1:  "GENERAL_ERR", 2:  "NO_OUTPUT", 3:  "PARTIAL_FAIL",
        4:  "USER_ABORT", 5:  "TIMEOUT",
        10: "SEARCH_NO_RESULT", 11: "SEARCH_SOURCE_FAIL",
        12: "SEARCH_RATE_LIMIT", 13: "SEARCH_CACHED",
        20: "FILE_NOT_FOUND", 21: "FILE_READ_ERR", 22: "FILE_WRITE_ERR",
        23: "FILE_MOVE_ERR", 24: "DIR_NOT_FOUND", 25: "DUPLICATE",
        30: "DATA_INVALID", 31: "DATA_EMPTY", 32: "DATA_INCOMPLETE",
        33: "CONTENT_LOW_QUALITY",
        40: "INVALID_ARGS", 41: "MISSING_ARG", 42: "CONFIG_ERR",
        43: "ENV_MISSING",
        50: "API_ERR", 51: "NETWORK_ERR", 52: "DEP_MISSING", 53: "AUTH_ERR",
        60: "CONSTRAINT_VIOLATION", 61: "FORMAT_ERR", 62: "LINK_BROKEN",
        63: "INDEX_MISSING",
        70: "TASK_FAIL", 71: "TASK_EMPTY", 72: "TASK_STALE",
        73: "TASK_DEGRADED",
        80: "QA_FAIL", 81: "QA_WARN", 82: "COVERAGE_LOW",
    }

    @classmethod
    def describe(cls, code: int) -> str:
        return cls._DESCRIPTIONS.get(code, f"UNKNOWN_{code}")

    @classmethod
    def is_success(cls, code: int) -> bool:
        return code == 0

    @classmethod
    def is_retryable(cls, code: int) -> bool:
        """是否可重试（网络/API/超时等临时故障）"""
        return code in (5, 11, 12, 50, 51, 53, 70)

    @classmethod
    def is_output_issue(cls, code: int) -> bool:
        """产出相关的非致命问题"""
        return code in (2, 10, 13, 31, 71, 72)

    @classmethod
    def is_fatal(cls, code: int) -> bool:
        """致命错误，需人工介入"""
        return code in (20, 24, 30, 40, 42, 43, 60)


EC = ErrorCode  # 简短别名


def exit_with(code: int, message: str = "", *, silent: bool = False):
    """
    退出脚本，输出结构化信息。
    
    参数:
        code:    错误码（来自 EC）
        message: 附加说明
        silent:  为 True 时不打印任何信息
    """
    name = EC.describe(code)
    if not silent:
        if code == 0:
            print(f"✅ [{name}] {message}" if message else f"✅ [{name}]")
        elif code in (2, 10, 13, 31, 71):
            print(f"⚠️  [{name}] {message}" if message else f"⚠️  [{name}]")
        else:
            print(f"❌ [{name}] {message}" if message else f"❌ [{name}]")
    sys.exit(code)


if __name__ == "__main__":
    # 简单自测
    print("ErrorCode 标准退出码:")
    print(f"  SUCCESS      = {EC.SUCCESS}  — 完全成功")
    print(f"  NO_OUTPUT    = {EC.NO_OUTPUT}  — 执行成功但无产出")
    print(f"  PARTIAL_FAIL = {EC.PARTIAL_FAIL}  — 部分失败")
    print(f"  SEARCH_NO_RESULT = {EC.SEARCH_NO_RESULT}")
    print(f"  INVALID_ARGS = {EC.INVALID_ARGS}")
    print(f"  TASK_STALE   = {EC.TASK_STALE}")
    print(f"可重试码: {[c for c in range(100) if EC.is_retryable(c)]}")
    print(f"产出问题码: {[c for c in range(100) if EC.is_output_issue(c)]}")
    print(f"致命码: {[c for c in range(100) if EC.is_fatal(c)]}")
    exit_with(EC.SUCCESS, "自测通过")
