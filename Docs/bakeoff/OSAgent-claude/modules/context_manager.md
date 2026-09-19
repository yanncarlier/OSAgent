## Context Manager

**Role:** Injects specialized knowledge into LLM context based on input triggers.
**Entry point:** main.py:ContextManager class
**Public API:** 
  get_relevant_context(user_input: str) -> str — Returns relevant knowledge snippets based on triggers in input
**Internal structure:** Static utility class that scans user input for predefined triggers and returns corresponding knowledge base content. Uses the embedded KNOWLEDGE_BASE dictionary which maps trigger words to specialized context snippets.
**State / side effects:** Stateless utility - owns no persistent state. Reads only from the KNOWLEDGE_BASE (does not modify it during runtime). No external side effects.
**Error handling contract:** 
  - Returns empty string if no triggers match (no error condition)
  - Does not throw exceptions - always returns a string (possibly empty)
  - Handles missing keys in KNOWLEDGE_BASE gracefully (would return empty string for that section)
**Common pitfalls:** 
  - Trigger matching is case-insensitive but exact substring matching (no stemming or synonyms)
  - Multiple matching triggers result in concatenated knowledge snippets (can lead to very long context)
  - Knowledge base is embedded in code - changes require modifying the source
  - No mechanism to prioritize or limit the amount of context injected
**Tests:** No explicit tests. Can be verified by calling get_relevant_context with various inputs and checking returned knowledge snippets.