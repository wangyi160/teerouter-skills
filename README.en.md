# TeeRouter Skills

[简体中文](README.md) | **English**

An open-source Agent Skill for downloading and configuring **TeeProxy** and **TeeMerchant**.
It helps an assistant select official releases, verify downloads, preserve portable data,
configure identities and TEE policies, and connect a supported native model agent.

## Install

With the [Skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add wangyi160/teerouter-skills --skill teerouter-setup
```

Choose the target agent when prompted. Installation is project-scoped by default; add
`-g` for a user-scoped installation. See the CLI documentation for its Node.js requirements.
If Windows PowerShell blocks `npx.ps1`, use `npx.cmd` without changing the system execution policy.
Alternatively, copy the complete `skills/teerouter-setup` folder into your agent's supported
skills directory. Other assistants can read `SKILL.md` and its linked references directly.
Some hosts require a new session to discover an installed skill.

Example requests:

> Use teerouter-setup to install TeeProxy on Windows and connect Codex, preserving my existing configuration.

> Install TeeMerchant and help me publish a Grok account pool. I will complete official OAuth consent myself.

> Upgrade TeeProxy while retaining my local identity, API key, policy and data directory.

Codex can invoke it as `$teerouter-setup`; discovery and invocation depend on the host.
Agents with UI automation can operate the client. Others prepare downloads/configuration
and identify the remaining UI action without claiming an unattended setup succeeded.

## Scope

- TeeProxy: Windows x64 portable GUI. Connect Codex, Claude Code or Grok Build with the
  correct native protocol and an exact model ID from the catalog.
- TeeMerchant: Windows/Linux x64 portable service; Linux needs glibc 2.36+. Its web UI is
  loopback-only. Manage official accounts, per-account proxies, OAuth/JSON import and pools.
- Existing identities, approved policies, API keys and user configuration are preserved.
- Google/provider login and consent remain user actions. No credentials are bundled.
- An independently accepted TEE policy is required; an empty example cannot authorize a Router.
- A model test can incur usage charges. Payments, withdrawals and raising price ceilings
  are not default installation steps.

An agent's ability to load this skill does not mean Router accepts that agent as a model
client. Router currently matches Codex→ChatGPT, Claude Code→Claude and Grok Build→Grok.

## Download helper

Python 3.10+, standard library only:

```sh
python skills/teerouter-setup/scripts/download_release.py teeproxy
python skills/teerouter-setup/scripts/download_release.py teeproxy --download ./downloads
python skills/teerouter-setup/scripts/download_release.py teemerchant --platform linux-x64 --download ./downloads
```

Without `--download`, the script only reads release metadata. `--version vX.Y.Z` selects
a stable tag. Downloads are checked against GitHub's SHA-256 digest or the release's
checksum file; conflicting existing files are not overwritten. It never executes an
archive or accesses platform accounts. Standard HTTPS proxy environment settings apply.
Checksum verification is not a substitute for TEE attestation or a source-code audit.
The agent may use native download/hash tools if Python is unavailable.

Run the helper's behavioral tests with `python -m unittest discover -s tests -v`.
The skill follows the [Agent Skills format](https://agentskills.io/specification).

## Links

[Website](https://teerouter.org) · [Documentation](https://docs.teerouter.org/?lang=en) ·
[TeeProxy](https://github.com/wangyi160/teeproxy) · [TeeMerchant](https://github.com/wangyi160/teemerchant) ·
[Telegram](https://t.me/teerouter) · [Discord](https://discord.gg/ssH4KvKhxB)

MIT licensed. This repository contains setup instructions and a download helper, not
Router deployment configuration, private keys, client identities or account databases.
