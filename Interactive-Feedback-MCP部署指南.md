# Interactive Feedback MCP 部署指南

## 一、简介

Interactive Feedback MCP 是一个 MCP（Model Context Protocol）服务器，用于在 Cursor 等 AI 辅助开发工具中实现**人机交互反馈循环**。

**核心优势：**
- 💰 **节省 API 调用**：AI 在不确定时先向你提问，而非猜测执行，避免浪费高级请求配额
- ✅ **减少错误**：先确认再执行，减少错误代码和调试时间
- ⏱️ **加速迭代**：快速确认胜过调试错误猜测
- 🎮 **更好的协作**：将单向指令变为对话，保持你的控制权

---

## 二、前置要求

### Windows
- **操作系统**：Windows 10/11
- **Python**：3.11 或更新版本（uv 会自动下载管理）
- **uv**：Python 包管理器（已包含在 `C:\MCP\uv-x86_64-pc-windows-msvc\` 中）
- **Cursor**：已安装并正常运行

### macOS
- **操作系统**：macOS 12 Monterey 或更新版本
- **Python**：3.11 或更新版本（uv 会自动下载管理）
- **uv**：Python 包管理器（通过官方脚本安装）
- **Cursor**：已安装并正常运行

### Ubuntu / Linux
- **操作系统**：Ubuntu 18.04+ (含 SSH Remote 开发场景)
- **Python**：3.11 或更新版本（可通过 Miniconda 安装）
- **Cursor**：本地安装并通过 SSH Remote 连接（或本地运行）
- **网络**：能够访问 Python 包镜像源

---

## 三、Windows 安装步骤

### 步骤 1：复制 MCP 目录

将整个 `C:\MCP` 目录复制到你的电脑 `C:\MCP`，确保目录结构如下：

```
C:\MCP\
├── interactive-feedback-mcp\        # MCP 服务器代码
│   ├── server.py                    # 主服务器文件
│   ├── feedback_ui.py               # 反馈 UI 文件
│   ├── pyproject.toml               # 项目配置
│   ├── uv.lock                      # 依赖锁定文件
│   └── ...
└── uv-x86_64-pc-windows-msvc\      # uv 包管理器
    ├── uv.exe
    ├── uvw.exe
    └── uvx.exe
```

### 步骤 2：添加 uv 到系统 PATH

以管理员身份打开 PowerShell，运行以下命令将 `uv` 添加到用户环境变量：

```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\MCP\uv-x86_64-pc-windows-msvc", [EnvironmentVariableTarget]::User)
```

验证安装：**重新打开一个新的终端窗口**，运行：

```powershell
uv --version
```

应输出类似：`uv 0.9.27 (b5797b2ab 2026-01-26)`

### 步骤 3：安装 Python 依赖

在终端中运行：

```powershell
Set-Location C:\MCP\interactive-feedback-mcp
uv sync
```

等待依赖安装完成。首次运行时 uv 会自动下载 Python 3.11 并创建虚拟环境。

### 步骤 4：验证服务可启动

```powershell
uv --directory "C:/MCP/interactive-feedback-mcp" run server.py
```

如果看到类似以下输出，说明安装成功（按 `Ctrl+C` 终止）：

```
FastMCP x.x.x
Server: Interactive Feedback MCP
Starting MCP server 'Interactive Feedback MCP' with transport 'stdio'
```

### 步骤 5：配置 Cursor MCP

找到 Cursor 的 MCP 配置文件：`C:\Users\<你的用户名>\.cursor\mcp.json`

> 如果文件不存在，手动创建即可。

```json
{
  "mcpServers": {
    "interactive-feedback": {
      "command": "uv",
      "args": [
        "--directory",
        "C:/MCP/interactive-feedback-mcp",
        "run",
        "server.py"
      ],
      "timeout": 86400,
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

---

## 四、macOS 安装步骤

### 步骤 1：复制 MCP 目录

将 MCP 目录复制到 Mac 上，建议放在 `~/Project/MCP`（或任意你习惯的位置）：

```
/Users/<用户名>/Project/MCP/
├── interactive-feedback-mcp/
│   ├── server.py
│   ├── feedback_ui.py
│   ├── pyproject.toml
│   ├── uv.lock
│   └── ...
└── Interactive-Feedback-MCP部署指南.md
```

### 步骤 2：安装 uv 包管理器

在终端中运行官方安装脚本：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装完成后，使环境变量生效：

```bash
source $HOME/.local/bin/env
```

验证安装：

```bash
uv --version
```

应输出类似：`uv 0.10.9 (xxxx 2026-xx-xx)`

### 步骤 3：安装 Python 依赖

```bash
cd ~/Project/MCP/interactive-feedback-mcp
uv sync
```

首次运行时 uv 会自动下载 Python 3.11 并创建虚拟环境（`.venv/`）。PySide6 依赖较大（约 400MB），如果下载较慢可使用国内镜像：

```bash
UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ uv sync
```

### 步骤 4：验证服务可启动

```bash
~/Project/MCP/interactive-feedback-mcp/.venv/bin/python \
  ~/Project/MCP/interactive-feedback-mcp/server.py
```

应看到类似输出（按 `Ctrl+C` 终止）：

```
FastMCP x.x.x
Server: Interactive Feedback MCP
Starting MCP server 'Interactive Feedback MCP' with transport 'stdio'
```

### 步骤 5：配置 Cursor MCP

编辑 `~/.cursor/mcp.json`（如果不存在，手动创建）：

```json
{
  "mcpServers": {
    "interactive-feedback": {
      "command": "/Users/<用户名>/Project/MCP/interactive-feedback-mcp/.venv/bin/python",
      "args": [
        "/Users/<用户名>/Project/MCP/interactive-feedback-mcp/server.py"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "timeout": 86400,
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

> ⚠️ **重要**：macOS 下**不要使用 `uv run server.py`** 作为启动命令。`uv run` 每次启动需要解析依赖环境，开销较大，可能导致 MCP 初始化超时（60 秒内无法完成握手）。直接使用 `.venv/bin/python` 启动可在 1 秒内完成初始化。

---

## 五、Ubuntu / Linux 安装步骤

适用于 Ubuntu 18.04+ 环境，特别适合 Cursor SSH Remote 开发场景（无 sudo 权限也可操作）。

### 步骤 1：复制 MCP 目录

将 MCP 目录复制到 Linux 机器上，建议放在 `/home/<用户名>/MCP`：

```bash
# 目录结构
/home/<用户名>/MCP/
├── interactive-feedback-mcp/
│   ├── server.py
│   ├── feedback_ui.py
│   ├── pyproject.toml
│   └── ...
└── Interactive-Feedback-MCP部署指南.md
```

### 步骤 2：安装 Python 3.11+

如果系统 Python 版本低于 3.11（Ubuntu 18.04 默认 Python 3.6），使用 Miniconda 安装：

```bash
# 从清华镜像下载 Miniconda（兼容 glibc 2.27 的版本）
wget "https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py311_24.1.2-0-Linux-x86_64.sh" \
  -O /tmp/miniconda.sh

# 静默安装到用户目录（无需 sudo）
bash /tmp/miniconda.sh -b -p $HOME/miniconda3

# 验证
$HOME/miniconda3/bin/python3 --version
# 应输出: Python 3.11.7
```

> ⚠️ **注意**：最新版 Miniconda 需要 glibc >= 2.28。Ubuntu 18.04 (glibc 2.27) 请使用 `Miniconda3-py311_24.1.2-0` 版本。

### 步骤 3：创建虚拟环境并安装依赖

```bash
cd /home/<用户名>/MCP/interactive-feedback-mcp

# 使用 Miniconda 的 Python 创建虚拟环境
$HOME/miniconda3/bin/python3 -m venv .venv_linux

# 激活虚拟环境
source .venv_linux/bin/activate

# 使用国内镜像安装依赖
pip install fastmcp psutil -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> 💡 **PySide6 说明**：Linux SSH Remote 场景通常无 GUI 环境，PySide6 不是必需的。`server.py` 会优先使用 MCP Elicitation（在 Cursor 聊天窗口内联显示），仅在不支持时才 fallback 到 Qt GUI。

### 步骤 4：验证服务可启动

```bash
# 直接使用 venv 的 Python 运行
timeout 5 /home/<用户名>/MCP/interactive-feedback-mcp/.venv_linux/bin/python \
  /home/<用户名>/MCP/interactive-feedback-mcp/server.py
```

应看到类似输出：

```
FastMCP 3.1.0
Server: Interactive Feedback MCP
Starting MCP server 'Interactive Feedback MCP' with transport 'stdio'
```

### 步骤 5：配置 Cursor MCP

编辑 `~/.cursor/mcp.json`（SSH Remote 场景下此文件在远程机器上）：

```json
{
  "mcpServers": {
    "interactive-feedback": {
      "command": "/home/<用户名>/MCP/interactive-feedback-mcp/.venv_linux/bin/python",
      "args": [
        "/home/<用户名>/MCP/interactive-feedback-mcp/server.py"
      ],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      },
      "timeout": 86400,
      "autoApprove": [
        "interactive_feedback"
      ]
    }
  }
}
```

> ⚠️ **关键差异**：Linux 下直接使用 venv 的 Python 解释器路径作为 `command`，无需 uv。

---

## 六、配置全局规则（User Rules）— 必须步骤

> **重要**: 此步骤是部署流程的**必要组成部分**，不是可选项。不配置 User Rules，AI 将不会主动调用 interactive_feedback 工具，MCP 安装等于无效。

### 适用于 Windows、macOS 和 Linux

1. 打开 Cursor
2. 点击右上角 **齿轮图标** → 选择 **Cursor Settings**（Windows/Linux 按 `Ctrl+Shift+J`，macOS 按 `Cmd+Shift+J`）
3. 在左侧菜单找到 **General** → **Rules for AI**
4. 在 **User Rules** 文本框中，添加以下规则（中英双语确保不同模型都能理解）：

```
如果要求或指令不明确，在继续操作之前使用interactive_feedback工具向用户询问澄清问题，不要做出假设。
尽可能通过interactive_feedback MCP工具向用户提供预定义的选项，以促进快速决策。 每当即将完成用户请求时，调用interactive_feedback工具在结束流程前请求用户反馈。如果反馈为空，则可以结束请求，并且不要循环调用该工具。

If requirements or instructions are unclear use the tool interactive_feedback to ask clarifying questions to the user before proceeding, do not make assumptions. Whenever possible, present the user with predefined options through the interactive_feedback MCP tool to facilitate quick decisions.
Whenever you're about to complete a user request, call the interactive_feedback tool to request user feedback before ending the process. If the feedback is empty you can end the request and don't call the tool in loop.
```

> 💡 如果你的项目已有 `.cursor/rules/` 配置文件，也可以将上述规则合并到项目规则中，这样不需要单独配置 User Rules。

> **验证方法**: 配置完成后，在 AI 对话中输入 "帮我写一个脚本"。AI 应当调用 `interactive_feedback` 工具（在聊天窗口内联显示选项），而不是直接猜测执行。

---

## 七、验证 MCP 连接

1. 重启 Cursor（或重新加载窗口：Windows/Linux `Ctrl+Shift+P`，macOS `Cmd+Shift+P` → 搜索 `Reload Window`）
2. 打开 Cursor Settings → MCP 页面
3. 确认 `interactive-feedback` 显示为绿色（已连接状态）
4. 如果显示红色或未连接，点击旁边的刷新按钮重试

---

## 八、使用测试

配置完成后，在 Cursor 的 AI 对话中输入一个模糊的请求进行测试，例如：

```
帮我写一个脚本
```

AI 应当调用 `interactive_feedback` 工具向你询问更多细节，而不是直接猜测执行。

---

## 九、故障排除

### 通用问题

#### 问题 1：MCP 显示红色/未连接
**可能原因及解决方案**：
1. 点击 MCP 旁的刷新按钮重试
2. 检查 `mcp.json` 格式是否正确（JSON 语法错误会导致加载失败）
3. 手动运行服务器命令测试

#### 问题 2：FastMCP 版本兼容性
不同版本的 fastmcp API 可能有变化。如果遇到 `FastMCP() no longer accepts log_level` 之类的错误：
- 修改 `server.py`，将 `log_level="ERROR"` 从 `FastMCP()` 构造函数中移除
- 改为在环境变量中设置：`FASTMCP_LOG_LEVEL=ERROR`

### Windows 专用

#### 问题：uv 命令未找到
```powershell
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\MCP\uv-x86_64-pc-windows-msvc", [EnvironmentVariableTarget]::User)
```
添加后**重新打开终端**。

#### 问题：依赖安装失败
```powershell
Set-Location C:\MCP\interactive-feedback-mcp
uv sync
```

### macOS 专用

#### 问题：MCP 初始化超时（Request timed out）
**根本原因**：使用 `uv run server.py` 作为启动命令时，`uv run` 每次启动需要解析依赖环境，可能耗时超过 Cursor 的 60 秒超时限制。

**解决方案**：在 `mcp.json` 中改用 `.venv/bin/python` 直接启动：
```json
{
  "command": "/Users/<用户名>/Project/MCP/interactive-feedback-mcp/.venv/bin/python",
  "args": ["/Users/<用户名>/Project/MCP/interactive-feedback-mcp/server.py"]
}
```

#### 问题：PySide6 下载慢
PySide6 依赖约 400MB，默认从 PyPI 下载可能很慢。使用国内镜像加速：
```bash
UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ uv sync
```

#### 问题：uv 命令未找到
安装 uv 后需要加载环境变量：
```bash
source $HOME/.local/bin/env
```
也可将此行添加到 `~/.zshrc` 或 `~/.bash_profile` 中永久生效。

### Linux / Ubuntu 专用

#### 问题：glibc 版本不满足
Ubuntu 18.04 (glibc 2.27) 使用旧版 Miniconda：
```bash
wget "https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py311_24.1.2-0-Linux-x86_64.sh" \
  -O /tmp/miniconda.sh
bash /tmp/miniconda.sh -b -p $HOME/miniconda3
```

#### 问题：pip 安装超时
使用国内镜像源：
```bash
pip install <包名> -i https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 问题：SSH Remote 环境无 GUI
这是正常的。MCP server 会使用 Elicitation API 在 Cursor 聊天窗口内联显示交互界面，不需要 GUI 环境。PySide6 依赖可以不安装。

---

## 十、目录结构说明

| 平台 | 文件/目录 | 说明 |
|-------|-----------|------|
| 通用 | `interactive-feedback-mcp/server.py` | MCP 服务器主文件 |
| 通用 | `interactive-feedback-mcp/feedback_ui.py` | 备用 Qt GUI 反馈界面 |
| 通用 | `interactive-feedback-mcp/pyproject.toml` | 项目依赖配置 |
| Windows | `interactive-feedback-mcp/.venv/` | Windows Python 虚拟环境 |
| macOS | `interactive-feedback-mcp/.venv/` | macOS Python 虚拟环境（uv 自动创建） |
| Linux | `interactive-feedback-mcp/.venv_linux/` | Linux Python 虚拟环境 |
| Windows | `uv-x86_64-pc-windows-msvc/uv.exe` | Windows uv 包管理器 |
| macOS | `~/.local/bin/uv` | macOS uv 包管理器（官方脚本安装） |
| Linux | `~/miniconda3/` | Miniconda Python 环境 |
| Windows | `C:\Users\<用户名>\.cursor\mcp.json` | Cursor MCP 配置文件 |
| macOS | `~/.cursor/mcp.json` | Cursor MCP 配置文件 |
| Linux | `~/.cursor/mcp.json` | Cursor MCP 配置文件 |

---

## 十一、快速检查清单

### Windows
- [ ] `C:\MCP\interactive-feedback-mcp\` 目录存在
- [ ] `C:\MCP\uv-x86_64-pc-windows-msvc\uv.exe` 存在
- [ ] 终端中 `uv --version` 能正常输出版本号
- [ ] `uv sync` 在项目目录中执行成功
- [ ] `C:\Users\<用户名>\.cursor\mcp.json` 已正确配置
- [ ] Cursor Settings → General → Rules for AI 中已添加规则
- [ ] Cursor 中 MCP 页面显示 `interactive-feedback` 为绿色已连接

### macOS
- [ ] MCP 项目目录存在（如 `~/Project/MCP/interactive-feedback-mcp/`）
- [ ] uv 已安装（`uv --version` 能正常输出）
- [ ] `uv sync` 在项目目录中执行成功，`.venv/` 已创建
- [ ] 手动运行 `.venv/bin/python server.py` 能正常启动
- [ ] `~/.cursor/mcp.json` 已正确配置（使用 `.venv/bin/python` 绝对路径，**不要用 `uv run`**）
- [ ] Cursor Settings → General → Rules for AI 中已添加规则（或合并到项目规则）
- [ ] Cursor 中 MCP 页面显示 `interactive-feedback` 为绿色已连接
- [ ] **验证测试**: 输入模糊请求，AI 通过 `interactive_feedback` MCP 工具询问

### Ubuntu / Linux
- [ ] `/home/<用户名>/MCP/interactive-feedback-mcp/` 目录存在
- [ ] Python 3.11+ 可用（`$HOME/miniconda3/bin/python3 --version`）
- [ ] `.venv_linux` 虚拟环境已创建且 fastmcp 已安装
- [ ] 手动运行 `server.py` 能正常启动
- [ ] `~/.cursor/mcp.json` 已正确配置（使用绝对路径）
- [ ] **Cursor Settings → General → Rules for AI 中已添加 User Rules（必须！）**
- [ ] Cursor 中 MCP 页面显示 `interactive-feedback` 为绿色已连接
- [ ] **验证测试**: 输入模糊请求，AI 通过 `interactive_feedback` MCP 工具询问
