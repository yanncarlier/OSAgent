# Progressive Disclosure Guide

## Intended Usage Pattern
Agents should follow this sequence when approaching the OSAgent codebase:

### Phase 1: High-Level Understanding (Read First)
1. **ARCHITECTURE.md** (~600 tokens) - Understand system purpose, components, and data flows
2. **CONTEXT_MAP.md** (~500 tokens) - Learn domain concepts, ubiquitous language, and key primitives
3. **FILE_SUMMARIES.md** (~400 tokens) - Get inventory of all files with purpose and roles

*Total for Phase 1: ≈1,500 tokens*

### Phase 2: Targeted Detail (Read Next)
Based on your task, select 1-3 relevant SKILLS/*.md files:
- **Agent-related tasks** (conversation flow, knowledge injection, tool use): `agent-domain.md`
- Each skill file: ≈250-350 tokens

*Total for Phase 2: ≈250-350 tokens*

### Phase 3: Source Code (Read Last)
Only read specific source files when:
- You need to see exact implementation details
- The skill files don't contain sufficient information
- You're modifying or extending specific functionality

Start with entry points from `ENTRY_POINTS.md` then navigate to related files.

## Example Reasoning Steps

### Scenario: Debugging Command Execution Failure
1. Read **ARCHITECTURE.md** to understand agent orchestration
2. Read **CONTEXT_MAP.md** for security boundaries and tool use protocol
3. Read **FILE_SUMMARIES.md** to locate command execution components
4. Select **agent-domain.md** (covers TerminalTool and security)
5. From agent-domain.md, learn:
   - Command execution happens in `TerminalTool.execute()`
   - Safety filtering blocks high-risk commands
   - Output format includes exit codes and stderr
6. Read `main.py:TerminalTool.execute()` to see implementation
7. Check logs in `logs/` directory for actual command output
8. Verify command isn't blocked by safety filter
9. Examine timeout or permission issues

### Scenario: Adding Specialized Knowledge
1. Read **ARCHITECTURE.md** to see where knowledge injection occurs
2. Read **CONTEXT_MAP.md** for knowledge base structure concepts
3. Read **FILE_SUMMARIES.md** to locate knowledge management code
4. Select **agent-domain.md** (covers ContextManager and knowledge base)
5. From agent-domain.md, learn:
   - Knowledge base is `KNOWLEDGE_BASE` dictionary in `main.py`
   - Each entry needs `description`, `triggers` (list), and `content`
   - Triggers are matched against lowercased user input
6. Read `main.py:ContextManager.get_relevant_context()` to see matching logic
7. Add new entry to `KNOWLEDGE_BASE` in `main.py`
8. Choose appropriate trigger keywords
9. Write specialized content to inject when triggers match

## Key Principles
- **Start Broad, Go Deep**: Always begin with high-level context before diving into source
- **Match Context to Task**: Only load skill files relevant to your current goal
- **Leverage Existing Patterns**: Extend the system by following established conventions
- **Respect Boundaries**: Understand security and design constraints before modifying
- **Trace the Flow**: Use entry points and data flows to navigate between components

## Token Efficiency Tips
- A single skill file (~300 tokens) often contains sufficient information for common tasks
- Combining ARCHITECTURE.md + CONTEXT_MAP.md + one skill file (<1,200 tokens) covers most scenarios
- Only exceed 2,000 tokens when deep implementation details are truly necessary