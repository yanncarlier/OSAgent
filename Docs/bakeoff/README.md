# Bakeoff archive

These folders were parallel “improve this Ubuntu sysadmin agent” runs. One product tree was kept at the repo root (Mistral’s deny-list + Ubuntu knowledge), then wired for env/CLI inference and a persistent terminal HITL.

| Variant | Verdict |
| --- | --- |
| **OSAgent-mistral** | **Winner.** Blocks host-killing patterns, still allows `systemctl` / `apt` / `journalctl`. Ubuntu + monitoring knowledge. `[[SYSINFO:]]`. Ask-first. |
| OSAgent-chatgpt | Targeted deny-list plus leaky “strict” prefixes. Usable, weaker Ubuntu context. |
| OSAgent-gemini | Over-blocks (`systemctl stop`, all `rm`). `if __name__` sits above later helpers. |
| OSAgent-grok | Best knowledge dump, broken policy (`ip` / `apt-get` treated as dangerous; unknown commands never run). Simulated MCP leftover. |
| OSAgent-claude | Env config was good; filters block `systemctl`, `sudo`, `ps aux` — not a sysadmin. Simulated MCP leftover. |
| OSAgent-perplexity | Automation rate limits / audit log ideas; `sudo` and tiny automation whitelist make admin impossible. |
| OSAgent-x | Allowlist includes `sudo`/`wget`; substring “destructive” matches are noisy. |

`LXD_create_VMs.sh` provisioned one VM per variant. Context-generation prompts and screenshots are in `Docs/AGENTS_context_generation_testing_files/`.
