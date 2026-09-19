import os
import re
import json
import requests
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Optional

# --- CONFIGURATION ---
# NOTE: You need to have a compatible LLM API running at this endpoint.
# Examples: LocalLM Studio, Ollama with OpenWebUI, or any OpenAI-compatible API
API_URL = "http://10.167.32.1:1234/v1/chat/completions"
MODEL_TEMPERATURE = 0.1
MODEL_AUTOMATION = False
LOG_DIR = "logs"

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
    "UbuntuSystemAdmin": {
        "description": "Ubuntu 24.04 LTS (Noble Numbat) system administration best practices and commands.",
        "triggers": [
            "ubuntu",
            "apt",
            "systemctl",
            "service",
            "package",
            "update",
            "upgrade",
            "netplan",
            "ufw",
            "firewall",
            "user",
            "group",
            "permission",
            "disk",
            "storage",
            "mount",
            "log",
            "journalctl",
        ],
        "content": """
### SPECIALIZED CONTEXT: UBUNTU 24.04 LTS SYSTEM ADMINISTRATION ###
- **Package Management:** Use `apt update && apt upgrade -y` for regular updates. For major version changes, use `do-release-upgrade`.
- **Service Management:** Use `systemctl` commands (start, stop, restart, status, enable, disable) for services managed by systemd.
- **Network Configuration:** Use Netplan (`/etc/netplan/` directory) with `netplan apply` to apply changes.
- **Firewall:** Use UFW (Uncomplicated Firewall) with `ufw enable/disable`, `ufw allow/deny`, `ufw status`.
- **User Management:** Use `adduser`, `deluser`, `usermod` for user management. Use `groups` to view group membership.
- **Disk Management:** Use `lsblk`, `fdisk`, `parted` for disk partitioning. Use `mount`/`umount` for mounting filesystems.
- **Logs:** Use `journalctl` for systemd logs. Common options: `-f` (follow), `-p err` (priority errors), `--since "1 hour ago"`.
- **Hardware Info:** Use `lscpu`, `lsblk`, `lspci`, `lsusb`, `dmidecode` for hardware information.
- **Memory/CPU:** Use `free -h`, `top`, `htop`, `ps aux` for resource monitoring.
- **Boot Management:** Use `systemctl list-units --type=target` to view boot targets. Default is usually graphical.target or multi-user.target.
- **Snap Packages:** Use `snap list`, `snap install`, `snap remove` for managing Snap packages.
- **Kernel Management:** Use `uname -r` to check kernel version. Use `apt list --installed | grep linux-image` to see installed kernels.
""",
    },
    "UbuntuSecurity": {
        "description": "Ubuntu 24.04 LTS security best practices and configurations.",
        "triggers": [
            "security",
            "firewall",
            "ufw",
            "fail2ban",
            "apparmor",
            "selinux",
            "audit",
            "password",
            "ssh",
            "ssl",
            "tls",
            "certificate",
            "encrypt",
        ],
        "content": """
### SPECIALIZED CONTEXT: UBUNTU 24.04 LTS SECURITY ###
- **Firewall:** Enable UFW with `ufw enable`. Set default policies: `ufw default deny incoming`, `ufw default allow outgoing`.
- **SSH Hardening:** Edit `/etc/ssh/sshd_config`: Change port, disable root login (`PermitRootLogin no`), use key-based auth (`PasswordAuthentication no`), limit users (`AllowUsers`).
- **Fail2Ban:** Install with `apt install fail2ban`. Configure in `/etc/fail2ban/jail.local`. Protects against brute-force attacks.
- **AppArmor:** Ubuntu's default MAC system. Check status with `aa-status`. Profiles in `/etc/apparmor.d/`.
- **Password Policies:** Edit `/etc/pam.d/common-password` for complexity requirements. Use `chage` to set password expiration policies.
- **Automatic Updates:** Configure with `apt install unattended-upgrades`. Edit `/etc/apt/apt.conf.d/50unattended-upgrades`.
- **Audit System:** Install auditd with `apt install auditd`. Use `auditctl` to configure rules, `ausearch` to search logs.
- **Rootkit Detection:** Use `rkhunter` and `chkrootkit` for periodic scanning.
- **File Integrity:** Use `AIDE` (Advanced Intrusion Detection Environment) for file integrity monitoring.
- **Encryption:** Use `ecryptfs-utils` for home directory encryption. Consider LUKS for full disk encryption during installation.
- **Network Security:** Disable IPv6 if not needed (`net.ipv6.conf.all.disable_ipv6 = 1` in sysctl.conf). Use TLS/SSL for services.
""",
    },
    "UbuntuTroubleshooting": {
        "description": "Common Ubuntu 24.04 LTS troubleshooting techniques and diagnostic commands.",
        "triggers": [
            "troubleshoot",
            "debug",
            "diagnose",
            "error",
            "problem",
            "issue",
            "fix",
            "repair",
            "rescue",
            "recover",
            "boot",
            "startup",
        ],
        "content": """
### SPECIALIZED CONTEXT: UBUNTU 24.04 LTS TROUBLESHOOTING ###
- **Boot Issues:** 
  - Hold Shift during boot for GRUB menu
  - Use `systemctl rescue` to boot into rescue target
  - Check boot logs with `journalctl -b`
  - Use `fsck` to check filesystem integrity from live CD
  
- **Service Problems:**
  - Check service status: `systemctl status servicename`
  - View logs: `journalctl -u servicename -f`
  - Test configuration: Many services have test commands (e.g., `nginx -t`, `apache2ctl configtest`)
  
- **Network Issues:**
  - Test connectivity: `ping`, `traceroute`, `mtr`
  - Check interfaces: `ip addr show`, `ip link show`
  - Check routing: `ip route show`, `netstat -rn`
  - Check open ports: `ss -tulpn`, `netstat -tulpn`
  - DNS resolution: `dig example.com`, `nslookup example.com`
  
- **Performance Issues:**
  - CPU: `top`, `htop`, `mpstat`, `vmstat`
  - Memory: `free -h`, `vmstat`, `pmap`
  - Disk I/O: `iostat`, `iotop`, `dstat`
  - Network: `iftop`, `nethogs`, `tcpdump`
  
- **Package Issues:**
  - Fix broken packages: `apt --fix-broken install`
  - Reconfigure packages: `dpkg --reconfigure package_name`
  - Clean package cache: `apt clean`, `apt autoclean`
  - Check held packages: `apt-mark showhold`
  
- **Logs Analysis:**
  - System logs: `journalctl` (systemd)
  - Kernel logs: `dmesg`
  - Application logs: Usually in `/var/log/`
  - Log rotation: Configured in `/etc/logrotate.d/`
  
- **Recovery Options:**
  - Boot from live USB for filesystem repairs
  - Use `chroot` to repair installed system from live environment
  - GRUB recovery: Edit boot parameters, use recovery mode
""",
    },
}

# --- LOGGING SYSTEM ---


class SessionLogger:
    """
    Handles file-based logging for all agent communications.
    """

    def __init__(self, directory: str):
        self.directory = directory
        self._ensure_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.directory, f"session_{timestamp}.log")

    def _ensure_dir(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def log(self, sender: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {sender.upper()}:\n{message}\n{'-' * 40}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)


# --- TOOLS ---


class TerminalTool:
    # Define safe command categories for Ubuntu 24.04 LTS system administration
    SAFE_COMMANDS = {
        # File operations (read-only)
        "ls",
        "cat",
        "less",
        "more",
        "head",
        "tail",
        "grep",
        "find",
        "locate",
        "stat",
        "pwd",
        "du",
        "df",
        "diff",
        "cmp",
        "file",
        "which",
        "whereis",
        # System information (read-only)
        "ps",
        "top",
        "htop",
        "free",
        "uname",
        "hostnamectl",
        "lscpu",
        "lsblk",
        "lspci",
        "lsusb",
        "dmidecode",
        "uptime",
        "who",
        "w",
        "last",
        "id",
        "groups",
        "env",
        "printenv",
        "date",
        "cal",
        "timedatectl",
        "locale",
        "hwclock",
        # Network information (read-only)
        "ip",
        "ifconfig",
        "netstat",
        "ss",
        "ping",
        "traceroute",
        "tracepath",
        "host",
        "dig",
        "nslookup",
        "route",
        "arp",
        "iwconfig",
        "iwlist",
        "nmcli",
        # Package management (query only)
        "apt",
        "dpkg",
        "snap",
        "flatpak",
        # Service management (query only)
        "systemctl",
        "service",
        "initctl",
        # Process management (query only)
        "pgrep",
        "pkill",
        "killall",
        "nice",
        "renice",
        # Disk management (query only)
        "fdisk",
        "parted",
        "sfdisk",
        "blkid",
        "mount",
        "lsblk",
        # Log viewing (read-only)
        "journalctl",
        "dmesg",
        "lastlog",
        # User management (query only)
        "getent",
        "finger",
        "chfn",
        "chsh",
        # Miscellaneous safe utilities
        "echo",
        "printf",
        "basename",
        "dirname",
        "realpath",
        "readlink",
        "tree",
        "wc",
        "sort",
        "uniq",
        "cut",
        "paste",
        "join",
        "split",
        "fmt",
        "pr",
        "tr",
        "expr",
        "bc",
        "calc",
        "units",
        "numfmt",
    }

    # Commands that require caution (can modify system but are generally safe with proper args)
    CAUTIOUS_COMMANDS = {
        # File operations (can modify)
        "cp",
        "mv",
        "mkdir",
        "rmdir",
        "touch",
        "chmod",
        "chown",
        "chgrp",
        # Archive/compression
        "tar",
        "gzip",
        "gunzip",
        "bzip2",
        "bunzip2",
        "xz",
        "unxz",
        "zip",
        "unzip",
        # Text processing (can modify files)
        "sed",
        "awk",
        "perl",
        "python",
        "python3",
        "ruby",
        "php",
        # Download/transfer
        "wget",
        "curl",
        "scp",
        "rsync",
        # System control (limited)
        "shutdown",
        "reboot",
        "halt",
        "poweroff",
        "suspend",
        "hibernate",
        # Service management (can modify)
        "systemctl",
        "service",
        "initctl",
        # Package management (can modify)
        "apt",
        "dpkg",
        "snap",
        "flatpak",
        # User management (can modify)
        "useradd",
        "usermod",
        "userdel",
        "groupadd",
        "groupmod",
        "groupdel",
        # Password management
        "passwd",
        "chage",
        # Cron jobs
        "crontab",
        # Kernel modules
        "lsmod",
        "insmod",
        "rmmod",
        "modprobe",
        # Firewall (query and basic modify)
        "ufw",
        "iptables",
        "nft",
        "firewalld",
    }

    # Commands that are dangerous and should be blocked or require extra confirmation
    DANGEROUS_COMMANDS = {
        # Destructive file operations
        "rm",
        ">",
        ">>",
        "<",
        "|",
        "dd",
        ">|",
        "&>",
        # Disk destruction
        "fdisk",
        "parted",
        "sfdisk",
        "mkfs",
        "mkswap",
        # System modification
        "mount",
        "umount",
        "swapon",
        "swapoff",
        # Kernel/module modification
        "modprobe",
        "insmod",
        "rmmod",  # Also in cautious but risky
        # Dangerous system commands
        "init",
        "telinit",
        "kill",
        "killall5",
        "reboot",
        "poweroff",
        "halt",
        # Dangerous package operations
        "apt-get",
        "apt-cache",
        "dpkg-reconfigure",
        "dpkg-divert",
        # Dangerous user operations
        "chpasswd",
        "newusers",
        # Dangerous network
        "ifconfig",
        "ip",
        "route",
        "arp",  # Also in cautious/safe but can be risky
        # Obviously dangerous
        "forkbomb",
        ":(){ :|:& };:",
        "rm -rf",
        "mkfs",
        "format",
    }

    @staticmethod
    def _is_safe_command(command: str) -> tuple[bool, str]:
        """
        Check if a command is safe to execute.
        Returns (is_safe, reason) tuple.
        """
        # Handle empty commands
        if not command or not command.strip():
            return False, "Empty command"

        # Split command into parts
        parts = command.strip().split()
        if not parts:
            return False, "Invalid command"

        base_cmd = parts[0]

        # Check for obvious dangerous patterns first
        dangerous_patterns = [
            "rm -rf /",
            "rm -rf /*",
            ":(){ :|:& };:",
            "chmod -R 777 /",
            "chown -R root:root /",
            "> /dev/sda",
            "dd if=",
            "fork()",
            "forkbomb",
        ]

        for pattern in dangerous_patterns:
            if pattern in command:
                return False, f"Dangerous pattern detected: {pattern}"

        # Check if base command is in dangerous list
        if base_cmd in TerminalTool.DANGEROUS_COMMANDS:
            # Some commands in dangerous list might be safe with specific args
            # For now, we'll treat them as requiring caution
            return (
                False,
                f"Command '{base_cmd}' is considered dangerous and requires extra review",
            )

        # Check if base command is in cautious list
        if base_cmd in TerminalTool.CAUTIOUS_COMMANDS:
            return True, f"Command '{base_cmd}' is cautious - allowed with review"

        # Check if base command is in safe list
        if base_cmd in TerminalTool.SAFE_COMMANDS:
            return True, f"Command '{base_cmd}' is considered safe"

        # Command not in any list - treat as unknown and require caution
        return (
            False,
            f"Command '{base_cmd}' is not in approved list - requires manual review",
        )

    @staticmethod
    def execute(command: str) -> str:
        # First check if command is safe
        is_safe, reason = TerminalTool._is_safe_command(command)

        # Log the safety check result for transparency
        safety_log = f"Safety Check: {reason}"

        if not is_safe:
            # For unknown commands or cautious commands, we still might allow them
            # but with extra warning
            if "not in approved list" in reason or "cautious" in reason:
                return f"Warning: {safety_log}\nProceed with caution. This command may modify your system."
            else:
                # Actually dangerous commands
                return f"Error: {safety_log}"

        # If we get here, command passed safety check
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            output = result.stdout if result.stdout else ""
            errors = result.stderr if result.stderr else ""
            if result.returncode != 0:
                return f"Execution Error (Exit Code {result.returncode}):\n{errors}\n\nSafety Check: {safety_log}"
            return (
                output
                if output.strip()
                else f"Success (no output). Stderr: {errors}\n\nSafety Check: {safety_log}"
            )
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds.\n\nSafety Check: {safety_log}"
        except Exception as e:
            return f"Error executing command: {str(e)}\n\nSafety Check: {safety_log}"


# --- AGENT CORE ---


class ContextManager:
    @staticmethod
    def get_relevant_context(user_input: str) -> str:
        """
        Get relevant context based on user input with improved matching and formatting.
        Returns formatted context string or empty string if no relevant context found.
        """
        if not user_input or not user_input.strip():
            return ""

        input_lower = user_input.lower()
        context_matches = []

        # Score each knowledge base entry based on trigger matches
        for name, data in KNOWLEDGE_BASE.items():
            triggers = data.get("triggers", [])
            if not triggers:
                continue

            # Count how many triggers match
            matches = sum(1 for trigger in triggers if trigger in input_lower)
            if matches > 0:
                # Calculate relevance score (simple ratio of matched triggers)
                relevance = matches / len(triggers)
                context_matches.append(
                    {
                        "name": name,
                        "content": data["content"],
                        "relevance": relevance,
                        "matches": matches,
                        "triggers_len": len(
                            triggers
                        ),  # Store for threshold calculation
                    }
                )

        # Sort by relevance (descending) and then by number of matches (descending)
        context_matches.sort(key=lambda x: (x["relevance"], x["matches"]), reverse=True)

        # Build disclosed text with prioritized context
        disclosed_text = ""
        for match in context_matches:
            # Include context if:
            # 1. Relevance is at least 15%, OR
            # 2. At least 2 direct matches, OR
            # 3. For trigger lists with more than 10 items, at least 1 match with relevance >= 0.08
            if (
                match["relevance"] >= 0.15
                or match["matches"] >= 2
                or (
                    match["triggers_len"] > 10
                    and match["relevance"] >= 0.08
                    and match["matches"] >= 1
                )
            ):
                disclosed_text += (
                    f"\n--- {match['name'].upper()} ---\n{match['content'].strip()}\n"
                )

        return disclosed_text.strip()


class AgentLLM:
    @staticmethod
    def chat(messages: List[Dict]) -> str:
        payload = {
            "messages": messages,
            "temperature": MODEL_TEMPERATURE,
            "stream": False,
            "stop": ["User>", "System:"],
        }
        try:
            response = requests.post(API_URL, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error: {str(e)}"


# --- ORCHESTRATOR ---


def run_agentic_session():
    terminal = TerminalTool()
    logger = SessionLogger(LOG_DIR)

    base_system_prompt = (
        "You are an Advanced Linux Automation Agent. You have access to a local terminal.\n\n"
        "**TOOL USE:** To execute a command, use: [[EXEC: <command>]]\n\n"
        "**RULES:** Stop after calling EXEC. Analyze output before final response."
    )

    print(f"\n--- AGENTIC TERMINAL READY (Logging to {LOG_DIR}/) ---")
    history = []

    while True:
        try:
            user_input = input("\nUser> ")
        except KeyboardInterrupt:
            break

        if user_input.lower() in ["exit", "quit", "q"]:
            logger.log("SYSTEM", "User terminated session.")
            break

        logger.log("USER", user_input)

        specialized_context = ContextManager.get_relevant_context(user_input)
        current_system_message = base_system_prompt
        if specialized_context:
            current_system_message += (
                f"\n\n--- ACTIVE KNOWLEDGE ---\n{specialized_context}"
            )

        messages = [{"role": "system", "content": current_system_message}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})
        history.append({"role": "user", "content": user_input})

        while True:
            print("Agent thinking...", end="\r")
            response = AgentLLM.chat(messages)
            print(f"\rAgent: {response}\n")

            logger.log("AGENT", response)
            history.append({"role": "assistant", "content": response})
            messages.append({"role": "assistant", "content": response})

            match = re.search(r"\[\[EXEC:\s*(.*?)\s*\]\]", response, re.DOTALL)
            if match:
                cmd = match.group(1).strip()
                print(f"\n[?] Agent requests execution: \033[93m{cmd}\033[0m")

                if MODEL_AUTOMATION:
                    confirm = "y"
                else:
                    confirm = input("[y/n] > ").lower()

                if confirm == "y":
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
                continue
            else:
                break


if __name__ == "__main__":
    # Check if a prompt was provided as command-line argument
    if len(sys.argv) > 1:
        # Agentic mode: treat first arg as goal/prompt, run until completion
        prompt = " ".join(sys.argv[1:])
        terminal = TerminalTool()
        logger = SessionLogger(LOG_DIR)

        base_system_prompt = (
            "You are an Advanced Linux Automation Agent. You have access to a local terminal.\n\n"
            "**TOOL USE:** To execute a command, use: [[EXEC: <command>]]\n\n"
            "**RULES:** Stop after calling EXEC. Analyze output before final response.\n\n"
            "**GOAL:** Continue working on the user's objective until it is complete, then provide a final summary without requesting further actions."
        )

        specialized_context = ContextManager.get_relevant_context(prompt)
        current_system_message = base_system_prompt
        if specialized_context:
            current_system_message += (
                f"\n\n--- ACTIVE KNOWLEDGE ---\n{specialized_context}"
            )

        messages = [{"role": "system", "content": current_system_message}]
        messages.append({"role": "user", "content": prompt})

        print(f"\n--- AGENTIC TERMINAL READY (Logging to {LOG_DIR}/) ---")
        print(f"\nObjective: {prompt}")

        max_iterations = 20  # Safety limit
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            print("Agent thinking...", end="\r")
            response = AgentLLM.chat(messages)
            print(f"\rAgent: {response}\n")

            logger.log("AGENT", response)

            # Check if LLM requested command execution
            match = re.search(r"\[\[EXEC:\s*(.*?)\s*\]\]", response, re.DOTALL)
            if match:
                cmd = match.group(1).strip()
                print(f"\n[?] Agent requests execution: \033[93m{cmd}\033[0m")

                if MODEL_AUTOMATION:
                    confirm = "y"
                else:
                    confirm = input("[y/n] > ").lower()

                if confirm == "y":
                    logger.log("SYSTEM", f"Executing Command: {cmd}")
                    execution_result = terminal.execute(cmd)
                    logger.log("TERMINAL_OUTPUT", execution_result)
                    print(f"[*] Output:\n{execution_result}")
                else:
                    execution_result = "User denied execution."
                    logger.log("SYSTEM", "User denied command execution.")
                    print("[!] Execution denied.")

                # Add the command output to conversation for next iteration
                messages.append(
                    {"role": "user", "content": f"COMMAND OUTPUT:\n{execution_result}"}
                )
                # Continue loop - LLM will see this output and decide next action
            else:
                # LLM didn't request any execution - consider task complete
                print("\n--- Task Completed ---")
                logger.log(
                    "SYSTEM",
                    "Agent indicates task completion (no further actions requested)",
                )
                break
        else:
            # This executes if loop completed without breaking (hit max iterations)
            print(f"\n--- Maximum iterations ({max_iterations}) reached ---")
            logger.log("SYSTEM", f"Terminated after {max_iterations} iterations")
    else:
        # Run in interactive mode if no arguments provided
        run_agentic_session()
