# TeeRouter Skills

**简体中文** | [English](README.en.md)

让支持 Agent Skills 的编程助手，帮助用户下载和配置 **TeeProxy** 或 **TeeMerchant**。
这是独立的开源安装配置指南与辅助工具，采用 MIT 许可。

- 使用模型：安装 TeeProxy，注册或使用本地 ID，配置 TEE 信任策略、本地 API key 和路由，再接入 Codex、Claude Code 或 Grok Build。
- 提供账号：安装 TeeMerchant，注册商户 ID，配置账号代理，通过官方 OAuth 或 JSON 添加账号，测试并发布账号池。
- 升级客户端：先检查现有安装和运行状态，保留身份、账号库和整个 `data/` 目录。

## 安装 Skill

使用 [Skills CLI](https://github.com/vercel-labs/skills) 安装，按提示选择 Agent：

```sh
npx skills add wangyi160/teerouter-skills --skill teerouter-setup
```

默认安装到当前项目；添加 `-g` 可安装到用户范围。Skills CLI 的 Node.js 版本要求以其官方文档为准。
Windows PowerShell 若阻止 `npx.ps1`，改用 `npx.cmd`，不需要更改系统执行策略。
也可以克隆仓库，将完整的 [`skills/teerouter-setup`](skills/teerouter-setup) 文件夹复制到 Agent 支持的 skills 目录。
不支持 Skills 的助手，可以阅读其中的 `SKILL.md` 和按需引用的文档。

安装的是 Agent 的操作能力，客户端仍由 Agent 按你的要求下载。
有些宿主需要重新加载会话才能发现新 Skill。

## 怎么用

对 Agent 说：

> 使用 teerouter-setup，帮我在 Windows 安装 TeeProxy，把 Codex 配置到本地端点。保留我现有的 Codex 配置。

> 帮我安装 TeeMerchant，创建一个 Grok 账号池。我会自行完成官方 OAuth 授权。

> 使用 teerouter-setup 升级现有 TeeProxy，保留我的本地身份、API key、信任策略和数据目录。

Codex 中也可以用 `$teerouter-setup` 显式调用。具体发现和调用方式由 Agent 宿主决定。
有 UI 自动化能力的 Agent 可以操作客户端；没有时，会完成可执行的文件与配置步骤，明确说明剩余的界面操作。

## 能做什么

| 步骤 | 行为 |
| --- | --- |
| 选择发行包 | 从官方 GitHub Releases 读取最新稳定版本，根据系统选择包，也支持指定版本 |
| 下载校验 | 只使用 `wangyi160/teeproxy` 与 `wangyi160/teemerchant`；下载后核对 SHA-256，拒绝覆盖不匹配的文件 |
| 配置客户端 | 区分用户与商户，保留已有身份和设置，使用便携数据目录 |
| 连接模型工具 | 为 Codex / Claude Code / Grok Build 配置各自原生接口，使用目录中的真实模型 ID |
| 验收 | 分别确认本地服务、身份、TEE、模型目录和实际调用结果，不把读到目录当成调用成功 |

Google 登录、供应商 OAuth 与授权确认由用户在官方页面完成。
TEE 需要用户认可的信任策略；示例空策略不能直接用于接入，Skill 不会自动信任未知服务器的度量值。
模型测试可能产生费用；充值、提现、提高倍率上限不属于默认安装步骤。

当前发行包支持 TeeProxy Windows x64，以及 TeeMerchant Windows/Linux x64。
Linux TeeMerchant 要求 glibc 2.36+，仅允许本机回环访问。
能运行 Skill 的 Agent，和 Router 接受的模型调用客户端，是两个不同的范围。

## 下载辅助工具

辅助脚本仅需 Python 3.10+ 标准库，不需要平台账号或 GitHub token。
它只下载并校验，不会执行客户端、注册身份、改动系统代理或读取本地凭据。

```sh
# 查询最新版本；无文件写入
python skills/teerouter-setup/scripts/download_release.py teeproxy

# 下载并校验到指定目录
python skills/teerouter-setup/scripts/download_release.py teeproxy --download ./downloads
python skills/teerouter-setup/scripts/download_release.py teemerchant --download ./downloads

# 只为指定系统下载，或固定发行版本
python skills/teerouter-setup/scripts/download_release.py teemerchant --platform linux-x64 --download ./downloads
python skills/teerouter-setup/scripts/download_release.py teeproxy --version v0.22.4 --download ./downloads
```

没有 Python 时，Agent 仍可使用操作系统的下载、解压和哈希校验工具。
辅助工具遵循标准 `HTTPS_PROXY` 环境设置；这些是访问 GitHub 的网络设置，不是 TeeProxy 的本地 Agent 端点。
校验和用于验证发行包完整性，不能代替 TEE 验证或独立代码审计。

## 开发与校验

```sh
python -m unittest discover -s tests -v
```

Skill 使用标准 [`SKILL.md` 格式](https://agentskills.io/specification)。
更新客户端流程时，应核对真实发行包、公开文档、接口差异与身份保存方式。
测试下载和解压使用临时目录，不能覆盖正在使用的客户端或提交其 `data/`。

## 链接

[官网](https://teerouter.org) · [文档](https://docs.teerouter.org) ·
[TeeProxy](https://github.com/wangyi160/teeproxy) · [TeeMerchant](https://github.com/wangyi160/teemerchant) ·
[Telegram](https://t.me/teerouter) · [Discord](https://discord.gg/ssH4KvKhxB)

中文视频：[项目介绍](https://youtu.be/-hoaz4fVxqU) ·
[TeeProxy 教程](https://youtu.be/_JN1GC5L3fA) · [TeeMerchant 教程](https://youtu.be/bvcw9qD-wRw)
