---
name: teerouter-setup
description: Download and configure TeeProxy for model users or TeeMerchant for account providers, verify official releases, preserve portable identities, and connect Codex, Claude Code, or Grok Build. Use for installing, upgrading, or troubleshooting these clients, not for deploying the Router or managing the platform.
license: MIT
metadata:
  author: wangyi160
  version: "0.1.0"
---

# TeeRouter client setup

Help the user reach a working client configuration. Respond in their language.
Use the tools available to the agent; when desktop or browser interaction is unavailable,
finish the file/configuration work and give the exact remaining UI action.

## Choose the client

- **Using models:** [TeeProxy setup](references/teeproxy.md). Windows x64 portable GUI.
- **Providing official accounts:** [TeeMerchant setup](references/teemerchant.md).
  Windows x64 portable GUI/service or Linux x64 local web service.
- **Connecting an agent to an existing TeeProxy:** read [Agent configuration](references/agents.md).

Infer the role from the request. Install both only when requested. Check the OS,
architecture, existing process, installation directory and selected identity before writing.
Preserve the user's existing endpoint, policy, port, API key, routing limits and model choices.

## Obtain the release

Run the self-contained Python 3.10+ helper from this skill directory:

```sh
python scripts/download_release.py teeproxy
python scripts/download_release.py teemerchant
# After choosing a writable portable installation location:
python scripts/download_release.py teeproxy --download /path/to/downloads
```

The default command reads the latest stable release metadata. `--download` also fetches
and verifies the archive. `--version vX.Y.Z` selects a published stable tag;
`--platform windows-x64` or `linux-x64` explicitly selects a download target.
Do not assume the agent's Linux/WSL environment is the user's Windows desktop.
Do not install an x64 package on an unsupported architecture without an explicit,
compatible execution environment.

The helper uses only the public `wangyi160/teeproxy` and `wangyi160/teemerchant` GitHub
repositories. It checks SHA-256 against GitHub's asset digest or the release checksum
file, refuses conflicting existing archives and never executes the download.
If Python is unavailable, use the same repository's Releases API/page and the host's
download/hash tools. Do not install Python solely for this helper without considering
the available tools. A checksum establishes archive integrity, not TEE trust.

Extract into a fresh staging directory, inspect the archive layout, and locate the actual
executable before launch. Do not merge a release over a running installation. For an
upgrade, stop the relevant client, back up its complete `data/` directory, then replace
program files while preserving that data. Never publish or place this backup in the skill
repository. Keep the original Windows user for DPAPI-protected data; a Windows data
directory is not a portable Linux identity backup.

## Establish the connection

The public platform is `https://teerouter.org`; the current Router default is
`https://router.teerouter.org`. A user's chosen deployment takes precedence. Let the
client obtain its authenticated Router connection details through its normal identity flow.

Use an existing registered local ID when available. First registration may be ordinary
local-key registration or, for TeeProxy, Google registration. Let the user complete Google
and provider OAuth sign-in/consent in the official browser page. Do not ask for their
password or copy credentials into the conversation. Do not create repeated IDs after an
ambiguous registration result; check whether the original operation succeeded.

Configure an independently reviewed TDX/SNP policy or reuse the user's accepted policy.
An empty example policy does not authorize a deployment. If none is available, ask for
the trusted policy/source while finishing the remaining setup. Do not learn an allowlist
from the endpoint being verified, disable verification or widen it to clear an error.
Platform login, a running local service and a loaded model catalog do not prove TEE verification.

## Confirm and hand off

Follow the selected client's reference for validation. Querying the catalog does not
exercise model generation. Use a real supported agent for an end-to-end test when that
test is within the user's request; it can consume balance. Do not spoof agent headers,
raise a price ceiling or submit payments to make setup appear successful.

Report the installed version/path, portable data path, local endpoint, current connection
state and any remaining user action. Do not print private keys, access/refresh tokens,
proxy passwords or API keys. Report a partial setup accurately if OAuth, TEE policy,
account availability or balance is still missing.
