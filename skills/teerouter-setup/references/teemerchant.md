# TeeMerchant: official account providers

Authoritative references: [Releases](https://github.com/wangyi160/teemerchant/releases/latest),
[README](https://github.com/wangyi160/teemerchant/blob/main/README.en.md),
[merchant documentation](https://docs.teerouter.org/teemerchant/).
Checked against public v0.4.2. Follow selected release notes when UI behavior differs.

## Download and run

Use `scripts/download_release.py teemerchant --download <dir>` and extract the verified
archive into a fresh writable directory. Packages contain the runtime and native
verification module; they do not require Electron, Node.js, a Python installation, or
a separate TeeProxy program. Windows is x64 ZIP. Linux is x64 tar.gz and requires
glibc 2.36 or later; inspect `getconf GNU_LIBC_VERSION` before starting on Linux.

- Windows: launch the extracted `teemerchant.exe`. Its small window shows service state
  and buttons to open the management page or data directory. Close/minimize sends it to
  the tray; exit from the tray actually stops the service.
- Linux: run the extracted `./teemerchant` under the intended account. Preserve executable
  permissions. Do not add autostart/systemd or run as root unless that deployment is requested.
- Default page: `http://127.0.0.1:8910`. `--port 8911` selects another local port.
- Optional `service.json` beside the executable:

```json
{"host":"127.0.0.1","port":8910}
```

The service intentionally accepts loopback only. Do not set `0.0.0.0`, expose it through
a public reverse proxy, disable Host/Origin/CSRF checks, or promise native LAN access.
Use a browser on the service host. If a user explicitly needs remote administration,
discuss access to that host separately rather than changing the service's security model.

Data defaults to the executable's `data/`. `--data` can select an existing data directory;
do not start two services against it. Windows uses the original user's DPAPI. Linux uses
the local `data/.vault-key`, which must be included in a protected backup. Do not overwrite
or move encrypted data across operating systems as though it were freely interchangeable.

## Register and connect

Open the local page and use **账号与连接 / Account and connection**. Use an existing local
merchant ID if present, otherwise **注册新 ID / Register new ID**. The client generates
and retains the private key; no platform username/password or hand-entered Merchant Secret
is needed. A running local service is different from a registered identity or verified Router.

Check `https://teerouter.org`, the chosen Router and the reviewed TDX/SNP policy. Login or
saving connection settings triggers TEE verification and connection automatically. Wait
for the Router connection state, not just the service-window running message.

## Add accounts and publish a pool

1. Create or select an account pool in **账号与模型 / Accounts and models**. Choose the
   official provider and the user's intended actual multiplier. Empty pools remain local.
2. Select the pool before **添加账号 / Add account**. The account inherits that pool.
3. Configure that account's outbound proxy before authorization/testing. Supported forms
   include HTTP(S), SOCKS5h and supported VLESS links; `direct://` is not allowed. Never
   substitute a free/public proxy or publish its password in a diagnostic message.
4. Choose either OAuth or JSON import, not both. Complete consent in the provider's UI:
   - ChatGPT/OpenAI: device-code authorization. The user enters the displayed code at the
     official page; account settings may need device-code login enabled.
   - Claude: paste the official authorization code into the client.
   - Grok: paste the complete returned callback URL into the client.
   Codes/callbacks are credentials; enter them into the local UI, not a shared transcript.
5. For JSON import, use the release's documented format. The account alias is independent
   of an official `account_id`; do not replace an official identifier with an alias.
   For bulk import, every entry needs its own explicit proxy and unique account alias.
6. Click **测试连接 / Test connection** after credentials and proxy are filled. Success
   means credentials and official model catalog are accepted; it does not generate tokens.
7. Click **保存并同步 / Save and sync**. Verify account status and last Access Token sync
   time. Do not treat a local save, failed test or pending public snapshot as upstream success.
8. Edit the pool's allowed model list and multiplier. The entire pool shares one allowed
   list; only nonempty pools are published. Confirm configuration changes succeeded.

Refresh tokens, if provided, stay in the merchant service. Only access-token material is
sent directly through the verified Router channel. Keep the service running for renewal
and re-upload after Router restarts. The platform does not receive account credentials.
Queries for public configuration, account status and finances use the management platform;
its snapshot can lag behind a successful token upload.

When renewal fails, inspect the displayed failed step and error. The service retries after
30, 60, 120 and 300 seconds, then pauses the account. Use the account's manual refresh after
diagnosis; do not create a second refresh owner or repeatedly reauthorize without checking
the stored progress. Never attempt to refresh the same rotating token from two clients.

Opening income, receipt or withdrawal pages is fine within setup inspection. Submitting a
withdrawal, changing payout addresses or publishing extra accounts requires the corresponding
user request; these are not prerequisites for verifying the installation.
