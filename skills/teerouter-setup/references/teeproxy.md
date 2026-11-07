# TeeProxy: model users

Authoritative references: [Releases](https://github.com/wangyi160/teeproxy/releases/latest),
[desktop guide](https://github.com/wangyi160/teeproxy/blob/main/docs/DESKTOP.en.md),
[attestation](https://github.com/wangyi160/teeproxy/blob/main/docs/ATTESTATION.en.md),
[user documentation](https://docs.teerouter.org/teeproxy/).
Checked against public v0.22.4. Inspect the selected release's notes when versions differ.

## Download and start

The published desktop package is Windows x64; do not promise a macOS/Linux GUI package.
For a Linux-only request, the repository documents a source-built CLI, but it requires
an already registered identity, signing seed and connection credentials. Downloading a
binary and inventing a random signing seed does not register a user.

1. Download the verified ZIP using `scripts/download_release.py teeproxy --download <dir>`.
2. Inspect ZIP entries and extract to a fresh directory in the user's chosen writable
   location. Keep the complete bundle. Locate `teeproxy.exe`; do not assume an archive root.
3. Start that executable once. On Windows launch background helpers hidden; the normal
   TeeProxy application window is the interface the user needs to interact with.
4. Portable settings, identities and policies live beside the executable in `data/`.
   The GUI owns `data/desktop.json` and encrypted identity/secret files. Do not fabricate
   the DPAPI payload or change those files while the application runs.

## Configure the GUI

Use Windows UI automation when available; otherwise guide the user through these exact pages.
Do not invent a local HTTP settings API for this native GUI.

| Page | Action |
| --- | --- |
| 我的账户 / My account | Select an existing local ID, or register one. Ordinary registration has no bonus. Google registration can receive the platform's current one-time reward; the UI shows eligibility and terms. Google verification remains a user action. |
| 连接与验证 / Connection and verification | Check platform/Router addresses and select the user's approved TDX or SNP policy. Save and verify. Existing signed-in addresses can be locked; do not discard identity data to change them. |
| Agent 接入 / Agent access | Keep `127.0.0.1:8899` unless the user requested otherwise. Generate or reuse a nonempty local API key, then save. Keys are 16–256 visible ASCII characters. Agent and TeeProxy must use the same value. |
| 账号池与模型 / Pools and models | Read the available pools and exact namespaced model IDs. Merely selecting a row does not apply a routing rule. |
| 路由策略 / Routing | Apply a fixed pool or automatic selection and retain the user's multiplier ceiling. The default ceiling is 1×; do not raise it to bypass a rejection. |
| 启动代理 / Start proxy | Start the listener after identity, API key and TEE configuration are ready. Confirm the running state in the UI. |

Only set `0.0.0.0`, a LAN address or a firewall rule when LAN access is requested.
Agents on another device use the server's actual address, never `0.0.0.0` or their own
loopback address. This local listener is HTTP, not HTTPS or an HTTP CONNECT proxy.
Do not point `HTTP_PROXY`/`HTTPS_PROXY` at TeeProxy or install a local CA.

## Validate and configure the agent

Use the local API key in a protected environment or an in-memory request header; do not
include it in logs or command-line arguments. Query `GET http://127.0.0.1:8899/v1/models`
with `Authorization: Bearer <local key>` (substitute the selected host/port). This confirms
the listener, local authentication and catalog only. TeeProxy has no public `/health`
endpoint. A local 401 means the Agent API key is missing/wrong; inspect where an error
originated before treating it as expired platform identity.

Read [Agent configuration](agents.md) and choose the exact catalog model ID:
Codex → `chatgpt/...`, Claude Code → `claude/...`, Grok Build → `grok/...`.
Other agents are not accepted by Router's current agent/provider policy. Do not disguise
an unsupported client with a forged User-Agent.

If the user asked for a working call, launch the selected native agent in an empty
temporary working directory and ask for a short Hello reply. Do not use a synthetic
`curl` generation call as a substitute for the real agent. Distinguish catalog success,
TEE verification and actual generation in the handoff.

## Common blockers

- **TEE policy failure:** keep verification enabled; check the reviewed policy against the
  intended release. Do not accept new measurements simply because the server returned them.
- **No matching pool:** inspect model prefix, availability, permissions, fixed pool and
  price ceiling. A list entry alone does not guarantee an available account at call time.
- **Balance exhausted:** show the client balance/recharge page; do not create a payment
  order unless the user requests one.
- **Interrupted request:** inspect the existing result/log before retrying. TeeProxy does
  not automatically replay forwarded requests; the upstream may already have consumed tokens.
- **Identity lost:** Google sign-in is not a replacement for a lost local private key.
  Preserve the original data and Windows decryption environment.
