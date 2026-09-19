**Analyze and Document Codebase for Agent Efficiency**

You are an expert software architect and codebase analyzer. Your task is to read the provided codebase and generate a set of lightweight, modular files that enable other AI agents to understand, navigate, and work with it efficiently.

**Input:** [Insert codebase path, GitHub repo, or zipped files here]

**Output Requirements:** Create these 6 files in the root directory:

1. **`CONTEXT.md`** (2KB max)

   - One-sentence project summary
   - Core business domain/problem solved
   - Key technologies/language versions
   - 3-5 most critical user workflows
   - High-level data flow diagram (ASCII)

2. **`ARCHITECTURE.md`** (3KB max)

   - Component diagram (ASCII or Mermaid)
   - Layered architecture overview
   - Key design patterns used
   - Critical dependencies/external services
   - Entry points and major APIs

3. **`PROGRESSIVE_DISCLOSURE/`** folder with:

   ```
   text├── README.md (overview + navigation map)
   ├── 01-overview.md (high-level only)
   ├── 02-core.md (business logic)
   ├── 03-data.md (models/DB flows)
   ├── 04-api.md (endpoints/services)
   └── 05-utils.md (helpers/config)
   ```

4. **`TOKEN_SAVER.json`**

   ```
   json{
     "quick_refs": {
       "add_user": "src/users/createUser.ts:42",
       "db_config": "config/database.ts",
       "main_entry": "src/index.ts"
     },
     "file_summaries": {
       "src/index.ts": "App bootstrap + routing setup",
       // ... top 20 files only
     },
     "search_tags": ["auth", "payment", "cache"]
   }
   ```

5. **`AGENT_GUIDE.md`** (1KB max)

   - How to progressively load context
   - Token-efficient query patterns
   - Common debugging paths
   - Code style conventions

6. **`CHANGELOG_CONTEXT.md`**

   - Last 3 releases + breaking changes
   - Migration guides for recent updates

**Constraints:**

- Total output < 15KB across all files
- Use Markdown tables/Mermaid for visuals
- Reference files by exact path:line
- Prioritize runtime-critical paths
- Write for AI agents (precise, scannable, no fluff)

**Generate all files now with full path structure.**