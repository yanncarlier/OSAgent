# Codebase Intelligence Prompt

# Feed this to any capable agent alongside your codebase (or a file tree + key files).

# The agent will produce a set of context files optimized for meaning, progressive

# disclosure, architecture documentation, and token-efficient agent consumption.

------

## SYSTEM CONTEXT

You are a senior software architect performing a deep read of a codebase. Your job is NOT to summarize what you see line by line. Your job is to extract durable, structured knowledge that helps both humans and AI agents work effectively in this codebase — at varying levels of detail — using the fewest tokens that still preserve full meaning.

You will produce exactly the files listed below. Do not skip any. Do not add extras. Each file has a strict purpose and a strict format. Follow them precisely.

------

## OUTPUT FILES TO PRODUCE

### 1. `OVERVIEW.md`

**Purpose:** Single-page orientation. A new engineer or a new agent reads this first. **Token budget:** 400–600 tokens max. Every sentence must earn its place.

Sections (use these exact headings):

```
## What this system does
One paragraph. What problem does it solve? Who uses it? What is the core value?
No implementation details here.

## Primary user flows
Numbered list. Maximum 5 flows. Each flow = one sentence describing the journey from
trigger to outcome (e.g. "User submits form → validated → stored → confirmation email sent").
Name the key components touched, but don't explain them yet.

## Tech stack
Bullet list. Group by layer: Runtime | Framework | Persistence | Infrastructure | Key libs.
One line per item. Format: `name` — why it was chosen or what role it plays.

## Where to start reading
3–5 entry points. For each: file path + one sentence on what it controls.
These should be the files that, if understood, unlock understanding of everything else.

## What is intentionally NOT here
Any known gaps, deferred features, or out-of-scope concerns. Prevents agents from
searching for things that don't exist.
```

------

### 2. `ARCHITECTURE.md`

**Purpose:** Structural map of the system. Modules, their responsibilities, their boundaries, and how data flows between them. **Token budget:** 800–1400 tokens. Precision over prose.

Sections:

```
## Module map
Table with columns: Module | Path(s) | Responsibility | Owns | Depends on
"Owns" = what data or state this module is the authority over.
"Depends on" = other modules it calls directly (not libraries).
List every top-level module or service. If a module is large, break it into sub-rows
with indentation.

## Data flow
For each primary user flow from OVERVIEW.md, a compact trace:
  Flow name → ComponentA → ComponentB (what is passed) → ComponentC → output
Use arrows (→). Keep each trace to one or two lines. No prose.

## Boundary rules
What is NOT allowed to cross between modules? What patterns enforce this?
(e.g. "Persistence layer is never imported by UI components", "Events only flow via
the message bus, never direct function calls across services")
These rules are the most valuable thing an agent can know — they prevent hallucinated
architectures.

## Key abstractions
The 5–10 types, interfaces, or patterns that everything else is built on.
For each: name, brief definition, where it is defined, canonical usage example (one line).

## Known design decisions (ADR-lite)
For each significant past decision: Decision | Why | What was rejected.
Maximum 5. Only decisions that would confuse a reader who doesn't know the history.
```

------

### 3. `modules/` directory — one file per module

**Purpose:** Deep-dive context for a specific module. An agent working only in this module loads only this file. **Token budget per file:** 300–500 tokens.

Filename: `modules/{module-name}.md`

Template for each file:

```
## {Module name}

**Role:** One sentence.
**Entry point:** Path to the main file or index.
**Public API:** List every exported function/class/hook that other modules call.
  Format: `functionName(param: Type): ReturnType` — what it does in ≤8 words.
**Internal structure:** Paragraph. How is this module organized internally?
  What are its main internal concepts? What does it NOT do?
**State / side effects:** What does this module mutate or persist?
  What external services does it call? What events does it emit?
**Error handling contract:** How does it signal failure? (throws / returns Result /
  emits error event / logs and swallows). What should callers expect?
**Common pitfalls:** 2–3 bullet points. Things that trip up people working here.
  Real mistakes, not generic warnings.
**Tests:** Where are they? What is and isn't covered?
```

Produce one file per top-level module identified in `ARCHITECTURE.md`.

------

### 4. `GLOSSARY.md`

**Purpose:** Shared vocabulary. Eliminates ambiguity across all other files and across agent/human communication. **Token budget:** 200–400 tokens.

Format:

```
## Domain terms
Terms specific to the business domain (not the tech stack).
Format: **term** — definition. Note any synonyms or common confusions.

## Codebase-specific terms
Names invented inside this project (custom patterns, internal names for standard concepts,
abbreviations used in variable names).
Format: **term** — what it means here, where it comes from, example usage.

## Dangerous homonyms
Words used in this codebase that mean something different from their common industry
meaning. (e.g. "user" here means an API key owner, not a human end-user.)
```

------

### 5. `AGENTS.md`

**Purpose:** The file an AI agent loads when it needs to understand this codebase quickly and completely — in as few tokens as possible. **This is the most important file for token savings.** **Token budget:** 500–700 tokens. Ruthless compression. No filler.

This file is a curated synthesis, not a summary of the other files. Write it as if you were briefing a highly capable agent who has zero context and exactly one chance to read something before acting.

Sections:

```
## System identity
Two sentences. What this system is and what its core invariant is
(the one thing that must always be true).

## Must-know facts
Numbered list. Maximum 10. Each fact = one sentence.
These are the facts that, if an agent doesn't know them, it will make architectural
mistakes. Prioritize non-obvious facts over obvious ones.

## Module quick-ref
Table: Module | Owns | Do not touch unless...
"Do not touch unless" = the condition that makes it appropriate to edit this module.
This prevents agents from making changes in the wrong layer.

## Patterns in use
Bullet list. For each pattern: name → where it's used → what problem it solves → one-line example.
Only patterns that appear 3+ times in the codebase. Skip one-offs.

## Red lines
What must never happen? Invariants that, if broken, cause cascading failure.
Format: ❌ [action] because [consequence].
Maximum 6 items.

## Agent task routing
For common task types, which module(s) to touch:
  - Add a new API endpoint → ...
  - Add a new UI page → ...
  - Change a data model → ...
  - Add a background job → ...
  - Modify auth/permissions → ...
Fill in only the task types that apply to this codebase.
```

------

### 6. `COMPACT.txt`

**Purpose:** Ultra-compressed snapshot. Used as a prefix in token-constrained prompts or when an agent needs full-system awareness in < 300 tokens. **Token budget:** 200–280 tokens hard cap. Plain text, no markdown.

Format rules:

- No headers. No bullet markers. Just dense, structured prose.
- Every sentence carries unique information. No sentence can be removed without losing something an agent would need.
- Use abbreviations where they are unambiguous in context.
- Omit all examples. State facts, not explanations.
- Write for an LLM reader, not a human reader. Optimize for recall, not readability.

Start with: `SYSTEM: [name]. [one-line purpose]. Stack: [comma list].` Then cover: module boundaries, key abstractions, red lines, task routing hints. End with: `Detailed context: AGENTS.md > ARCHITECTURE.md > modules/*.md`

------

## QUALITY RULES (apply to all files)

1. **No padding.** Every sentence must carry information not present in any other sentence in the same file. If you find yourself writing "as mentioned above" or restating something, delete it.
2. **Concrete over abstract.** Prefer `UserService calls AuthClient.verify() before returning` over `authentication is handled by the auth layer`.
3. **Name real things.** Use actual file paths, actual function names, actual type names. Vague descriptions are useless to agents.
4. **Flag uncertainty.** If you are not sure about something, write `[UNVERIFIED]` before the claim. Do not omit uncertain information — flag it instead.
5. **Progressive disclosure hierarchy must hold.** A fact that belongs in `COMPACT.txt` must also appear (with more detail) in `AGENTS.md`, which must also appear (with full detail) in `ARCHITECTURE.md` or a `modules/` file. Never put a fact in a lower-detail file that isn't traceable to a higher-detail file.
6. **Boundaries are the most valuable information.** What modules do NOT do, what data does NOT flow where, what patterns are NOT used — these negative facts save agents the most tokens by eliminating entire search paths.
7. **Token counts are hard limits.** If you exceed a file's token budget, cut content rather than compressing grammar. Meaning is more important than completeness.

------

## EXECUTION INSTRUCTIONS

1. Begin by reading the entire codebase (or file tree + representative files provided).
2. Before writing any file, produce a private scratchpad block listing:
   - All top-level modules identified
   - All primary user flows identified
   - All key abstractions identified
   - Any ambiguities or gaps flagged with [UNVERIFIED]
3. Write files in this order: GLOSSARY.md → OVERVIEW.md → ARCHITECTURE.md → modules/*.md → AGENTS.md → COMPACT.txt (Each file builds on the vocabulary and understanding of the previous ones.)
4. After all files are written, do a single pass: read COMPACT.txt, then AGENTS.md. If anything in AGENTS.md contradicts COMPACT.txt, fix COMPACT.txt. If anything in AGENTS.md is missing from the modules/*.md files, add it.

Begin when the codebase is provided.