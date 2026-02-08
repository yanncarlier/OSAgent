#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Progressive‑Disclosure OS Agent
--------------------------------

* Loads context files (identity, agent, soul, tools, heartbeat, skill)
  only when we have token budget left.
* Keeps a running estimate of how many tokens we have already spent.
* Adds newly‑loaded contexts as a system message after each LLM turn.
* The rest of the logic (RUN_COMMAND handling, command execution) is
  identical to the original script you posted.

Author:  <you>
"""

import json
import subprocess
import urllib.request
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# ----------------------------------------------------------------------
# 1️⃣  CONFIGURATION
# ----------------------------------------------------------------------
API_URL = "http://localhost:8080/v1/chat/completions"
CONTEXT_DIR = "../context_files"

# Adjust these if you want a different token ceiling for a single interaction.
# 32 768 is the default for the 7‑B model you listed.
MAX_TOKENS = 32_768

# ----------------------------------------------------------------------
# 2️⃣  PROMPT & SYSTEM MESSAGE
# ----------------------------------------------------------------------
SYSTEM_PROMPT = """You are an OS Agent. You have access to the user's computer.

To run a command, you MUST use the following format:

RUN_COMMAND: ["command", "arg1", "arg2"]


After a command runs, I will give you the output. You should:
1. Analyze the output.
2. If you need more info, run another command.
3. If you have the answer, explain it to the user and start with 'FINISH:'."""
# NOTE: The progressive‑disclosure contexts will be added **after** this
# message, each as its own system entry (preserves priority ordering).

# ----------------------------------------------------------------------
# 3️⃣  TOKEN‑COUNT HELPERS
# ----------------------------------------------------------------------
try:
    import tiktoken  # type: ignore
    ENCODER = tiktoken.encoding_for_model("gpt-3.5-turbo")  # any model that uses cl100k_base
    def count_tokens(text: str) -> int:
        """Accurate token count using tiktoken (if installed)."""
        return len(ENCODER.encode(text))
except Exception:   # pragma: no cover
    # Fallback: 1 token ≈ 4 characters (rough but works for budgeting)
    def count_tokens(text: str) -> int:
        return max(1, len(text) // 4)

# ----------------------------------------------------------------------
# 4️⃣  CONTEXT‑MANAGER (Progressive Disclosure)
# ----------------------------------------------------------------------
class ContextManager:
    """
    Loads the markdown files in priority order, tracks how many tokens they
    cost, and tells the caller whether the next file can be added without
    exceeding the overall token budget.
    """

    def __init__(self, base_dir: Path, max_tokens: int):
        self.base_dir = base_dir
        self.max_tokens = max_tokens

        # ------------------------------------------------------------------
        # 4.1  PRIORITY MAP (lower number == higher priority)
        # ------------------------------------------------------------------
        # You can change these numbers to reshuffle the loading order.
        self.priority_map: Dict[str, int] = {
            "identity": 1,
            "agent":    2,
            "soul":     3,
            "tools":    4,
            "heartbeat":5,
            "skill":    6,
        }

        # ------------------------------------------------------------------
        # 4.2  Build a sorted list of (name, path, priority) tuples
        # ------------------------------------------------------------------
        self._contexts: List[Tuple[str, Path, int]] = []
        for name in self.priority_map:
            md_path = self.base_dir / f"{name.upper()}.md"
            if md_path.is_file():
                self._contexts.append((name, md_path, self.priority_map[name]))
            else:
                print(f"[⚠️] Expected context file not found: {md_path}")

        self._contexts.sort(key=lambda tup: tup[2])   # sort by priority

        # ------------------------------------------------------------------
        # 4.3  Runtime state
        # ------------------------------------------------------------------
        self.loaded: List[str] = []          # names that have been injected
        self.used_tokens: int = 0            # tokens already spent on system messages

    # ----------------------------------------------------------------------
    def _read_and_tokenize(self, path: Path) -> Tuple[str, int]:
        """Read a markdown file and return (text, token_count)."""
        raw = path.read_text(encoding="utf-8")
        tokens = count_tokens(raw)
        return raw, tokens

    # ----------------------------------------------------------------------
    def load_initial(self, messages: List[Dict]) -> None:
        """
        Load as many top‑priority contexts as we can fit *right now*.
        This is called once before the first LLM request.
        """
        for name, path, _ in self._contexts:
            txt, tok = self._read_and_tokenize(path)

            # +1 for the surrounding system role wrapper (ChatML format)
            projected = self.used_tokens + tok + 1
            if projected > self.max_tokens:
                # Can't fit any more – stop.
                break

            messages.append({"role": "system", "content": txt})
            self.loaded.append(name)
            self.used_tokens = projected
            print(f"[📚] Loaded '{name}' ({tok} tokens). "
                  f"Running total: {self.used_tokens}/{self.max_tokens}")

    # ----------------------------------------------------------------------
    def try_load_next(self, messages: List[Dict]) -> bool:
        """
        After a turn, see if we still have budget for the *next* unloaded context.
        Returns True if something was added, False otherwise.
        """
        for name, path, _ in self._contexts:
            if name in self.loaded:
                continue

            txt, tok = self._read_and_tokenize(path)
            projected = self.used_tokens + tok + 1
            if projected > self.max_tokens:
                # No room left – abort further loading.
                return False

            messages.append({"role": "system", "content": txt})
            self.loaded.append(name)
            self.used_tokens = projected
            print(f"[🔓] Progressive disclosure: added '{name}' "
                  f"({tok} tokens). Total now {self.used_tokens}/{self.max_tokens}")
            return True   # only load **one** per turn to keep the interaction tight
        return False

# ----------------------------------------------------------------------
# 5️⃣  LLM CALL (unchanged except for a tiny error‑handling tweak)
# ----------------------------------------------------------------------
def call_llama(messages: List[Dict]) -> str:
    """Send a chat request to the locally‑running llama.cpp server."""
    payload = {
        "messages": messages,
        "temperature": 0.1,
        "stream": False
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL,
                                 data=data,
                                 headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req) as response:
            body = json.loads(response.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"]
    except Exception as exc:   # pragma: no cover
        print(f"\n[!] Error contacting llama.cpp: {exc}")
        sys.exit(1)

# ----------------------------------------------------------------------
# 6️⃣  COMMAND EXECUTOR (unchanged)
# ----------------------------------------------------------------------
def execute_os_command(cmd_list: List[str]) -> Dict[str, str]:
    """Runs a system command and returns a dict with code/stdout/stderr."""
    try:
        proc = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            "code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr
        }
    except Exception as exc:
        return {"code": -1, "stdout": "", "stderr": str(exc)}

# ----------------------------------------------------------------------
# 7️⃣  MAIN LOOP
# ----------------------------------------------------------------------
def main() -> None:
    print("--- Llama OS Bridge (Progressive Disclosure) Active ---")

    user_goal = input("\nWhat should the OS Agent do?: ").strip()

    # ---------- 7.1  Base message list ----------
    messages: List[Dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": user_goal}
    ]

    # ---------- 7.2  Initialise the ContextManager ----------
    ctx_dir = Path(__file__).parent / CONTEXT_DIR
    ctx_mgr = ContextManager(base_dir=ctx_dir, max_tokens=MAX_TOKENS)

    # Load as many top‑priority contexts as we can afford *before* the first LLM call.
    ctx_mgr.load_initial(messages)

    # ---------- 7.3  Interaction loop ----------
    while True:
        # 1️⃣  Let the model think / decide
        print("\n[Thinking...]", end="", flush=True)
        ai_response = call_llama(messages)
        messages.append({"role": "assistant", "content": ai_response})
        print(f"\n[OS Agent] {ai_response}")

        # 2️⃣  Finish? -------------------------------------------------
        if ai_response.strip().upper().startswith("FINISH:"):
            # No more disclosure needed – we are done.
            break

        # 3️⃣  Did the model ask us to run a command? ------------------
        if "RUN_COMMAND:" in ai_response:
            try:
                # Extract the JSON list that follows the token.
                raw_json = ai_response.split("RUN_COMMAND:")[1].strip().split("\n")[0]
                cmd_list = json.loads(raw_json)

                print(f"[Executing] {' '.join(cmd_list)}")
                result = execute_os_command(cmd_list)

                # Echo to the human console for visibility
                if result["stdout"]:
                    print("--- STDOUT ---\n" + result["stdout"])
                if result["stderr"]:
                    print("--- STDERR ---\n" + result["stderr"])

                # 4️⃣  Feed the result back to the model
                result_str = (
                    f"Exit Code: {result['code']}\n"
                    f"STDOUT: {result['stdout']}\n"
                    f"STDERR: {result['stderr']}"
                )
                messages.append({"role": "user", "content": f"COMMAND RESULT:\n{result_str}"})
            except Exception as exc:
                err_msg = f"Error parsing or running command: {exc}"
                print(f"[!] {err_msg}")
                messages.append({"role": "user", "content": err_msg})
        else:
            # No command – politely ask for one (or a FINISH)
            messages.append({"role": "user",
                             "content": ("I didn't see a RUN_COMMAND. "
                                         "If you are done, say FINISH:. "
                                         "Otherwise, provide a RUN_COMMAND.")})

        # ---------------------------------------------------------------
        # 5️⃣  Progressive disclosure: after each turn, try to add the next
        #     context file if we still have budget.
        # ---------------------------------------------------------------
        if ctx_mgr.try_load_next(messages):
            # The newly added system message will be considered on the
            # *next* call to the model, giving it fresh information without
            # re‑sending everything the model already knows.
            pass

    print("\n=== Session finished ===")

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()