# Connect a native agent to TeeProxy

First confirm TeeProxy is running, authenticated and configured with the user's accepted
TEE policy. Select an exact ID from its model catalog; examples below are placeholders.
The agent's model provider must match: Codex → ChatGPT, Claude Code → Claude,
Grok Build → Grok. Skill support in an editor does not imply that editor's own model
requests are accepted by Router.

Default endpoints:

| Agent | Base URL | Protocol |
| --- | --- | --- |
| Codex | `http://127.0.0.1:8899/v1` | Responses / SSE |
| Claude Code | `http://127.0.0.1:8899` | Anthropic Messages |
| Grok Build | `http://127.0.0.1:8899/v1` | Responses / SSE |

Use the user's actual host/port and the same nonempty local API key saved in TeeProxy.
This is not the upstream provider's API key and not a platform connection token. Keep it
out of committed files and command-line arguments. Preserve unrelated HTTP proxy settings;
if needed, merge loopback addresses into `NO_PROXY` rather than replacing the whole value.

## Codex

Inspect the installed Codex version/config first. Merge these tables into its selected
configuration (normally `~/.codex/config.toml`, or the user's `CODEX_HOME` configuration).
Back up an existing file. Preserve unrelated tables and avoid duplicate TOML tables.
If `teeproxy` is already defined for another endpoint, choose an unused profile name.

```toml
[model_providers.teeproxy]
name = "TeeRouter via TeeProxy"
base_url = "http://127.0.0.1:8899/v1"
env_key = "TEEPROXY_AGENT_KEY"
wire_api = "responses"
supports_websockets = false
requires_openai_auth = false

[profiles.teeproxy]
model_provider = "teeproxy"
```

Set `TEEPROXY_AGENT_KEY` in the agent process's environment to the existing local key.
Run `codex --profile teeproxy --model <catalog-chatgpt-model-id>`. Do not change the user's
global default or overwrite official login files just to test the new profile. Current
Router transport is HTTP/SSE; do not enable a WebSocket-only mode.

Sources: [TeeProxy integration](https://github.com/wangyi160/teeproxy/blob/main/docs/CLIENTS.en.md),
[Codex configuration](https://learn.chatgpt.com/docs/config-file/config-reference).

## Claude Code

Set these only for the intended Claude process/session unless persistent configuration
is requested:

```text
ANTHROPIC_BASE_URL=http://127.0.0.1:8899
ANTHROPIC_API_KEY=<the existing TeeProxy local API key>
```

Run `claude --model <catalog-claude-model-id>`. Do not append `/v1` to the base URL;
Claude appends `/v1/messages`. Inspect conflicting `ANTHROPIC_AUTH_TOKEN`, key helpers
or provider modes; resolve them only in the intended session, preserving other accounts.

Source: [Claude Code gateway configuration](https://code.claude.com/docs/en/llm-gateway).

## Grok Build

Merge a named model into `~/.grok/config.toml`, preserving existing models and defaults:

```toml
[model.teeproxy]
model = "grok/REPLACE_WITH_CATALOG_MODEL"
base_url = "http://127.0.0.1:8899/v1"
name = "Grok via TeeProxy"
env_key = "TEEPROXY_AGENT_KEY"
api_backend = "responses"
supports_backend_search = false
```

Set `TEEPROXY_AGENT_KEY` in the process environment and run `grok -m teeproxy`.
Replace the placeholder with the exact available ID before use. Do not silently change
`[models].default`. Backend hosted search is outside Router's supported billing scope;
native local tool calls still use the Responses stream.

Source: [Grok Build settings](https://docs.x.ai/build/settings).

## Validate without changing request behavior

Start the native agent in an empty test directory and request a short Hello response
only when an actual test call is requested. The test can incur model charges.
Do not inject or remove caching, reasoning, tool, service-tier or other billing-sensitive
parameters. Preserve the agent's native protocol. Record the result, not its secrets.

`GET /v1/models` is a useful local-auth/catalog check but not an end-to-end model test.
Router doesn't currently support `/v1/responses/compact`, `/v1/messages/count_tokens`
or WebSockets; do not interpret a 404 on one of these as a failed base connection or
work around it by forwarding to a different provider.
