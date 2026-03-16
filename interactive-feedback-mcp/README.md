# Interactive Feedback MCP

A [MCP Server](https://modelcontextprotocol.io/) that enables human-in-the-loop workflow in AI-assisted development tools like [Cursor](https://www.cursor.com). The server uses MCP Elicitation to display feedback forms **inline within the chat interface** — no popup windows needed.

一个 [MCP 服务器](https://modelcontextprotocol.io/)，为 [Cursor](https://www.cursor.com) 等 AI 辅助开发工具提供人机交互反馈能力。通过 MCP Elicitation 协议，反馈表单**直接在对话界面内联显示**，无需弹出窗口。

## Why Use This? / 为什么使用？

In Cursor, every prompt counts against your monthly limit (e.g. 500 premium requests). When iterating on vague instructions, each follow-up clarification triggers a full new request.

在 Cursor 中，每次发送 prompt 都会消耗月度配额（如 500 次高级请求）。当需求不明确反复沟通时，每次追问都算一次新请求。

This MCP server lets the model **pause and ask for clarification** before finalizing the response. The model triggers `interactive_feedback` which displays an inline form in the chat. You provide feedback, and the model continues — all within a single request.

本工具让模型在完成回复前**暂停并请求澄清**。模型调用 `interactive_feedback`，在对话中显示内联表单，你提供反馈后模型继续执行——全程只消耗一次请求。

### Use Cases / 使用场景

- **Clarify before acting / 行动前澄清** — Model asks for details when requirements are ambiguous, instead of guessing.
  模型在需求模糊时主动提问，而不是猜测。

- **Confirm before modifying / 修改前确认** — Model presents its plan and waits for approval before changing code.
  模型展示方案并等待批准后再修改代码。

- **Multi-option decision / 多选项决策** — Model offers predefined options for quick choices (e.g. which approach to use).
  模型提供预定义选项便于快速决策（如选择实现方案）。

- **Post-task feedback / 任务完成后反馈** — Model checks if you need anything else before ending the session.
  模型在结束前确认是否还有其他需要。

### Benefits / 优势

- **Fewer wasted requests / 减少请求浪费** — Multiple feedback rounds in a single request.
  一次请求内完成多轮反馈。

- **Fewer errors / 减少错误** — Clarification before action means less incorrect code.
  先澄清再执行，减少错误代码。

- **Faster iterations / 更快迭代** — Quick confirmations beat debugging wrong guesses.
  快速确认优于调试错误猜测。

- **Better collaboration / 更好协作** — Turns one-way instructions into a dialogue.
  将单向指令变为双向对话。

## Tool / 工具

This server exposes one tool via MCP:

- `interactive_feedback` — Asks the user a question inline in the chat. Supports predefined options for quick selection and free-text input.

### Parameters / 参数

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | `str` | Yes | The question to display to the user / 向用户展示的问题 |
| `predefined_options` | `list` | No | Predefined options for quick selection / 预定义选项供快速选择 |

### Features / 特性

- **Concurrent-safe / 并发安全** — Each tool call runs independently with its own Context. No global state or preemptive cancellation. Multiple conversations can call `interactive_feedback` simultaneously without interfering.
  每次调用独立运行，拥有独立 Context，无全局状态或抢占取消。多个对话可同时调用而互不干扰。

- **No timeout / 无超时** — Waits indefinitely for user response. Heartbeats keep the connection alive so the dialog stays open regardless of how long the user takes.
  无限等待用户响应。心跳机制保持连接存活，无论用户花多长时间对话框都不会消失。

- **Qt UI Fallback / Qt 弹窗降级** — If MCP Elicitation is unavailable (e.g. the client doesn't support it), the tool automatically falls back to a standalone Qt feedback window.
  当 MCP Elicitation 不可用时（如客户端不支持），自动降级为独立 Qt 弹窗。

- **Response States / 响应状态** — Handles three elicitation outcomes:
  处理三种 elicitation 结果：
  - `AcceptedElicitation` — User submitted feedback / 用户提交了反馈
  - `DeclinedElicitation` — User declined to respond / 用户拒绝响应
  - `CancelledElicitation` — User cancelled the dialog / 用户取消了对话

## Installation / 安装

### Prerequisites / 前置条件

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Python package manager)
  - macOS: `brew install uv`
  - Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Windows: `pip install uv`

### Setup / 配置

1. Clone the repository / 克隆仓库:

```bash
git clone https://github.com/pauoliva/interactive-feedback-mcp.git
```

2. Add to your Cursor MCP config (`mcp.json`), update the path accordingly / 添加到 Cursor MCP 配置，修改路径:

```json
{
  "mcpServers": {
    "interactive-feedback": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/interactive-feedback-mcp",
        "run",
        "server.py"
      ],
      "timeout": 600,
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

3. Add to your Cursor Rules (Settings > Rules > User Rules) / 添加到 Cursor 规则:

> If requirements or instructions are unclear, use the interactive_feedback tool to ask clarifying questions before proceeding. Present predefined options when possible for quick decisions. After completing a task, call interactive_feedback to check if the user needs anything else. If feedback is empty, end the request without looping.

## Acknowledgements / 致谢

Based on [interactive-feedback-mcp](https://github.com/poliva/interactive-feedback-mcp) by Fábio Ferreira ([@fabiomlferreira](https://x.com/fabiomlferreira)), enhanced by Pau Oliva ([@pof](https://x.com/pof)) with ideas from Tommy Tong's [interactive-mcp](https://github.com/ttommyth/interactive-mcp).

Modified to use MCP Elicitation for inline display in Cursor chat.
