import os
import re
import json
import requests
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Optional

# --- CONFIGURATION ---
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

# --- LOGGING SYSTEM ---

import glob


class SessionLogger:
    """
    Handles file-based logging for all agent communications.
    """

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
        """Remove old log files to prevent excessive disk usage"""
        try:
            log_files = glob.glob(os.path.join(self.directory, "session_*.log"))
            log_files.sort(key=os.path.getmtime, reverse=True)  # Newest first

            # Remove files beyond the maximum allowed
            for old_log in log_files[self.max_log_files :]:
                os.remove(old_log)
                print(f"[LOG CLEANUP] Removed old log file: {old_log}")
        except Exception as e:
            print(f"[LOG CLEANUP] Error cleaning old logs: {e}")

    def log(self, sender: str, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {sender.upper()}:\n{message}\n{'-' * 40}\n"
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)


# --- TOOLS ---


class TerminalTool:
    @staticmethod
    def execute(command: str) -> str:
        # Enhanced safety filters for Ubuntu 24.04 system administration
        dangerous_patterns = [
            # Destructive file operations
            r"rm\s+-rf\s+/",  # rm -rf / or variations
            r"rm\s+-rf\s+/\*",  # rm -rf /*
            r"mkfs\.",  # Formatting commands
            r"dd\s+if=.*of=/dev/",  # dd to disk devices
            r">\s*/dev/sd",  # Redirecting to disk devices
            # System critical modifications
            r"chmod\s+[0-9]*\s+/(etc|bin|sbin|usr|lib|lib64)",  # Dangerous chmod
            r"chown\s+-R\s+.*\/(etc|bin|sbin|usr|lib|lib64)",  # Dangerous chown
            # Kernel and boot modifications
            r"rm\s+.*\.(ko|mod)$",  # Removing kernel modules
            r"mv\s+/boot/",  # Moving boot files
            r"rm\s+/boot/",  # Removing boot files
            # Fork bombs and resource exhaustion
            r":\(\s*\)\s*{\s*:|\s*&}",  # Fork bomb variations
            # Privilege escalation risks
            r"echo\s+.*>>\s*/etc/sudoers",  # Unsafe sudoers modification
            r"visudo.*-f\s+/etc/sudoers",  # Unsafe sudoers editing
            # Network configuration risks
            r"ifconfig.*down",  # Bringing down network interfaces
            r"ip link.*down",  # Equivalent in ip command
            r"route del.*default",  # Deleting default route
            r"iptables.*-P.*DROP",  # Dropping all packets
            # Package management risks
            r"apt-get.*remove.*--purge.*linux-image",  # Removing kernel images
            r"dpkg.*--purge.*linux-image",  # Same with dpkg
        ]

        import re

        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return f"Error: High-risk command blocked by safety filter. Pattern matched: {pattern}"

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            output = result.stdout if result.stdout else ""
            errors = result.stderr if result.stderr else ""
            if result.returncode != 0:
                return f"Execution Error (Exit Code {result.returncode}):\n{errors}"
            return (
                output if output.strip() else f"Success (no output). Stderr: {errors}"
            )
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds."
        except Exception as e:
            return f"Error executing command: {str(e)}"

    @staticmethod
    def get_system_info() -> str:
        """Get comprehensive system information for Ubuntu 24.04"""
        try:
            info = []

            # Basic system info
            info.append("=== SYSTEM INFORMATION ===")
            info.append(
                f"Hostname: {subprocess.check_output(['hostname'], text=True).strip()}"
            )
            info.append(
                f"OS: {subprocess.check_output(['cat', '/etc/os-release'], text=True).strip()}"
            )

            # Kernel info
            info.append("\n=== KERNEL INFO ===")
            info.append(
                f"Version: {subprocess.check_output(['uname', '-r'], text=True).strip()}"
            )
            info.append(
                f"Architecture: {subprocess.check_output(['uname', '-m'], text=True).strip()}"
            )

            # Uptime
            info.append("\n=== UPTIME ===")
            info.append(subprocess.check_output(["uptime"], text=True).strip())

            # CPU info
            info.append("\n=== CPU INFO ===")
            info.append(
                f"Usage: {subprocess.check_output(['top', '-bn1'], text=True).splitlines()[2] if len(subprocess.check_output(['top', '-bn1'], text=True).splitlines()) > 2 else 'N/A'}"
            )
            info.append(
                f"Cores: {subprocess.check_output(['nproc'], text=True).strip()}"
            )

            # Memory info
            info.append("\n=== MEMORY INFO ===")
            mem_info = subprocess.check_output(["free", "-h"], text=True).strip()
            info.append(mem_info)

            # Disk info
            info.append("\n=== DISK INFO ===")
            disk_info = subprocess.check_output(["df", "-h"], text=True).strip()
            info.append(disk_info)

            # Load average
            info.append("\n=== LOAD AVERAGE ===")
            info.append(
                subprocess.check_output(["cat", "/proc/loadavg"], text=True).strip()
            )

            # Running processes (top 5 by CPU)
            info.append("\n=== TOP PROCESSES (CPU) ===")
            try:
                top_output = subprocess.check_output(
                    ["ps", "aux", "--sort=-%cpu", "-h"], text=True
                ).strip()
                info.append("\n".join(top_output.split("\n")[:5]))
            except:
                info.append("Unable to retrieve process info")

            # Service status (failed services)
            info.append("\n=== FAILED SERVICES ===")
            try:
                failed_services = subprocess.check_output(
                    ["systemctl", "--failed"], text=True, stderr=subprocess.STDOUT
                ).strip()
                if failed_services and "0 loaded units listed" not in failed_services:
                    info.append(failed_services)
                else:
                    info.append("No failed services")
            except:
                info.append("Unable to check service status")

            # Network interfaces
            info.append("\n=== NETWORK INTERFACES ===")
            try:
                net_info = subprocess.check_output(
                    ["ip", "-brief", "addr", "show"], text=True
                ).strip()
                info.append(net_info)
            except:
                info.append("Unable to retrieve network info")

            return "\n".join(info)
        except Exception as e:
            return f"Error getting system info: {str(e)}"


# --- AGENT CORE ---


class ContextManager:
    @staticmethod
    def get_relevant_context(user_input: str) -> str:
        disclosed_text = ""
        input_lower = user_input.lower()
        for name, data in KNOWLEDGE_BASE.items():
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
        "You are an Advanced Linux Automation Agent with Ubuntu 24.04 LTS expertise. You have access to a local terminal.\n\n"
        "**TOOL USE:** To execute a command, use: [[EXEC: <command>]]\n\n"
        "**RULES:** Stop after calling EXEC. Analyze output before final response."
    )

    print(f"\n--- AGENTIC TERMINAL READY (Logging to {LOG_DIR}/) ---")
    history = []

    # Check for command line argument for non-interactive mode
    non_interactive_mode = len(sys.argv) > 1
    initial_prompt = sys.argv[1] if non_interactive_mode else None

    while True:
        if non_interactive_mode:
            if initial_prompt is None:
                # We've already processed the argument, so break
                break
            user_input = initial_prompt
            initial_prompt = None  # mark as used
        else:
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

            # Handle EXEC commands
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

            # Handle system info command
            sysinfo_match = re.search(
                r"\[\[SYSINFO:\s*(.*?)\s*\]\]", response, re.DOTALL
            )
            if sysinfo_match:
                sysinfo_type = (
                    sysinfo_match.group(1).strip()
                    if sysinfo_match.group(1).strip()
                    else "full"
                )
                print(
                    f"\n[?] Agent requests system info: \033[93m{sysinfo_type}\033[0m"
                )

                if MODEL_AUTOMATION:
                    confirm = "y"
                else:
                    confirm = input("[y/n] > ").lower()

                if confirm == "y":
                    logger.log(
                        "SYSTEM", f"Executing System Info Command: {sysinfo_type}"
                    )
                    sysinfo_result = terminal.get_system_info()
                    logger.log("SYSTEM_OUTPUT", sysinfo_result)
                    print(f"[*] System Info:\n{sysinfo_result}")
                else:
                    sysinfo_result = "User denied system info execution."
                    logger.log("SYSTEM", "User denied system info command execution.")
                    print("[!] System Info Execution denied.")

                messages.append(
                    {
                        "role": "user",
                        "content": f"SYSTEM INFO OUTPUT:\n{sysinfo_result}",
                    }
                )
                continue
            else:
                break


if __name__ == "__main__":
    run_agentic_session()
