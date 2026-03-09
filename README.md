# Interactive Feedback MCP

基于 [poliva/interactive-feedback-mcp](https://github.com/poliva/interactive-feedback-mcp) 的定制部署版本，支持 **Windows**、**macOS** 和 **Ubuntu/Linux** 三平台开箱即用。

## 核心功能

Interactive Feedback MCP 是一个 MCP（Model Context Protocol）服务器，让 Cursor 等 AI 辅助开发工具在不确定时**先向你提问，而非猜测执行**。

- 💰 **节省 API 调用** — 通过 tool call 循环避免消耗额外的高级请求配额
- ✅ **减少错误** — 先确认再执行，减少错误代码和调试时间
- ⏱️ **加速迭代** — 快速确认胜过调试错误猜测
- 🎮 **更好的协作** — 将单向指令变为对话，保持你的控制权

## 快速开始

详细的安装和配置步骤请参阅 **[部署指南](Interactive-Feedback-MCP部署指南.md)**，包括：

- 各平台的安装步骤（Windows / macOS / Ubuntu）
- Cursor MCP 配置
- User Rules 配置
- 故障排除

## 目录结构

```
.
├── README.md                           # 本文件
├── Interactive-Feedback-MCP部署指南.md  # 三平台部署指南
├── interactive-feedback-mcp/           # MCP 服务器代码
│   ├── server.py                       # 主服务器文件
│   ├── feedback_ui.py                  # 备用 Qt GUI 反馈界面
│   ├── pyproject.toml                  # 项目依赖配置
│   └── ...
└── uv-x86_64-pc-windows-msvc/         # Windows uv 包管理器
    └── uv.exe / uvw.exe / uvx.exe
```

## 致谢

- [Fábio Ferreira](https://x.com/fabiomlferreira) — 原始开发
- [Pau Oliva](https://x.com/pof) — 增强版开发
- [Tommy Tong](https://github.com/ttommyth/interactive-mcp) — 灵感来源
