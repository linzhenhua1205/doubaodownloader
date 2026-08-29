# workflow/lib/ — 共享运行时辅助

> 供静态/动态 workflow 复用的轻量运行时（phase/log/assert/state）。

| 模块 | 职责 | 状态 |
|:-----|:-----|:----:|
| `phase.py` | 阶段声明 + 进度记录（progress.json） | 🟡 待建 |
| `log.py` | 结构化日志（phase + 结果摘要） | 🟡 待建 |
| `assert_check.py` | 调用 check 脚本返回布尔信号（驱动分支） | 🟡 待建 |
| `state.py` | 中间状态读写（workflow/.state/） | 🟡 待建 |

> P1 阶段实现。静态 workflow（wf-03/wf-04）脚本化时一并落地。
