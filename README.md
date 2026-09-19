# OSAgent

A terminal agent that acts as an Ubuntu 24.04 LTS sysadmin. Safety comes first: destructive commands are blocked, and a human on the same terminal can approve, deny, or interrupt work. Inference can be local or remote as long as it speaks OpenAI chat completions.

## What it does

- Interactive `User>` loop so you stay in the loop
- **Ask first** (default): every `[[EXEC:]]` / `[[SYSINFO:]]` waits for `[y/n]`
- **Autonomous**: `--autonomous` or `OSAGENT_AUTOMATION=true` — still printed, still deny-listed, Ctrl+C stops the session
- Deny-list for host-killing patterns (`rm -rf /`, `mkfs`, `dd` to disks, dropping default routes, purging kernel images, …)
- Real sysadmin commands (`systemctl`, `apt`, `journalctl`, `ip`, `ufw`) are allowed after confirmation

## Setup

Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
uv venv
source .venv/bin/activate
uv sync
```

Point the agent at any OpenAI-compatible server:

```bash
export OSAGENT_API_URL=http://127.0.0.1:1234/v1/chat/completions
export OSAGENT_MODEL=          # set if the server requires a model id
```

Copy `.env.example` and export those variables, or pass flags.

## Run

```bash
uv run python main.py
uv run python main.py "Check failed systemd units and disk usage"
uv run python main.py --autonomous "Collect a health snapshot"
uv run python main.py --api-url http://10.167.32.1:1234/v1/chat/completions --model llama-3.1
```

Quit with `exit`, `quit`, `q`, or Ctrl+C.

## Why this code won the bakeoff

Seven copies of the same agent were improved by different models. Most “safety” patches blocked normal administration (`systemctl`, `sudo`, `apt`) or used allowlists so tight the agent could not do the job. This tree is the Mistral variant: a **deny-list of destructive operations**, Ubuntu/monitoring knowledge, a read-only `SYSINFO` snapshot, and ask-first confirmation. Archives live in `Docs/bakeoff/`.

Simulated MCP “self-healing” servers from other variants are not part of the product; they talk to fake inventory, not this host.
