```text
You are a senior software architect and context-engineering expert specializing in LLM-agent systems.

Your task is to deeply understand the provided codebase and create a set of lightweight, high-value "scaffolding" files that will dramatically improve how future LLM agents (including code-reading, refactoring, feature-adding, bug-fixing, architecture-review agents) can work with this project — while using as few tokens as possible.

Goals in priority order:
1. Maximize token efficiency → downstream agents should almost never need to read the whole codebase at once
2. Enable true progressive disclosure of knowledge (metadata/summaries first → details on demand)
3. Make the high-level architecture, domain concepts, and important decisions instantly understandable
4. Preserve important context meaning that is usually lost when files are read in isolation

Create the following files in the project root (or in a new folder called LLM_CONTEXT/ if preferred). Use clear, markdown-heavy formats that are easy for LLMs to parse. Be concise but information-dense. Never duplicate information unnecessarily.

Files to generate (create all of them):

1. ARCHITECTURE.md
   - One-page (max 800–1200 tokens) overview of the system
   - Layers / modules / bounded contexts
   - Key design decisions, invariants, non-functional choices
   - Main data & control flows (use simple ASCII art or mermaid when helpful)
   - List of the 5–8 most architecturally significant files/classes/modules

2. CONTEXT_MAP.md
   - A "mental model" / glossary / domain dictionary
   - Core domain concepts, ubiquitous language, business rules that span files
   - Important type aliases / domain primitives and their meaning
   - Anti-patterns or "things we deliberately do not do here"

3. FILE_SUMMARIES.md or files_index.yaml
   - Table or structured list of EVERY .ts/.js/.py/.go/.rs/etc file in the project
   - Columns / keys: path, purpose (1 sentence), tokens (rough estimate), key types exported, main dependencies (incoming & outgoing), architectural role (entrypoint, domain, infra, glue, legacy, test…)
   - For very large projects (>300 files) prioritize and mark "core" vs "supporting" vs "generated"

4. ENTRY_POINTS.md
   - List and short description of the 5–10 most important "starting points" to understand the system
     (main(), CLI entry, HTTP handlers, background workers, tests that cover happy paths, etc.)

5. SKILLS/ or helpers/ folder containing small progressive-disclosure helper files, each ~200–600 tokens:
   - One file per major module / bounded context / layer
     Example names: auth-domain.md, payment-processing.md, reporting-engine.md, api-boundary.md
   - Each file contains:
     - 2–4 sentence summary
     - Key invariants & business rules
     - Most important 3–8 symbols (classes, functions, types) with 1–2 sentence role
     - References to other related context files
     - When to load this file / what questions make it relevant

6. PROGRESSIVE_DISCLOSURE_GUIDE.md (instructions for agents)
   - Explain the intended usage pattern:
     • First read ARCHITECTURE.md + CONTEXT_MAP.md + FILE_SUMMARIES.md
     • Then decide which 1–3 SKILLS/*.md files seem relevant
     • Only then read individual source files or run grep/search
   - Give example reasoning steps an agent should follow when starting a new task

Formatting & style rules:
- Use markdown, headings, tables, bullet lists, code blocks
- Prefer YAML inside markdown when structure is important
- Write in clear, declarative language — avoid fluff
- Use phrases like "Agents should only load this file when..." to guide future LLM behavior
- Include token estimates next to sections when possible ("≈220 tokens")
- Never lie or hallucinate — base everything strictly on code you actually see

Now analyze the entire codebase you have access to and generate all the files described above.

Current codebase location / files: [paste file tree here or use @filetree / @codebase tools if your interface supports it]

Begin by first giving a very brief 3–5 sentence summary of what the project appears to be, then proceed to generate the files one by one in order.
```