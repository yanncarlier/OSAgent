#!/usr/bin/env python3
"""Ubuntu 24.04 sysadmin agent: deny-list safety, ask-first HITL, OpenAI-compatible LLM."""

from __future__ import annotations

import argparse
import glob
import os
import re
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional

import requests

# --- CONFIGURATION (env overrides; CLI can override env) ---
API_URL = os.getenv("OSAGENT_API_URL", "http://127.0.0.1:1234/v1/chat/completions")
MODEL_NAME = os.getenv("OSAGENT_MODEL", "")
MODEL_TEMPERATURE = float(os.getenv("OSAGENT_MODEL_TEMPERATURE", "0.1"))
MODEL_AUTOMATION = os.getenv("OSAGENT_AUTOMATION", "false").lower() in {
    "1",
    "true",
    "yes",
    "on",
}
LOG_DIR = os.getenv("OSAGENT_LOG_DIR", "logs")
COMMAND_TIMEOUT_SEC = int(os.getenv("OSAGENT_COMMAND_TIMEOUT", "30"))
MAX_HISTORY_TURNS = int(os.getenv("OSAGENT_MAX_HISTORY_TURNS", "20"))

# --- EMBEDDED KNOWLEDGE BASE ---
KNOWLEDGE_BASE = {
    "BashScriptMaster": {
        "description": "Advanced shell scripting best practices and automation logic.",
        "triggers": [
            "bash",
            "shell",
            "script",
            "loop",
            "variable",
            "pipe",
            "sed",
            "awk",
            "grep",
            "automation",
        ],
        "content": """
### SPECIALIZED CONTEXT: PROFESSIONAL BASH SCRIPTING ###
- **Strict Mode:** Every script suggested must start with `set -euo pipefail`.
- **Portability:** Use `#!/usr/bin/env bash`.
- **Syntax:** Use `[[ ]]` for tests and `$(...)` for command substitution. Quote all variables.
- **Functionality:** Group logic into functions using `local` variables.
- **Performance:** Prefer `awk` or `sed` for large file processing.
""",
    },
    "Ubuntu2404Admin": {
        "description": "Ubuntu 24.04 LTS specific system administration and maintenance procedures.",
        "triggers": [
            "ubuntu",
            "24.04",
            "apt",
            "systemd",
            "service",
            "boot",
            "kernel",
            "upgrade",
            "netplan",
            "firewall",
            "ufw",
            "snap",
        ],
        "content": """
### SPECIALIZED CONTEXT: UBUNTU 24.04 LTS SYSTEM ADMINISTRATION ###
- **Package Management:** Use `apt update && apt upgrade -y` for regular updates. Prefer `apt install --only-upgrade` for specific packages.
- **Service Management:** Use `systemctl` commands: `systemctl status [service]`, `systemctl restart [service]`, `systemctl enable [service]`.
- **Boot & Kernel:** Do not remove old kernels until verifying new one works. Use `sudo apt autoremove --purge` to clean old kernels safely.
- **Network Configuration:** Use Netplan (`/etc/netplan/*.yaml`). Apply changes with `sudo netplan apply`.
- **Firewall:** UFW is default. Enable with `sudo ufw enable`, allow services with `sudo ufw allow [service]`.
- **Snap Packages:** List with `snap list`, refresh with `sudo snap refresh`. Be cautious with classic snaps.
- **Logs:** Use `journalctl` for system logs. `journalctl -u [service]` for service-specific logs.
- **Hardware Info:** Use `lscpu`, `lsblk`, `lspci`, `lsusb` for hardware inspection.
- **Disk Management:** Use `lsblk`, `df -h`, `du -sh`. For partitioning, prefer `parted` or `gparted`.
- **Users & Permissions:** Use `adduser`, `usermod`, `groups`. Always use `visudo` for sudoers edits.
""",
    },
    "SystemMonitoring": {
        "description": "System health monitoring and performance analysis techniques.",
        "triggers": [
            "monitor",
            "performance",
            "cpu",
            "memory",
            "disk",
            "network",
            "load",
            "usage",
            "top",
            "htop",
            "iotop",
        ],
        "content": """
### SPECIALIZED CONTEXT: SYSTEM HEALTH MONITORING ###
- **CPU Usage:** Monitor with `top`, `htop`, `mpstat`. Watch for high %sys or %wait indicating kernel or I/O issues.
- **Memory:** Use `free -h`, `vmstat`. Check for swap usage and cache pressure.
- **Disk I/O:** Monitor with `iostat`, `iotop`. High await times indicate storage bottlenecks.
- **Network:** Use `iftop`, `nethogs`, `ss -s`. Check for dropped packets and high latency.
- **Load Average:** Check with `uptime` or `cat /proc/loadavg`. Values > CPU count indicate overload.
- **Process Analysis:** Use `ps aux --sort=-%cpu` or `ps aux --sort=-%mem` for resource-heavy processes.
- **Service Health:** Use `systemctl is-failed [service]` and `systemctl status [service]`.
- **Logs Analysis:** Use `journalctl --since "1 hour ago"` for recent issues. Look for repeated errors.
- **Temperature:** Monitor with `sensors` (lm-sensors package) for overheating issues.
""",
    },
}

# Hard deny: commands that can destroy a host. Sysadmin work (systemctl, apt, journalctl) is allowed.
DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+/\*",
    r"mkfs\.",
    r"dd\s+if=.*of=/dev/",
    r">\s*/dev/sd",
    r"chmod\s+[0-9]*\s+/(etc|bin|sbin|usr|lib|lib64)",
    r"chown\s+-R\s+.*\/(etc|bin|sbin|usr|lib|lib64)",
    r"rm\s+.*\.(ko|mod)$",
    r"mv\s+/boot/",
    r"rm\s+/boot/",
    r":\(\s*\)\s*{\s*:|\s*&}",
    r"echo\s+.*>>\s*/etc/sudoers",
    r"visudo.*-f\s+/etc/sudoers",
    r"ifconfig.*down",
    r"ip link.*down",
    r"route del.*default",
    r"iptables.*-P.*DROP",
    r"apt-get.*remove.*--purge.*linux-image",
    r"dpkg.*--purge.*linux-image",
]


class SessionLogger:
    """File-based logging for all agent communications."""

    def __init__(self, directory: str, max_log_files: int = 10):
        self.directory = directory
        self.max_log_files = max_log_files
        self._ensure_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.directory, f"session_{timestamp}.log")
        self._cleanup_old_logs()

    def _ensure_dir(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def _cleanup_old_logs(self):
        try:
            log_files = glob.glob(os.path.join(self.directory, "session_*.log"))
            log_files.sort(key=os.path.getmtime, reverse=True)
            for old_log in log_files[self.max_log_files :]:
                os.remove(old_log)
                print(f"[LOG CLEANUP] Removed old log file: {old_log}")
        except OSError as e:
            print(f"[LOG CLEANUP] Error cleaning old logs: {e}")

    def log(self, sender: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {sender.upper()}:\n{message}\n{'-' * 40}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)


class TerminalTool:
    @staticmethod
    def execute(command: str) -> str:
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return (
                    "Error: High-risk command blocked by safety filter. "
                    f"Pattern matched: {pattern}"
                )

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=COMMAND_TIMEOUT_SEC,
            )
            output = result.stdout if result.stdout else ""
            errors = result.stderr if result.stderr else ""
            if result.returncode != 0:
                return f"Execution Error (Exit Code {result.returncode}):\n{errors}"
            return (
                output if output.strip() else f"Success (no output). Stderr: {errors}"
            )
        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {COMMAND_TIMEOUT_SEC} seconds."
        except Exception as e:
            return f"Error executing command: {str(e)}"

    @staticmethod
    def get_system_info() -> str:
        """Read-only snapshot of Ubuntu host health."""
        try:
            info = []
            info.append("=== SYSTEM INFORMATION ===")
            info.append(
                f"Hostname: {subprocess.check_output(['hostname'], text=True).strip()}"
            )
            info.append(
                f"OS: {subprocess.check_output(['cat', '/etc/os-release'], text=True).strip()}"
            )

            info.append("\n=== KERNEL INFO ===")
            info.append(
                f"Version: {subprocess.check_output(['uname', '-r'], text=True).strip()}"
            )
            info.append(
                f"Architecture: {subprocess.check_output(['uname', '-m'], text=True).strip()}"
            )

            info.append("\n=== UPTIME ===")
            info.append(subprocess.check_output(["uptime"], text=True).strip())

            info.append("\n=== CPU INFO ===")
            top_lines = subprocess.check_output(["top", "-bn1"], text=True).splitlines()
            info.append(
                f"Usage: {top_lines[2] if len(top_lines) > 2 else 'N/A'}"
            )
            info.append(
                f"Cores: {subprocess.check_output(['nproc'], text=True).strip()}"
            )

            info.append("\n=== MEMORY INFO ===")
            info.append(subprocess.check_output(["free", "-h"], text=True).strip())

            info.append("\n=== DISK INFO ===")
            info.append(subprocess.check_output(["df", "-h"], text=True).strip())

            info.append("\n=== LOAD AVERAGE ===")
            info.append(
                subprocess.check_output(["cat", "/proc/loadavg"], text=True).strip()
            )

            info.append("\n=== TOP PROCESSES (CPU) ===")
            try:
                top_output = subprocess.check_output(
                    ["ps", "aux", "--sort=-%cpu", "-h"], text=True
                ).strip()
                info.append("\n".join(top_output.split("\n")[:5]))
            except subprocess.CalledProcessError:
                info.append("Unable to retrieve process info")

            info.append("\n=== FAILED SERVICES ===")
            try:
                failed_services = subprocess.check_output(
                    ["systemctl", "--failed"], text=True, stderr=subprocess.STDOUT
                ).strip()
                if failed_services and "0 loaded units listed" not in failed_services:
                    info.append(failed_services)
                else:
                    info.append("No failed services")
            except subprocess.CalledProcessError:
                info.append("Unable to check service status")

            info.append("\n=== NETWORK INTERFACES ===")
            try:
                net_info = subprocess.check_output(
                    ["ip", "-brief", "addr", "show"], text=True
                ).strip()
                info.append(net_info)
            except subprocess.CalledProcessError:
                info.append("Unable to retrieve network info")

            return "\n".join(info)
        except Exception as e:
            return f"Error getting system info: {str(e)}"


class ContextManager:
    @staticmethod
    def get_relevant_context(user_input: str) -> str:
        disclosed_text = ""
        input_lower = user_input.lower()
        for _name, data in KNOWLEDGE_BASE.items():
            if any(trigger in input_lower for trigger in data.get("triggers", [])):
                disclosed_text += f"\n{data['content']}\n"
        return disclosed_text


class AgentLLM:
    @staticmethod
    def chat(messages: List[Dict]) -> str:
        payload = {
            "messages": messages,
            "temperature": MODEL_TEMPERATURE,
            "stream": False,
            "stop": ["User>", "System:"],
        }
        if MODEL_NAME:
            payload["model"] = MODEL_NAME
        try:
            response = requests.post(API_URL, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {str(e)}"


def _trim_history(history: List[Dict]) -> List[Dict]:
    max_messages = MAX_HISTORY_TURNS * 2
    if len(history) <= max_messages:
        return history
    return history[-max_messages:]


def confirm_execution(prompt: str) -> bool:
    """Ask-first HITL. Autonomous mode still prints the command; Ctrl+C aborts."""
    print(prompt)
    if MODEL_AUTOMATION:
        print("[autonomous] proceeding (Ctrl+C to interrupt the agent)")
        return True
    try:
        answer = input("[y/n] > ").strip().lower()
    except (KeyboardInterrupt, EOFError):
        print()
        return False
    return answer in {"y", "yes"}


def system_prompt() -> str:
    mode = "AUTONOMOUS" if MODEL_AUTOMATION else "ASK FIRST"
    return (
        "You are a risk-averse Ubuntu 24.04 LTS system administrator agent.\n"
        "Prefer read-only diagnosis before any change. Never suggest destroying "
        "disks, wiping /, dropping default routes, or purging kernel packages.\n\n"
        "**TOOL USE:**\n"
        "- Shell command: [[EXEC: <command>]]\n"
        "- Host health snapshot (read-only): [[SYSINFO: full]]\n\n"
        "**RULES:** Emit at most one tool call, then stop. Analyze the tool output "
        "before the next action or a final answer.\n"
        f"**MODE:** {mode}. The operator is on the same terminal and can deny commands."
    )


def handle_tool_turn(
    response: str,
    terminal: TerminalTool,
    logger: SessionLogger,
    messages: List[Dict],
) -> bool:
    """Return True if a tool ran and the model should continue."""
    match = re.search(r"\[\[EXEC:\s*(.*?)\s*\]\]", response, re.DOTALL)
    if match:
        cmd = match.group(1).strip()
        print(f"\n[?] Agent requests execution: \033[93m{cmd}\033[0m")
        if confirm_execution("Execute this command?"):
            logger.log("SYSTEM", f"Executing Command: {cmd}")
            execution_result = terminal.execute(cmd)
            logger.log("TERMINAL_OUTPUT", execution_result)
            print(f"[*] Output:\n{execution_result}")
        else:
            execution_result = "User denied execution."
            logger.log("SYSTEM", "User denied command execution.")
            print("[!] Execution denied.")
        messages.append(
            {"role": "user", "content": f"COMMAND OUTPUT:\n{execution_result}"}
        )
        return True

    sysinfo_match = re.search(r"\[\[SYSINFO:\s*(.*?)\s*\]\]", response, re.DOTALL)
    if sysinfo_match:
        sysinfo_type = sysinfo_match.group(1).strip() or "full"
        print(f"\n[?] Agent requests system info: \033[93m{sysinfo_type}\033[0m")
        if confirm_execution("Collect this host snapshot?"):
            logger.log("SYSTEM", f"Executing System Info Command: {sysinfo_type}")
            sysinfo_result = terminal.get_system_info()
            logger.log("SYSTEM_OUTPUT", sysinfo_result)
            print(f"[*] System Info:\n{sysinfo_result}")
        else:
            sysinfo_result = "User denied system info execution."
            logger.log("SYSTEM", "User denied system info command execution.")
            print("[!] System Info Execution denied.")
        messages.append(
            {"role": "user", "content": f"SYSTEM INFO OUTPUT:\n{sysinfo_result}"}
        )
        return True

    return False


def run_one_user_turn(
    user_input: str,
    history: List[Dict],
    terminal: TerminalTool,
    logger: SessionLogger,
) -> List[Dict]:
    logger.log("USER", user_input)
    current_system_message = system_prompt()
    specialized_context = ContextManager.get_relevant_context(user_input)
    if specialized_context:
        current_system_message += f"\n\n--- ACTIVE KNOWLEDGE ---\n{specialized_context}"

    messages = [{"role": "system", "content": current_system_message}]
    messages.extend(_trim_history(history))
    messages.append({"role": "user", "content": user_input})
    history.append({"role": "user", "content": user_input})

    while True:
        print("Agent thinking...", end="\r")
        response = AgentLLM.chat(messages)
        print(f"\rAgent: {response}\n")
        logger.log("AGENT", response)
        history.append({"role": "assistant", "content": response})
        messages.append({"role": "assistant", "content": response})
        if not handle_tool_turn(response, terminal, logger, messages):
            break
    return history


def run_agentic_session(initial_prompt: Optional[str] = None) -> None:
    terminal = TerminalTool()
    logger = SessionLogger(LOG_DIR)
    mode = "autonomous" if MODEL_AUTOMATION else "ask-first"
    print(f"\n--- OSAgent ready ({mode}) ---")
    print(f"Inference: {API_URL}")
    if MODEL_NAME:
        print(f"Model: {MODEL_NAME}")
    print(f"Logs: {logger.log_file}")
    print("Type a task, or exit/quit/q. Ctrl+C leaves the session.\n")

    history: List[Dict] = []
    if initial_prompt:
        history = run_one_user_turn(initial_prompt, history, terminal, logger)

    while True:
        try:
            user_input = input("\nUser> ")
        except (KeyboardInterrupt, EOFError):
            print("\nSession ended.")
            break

        if user_input.lower() in ["exit", "quit", "q"]:
            logger.log("SYSTEM", "User terminated session.")
            break

        if not user_input.strip():
            continue

        history = run_one_user_turn(user_input, history, terminal, logger)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "OSAgent: Ubuntu sysadmin agent. Ask-first by default; "
            "use --autonomous only inside a disposable host."
        )
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Optional first task. After it finishes, the terminal stays open.",
    )
    parser.add_argument(
        "--autonomous",
        "-A",
        action="store_true",
        help="Skip y/n confirmation (still blocked by the safety deny-list).",
    )
    parser.add_argument(
        "--ask-first",
        action="store_true",
        help="Force confirmation even if OSAGENT_AUTOMATION is set.",
    )
    parser.add_argument("--api-url", help="OpenAI-compatible chat completions URL.")
    parser.add_argument(
        "--model",
        help="Model id for local or remote providers that require it.",
    )
    return parser.parse_args()


def apply_runtime_config(args: argparse.Namespace) -> None:
    global API_URL, MODEL_NAME, MODEL_AUTOMATION
    if args.api_url:
        API_URL = args.api_url
    if args.model:
        MODEL_NAME = args.model
    if args.autonomous:
        MODEL_AUTOMATION = True
    if args.ask_first:
        MODEL_AUTOMATION = False


if __name__ == "__main__":
    cli = parse_args()
    apply_runtime_config(cli)
    first = " ".join(cli.prompt).strip() or None
    run_agentic_session(first)
