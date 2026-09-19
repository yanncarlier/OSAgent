> **Task:**
>  Analyze the provided codebase and generate a set of files to improve **context understanding, progressive disclosure, software architecture documentation, and token efficiency** for agents (e.g., LLMs, developers, or automation tools).
>
> **Deliverables:**
>  Create the following files in Markdown or a structured format:
>
> 1. **Context Meaning Guide (`CONTEXT.md`)**
>    - **Purpose:** Explain the high-level purpose, domain, and key concepts of the codebase.
>    - **Content:**
>      - Overview of the project’s goals and scope.
>      - Glossary of domain-specific terms, acronyms, and jargon.
>      - Key entities, data models, and their relationships.
>      - Examples of typical workflows or user journeys.
>      - "Why" behind major design decisions (e.g., architectural trade-offs).
> 2. **Progressive Disclosure Guide (`PROGRESSIVE_DISCLOSURE.md`)**
>    - **Purpose:** Help users (or agents) navigate the codebase incrementally, revealing complexity only as needed.
>    - **Content:**
>      - A hierarchical map of the codebase (e.g., modules, layers, or features).
>      - "Start here" sections for common tasks (e.g., "Adding a new API endpoint").
>      - "Deep dive" sections for advanced topics, hidden behind collapsible sections or links.
>      - FAQs for common pitfalls or misunderstandings.
>      - Suggested reading paths for different roles (e.g., frontend dev, backend dev, DevOps).
> 3. **Software Architecture Diagram and Notes (`ARCHITECTURE.md`)**
>    - **Purpose:** Visualize and document the architecture for clarity and maintainability.
>    - **Content:**
>      - High-level architecture diagram (e.g., C4 model, layer diagram).
>      - Component interaction flowcharts (e.g., sequence diagrams for critical paths).
>      - Data flow and dependency graphs.
>      - Infrastructure overview (if applicable).
>      - Justification for major architectural choices (e.g., microservices vs. monolith).
> 4. **Token-Saving Summaries (`SUMMARIES/` directory)**
>    - **Purpose:** Reduce token usage for agents by providing concise, structured summaries.
>    - **Content:**
>      - One-sentence descriptions for each file/module (e.g., `// SUMMARY: Handles user authentication and JWT token generation`).
>      - Key function/class summaries (input/output, purpose, edge cases).
>      - Pre-generated "TL;DR" sections for complex logic or algorithms.
>      - Example: "Token-efficient" code comments for critical sections (e.g., `// @PURPOSE: Validates input and throws Error if invalid`).
> 5. **Agent-Specific Cheat Sheet (`AGENT_CHEAT_SHEET.md`)**
>    - **Purpose:** Optimize for LLM/agent consumption.
>    - **Content:**
>      - Common patterns and anti-patterns in the codebase.
>      - "Do’s and Don’ts" for modifying the code (e.g., "Always use `validateInput()` before database calls").
>      - Pre-formatted snippets for typical agent tasks (e.g., "How to add a new API route").
>      - Token-saving tips (e.g., "Use `getUserById(id)` instead of querying the DB directly").
>
> **Guidelines:**
>
> - Use **clear, jargon-free language** where possible.
> - Prioritize **actionable information** over exhaustive detail.
> - Include **examples** (e.g., code snippets, diagrams, or analogies).
> - Flag **areas of technical debt** or known pain points.
> - Assume the reader (or agent) is **intelligent but unfamiliar** with the codebase.
>
> **Format:**
>
> - Use Markdown for readability.
> - Embed diagrams as Mermaid.js or PlantUML code blocks.
> - Keep files modular (e.g., split by topic or component).
>
> **Output:**
>  Provide the files as separate Markdown documents, ready to be placed in the codebase’s `docs/` directory.