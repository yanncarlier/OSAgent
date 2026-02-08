# context_analyzer.py
# Helper script to analyze your context files and suggest optimizations

import json
from pathlib import Path
from collections import Counter
import re

CONTEXT_DIR = "context_files"

def analyze_contexts():
    """Analyze context files for keywords and suggest loading strategies."""
    
    context_dir = Path(CONTEXT_DIR)
    
    if not context_dir.exists():
        print(f"Directory {CONTEXT_DIR} not found!")
        return
    
    print("=" * 70)
    print("  Context File Analysis")
    print("=" * 70)
    
    total_tokens = 0
    contexts = []
    
    for file_path in sorted(context_dir.glob("*.md")):
        content = file_path.read_text(encoding='utf-8')
        
        # Token estimation
        tokens = len(content) // 4
        total_tokens += tokens
        
        # Extract keywords (simple approach)
        words = re.findall(r'\b[a-z]{4,}\b', content.lower())
        top_words = Counter(words).most_common(10)
        
        contexts.append({
            "name": file_path.stem,
            "tokens": tokens,
            "lines": len(content.split('\n')),
            "chars": len(content),
            "keywords": top_words
        })
        
        print(f"\n{file_path.stem.upper()}")
        print(f"  Tokens: ~{tokens}")
        print(f"  Lines: {len(content.split('\n'))}")
        print(f"  Top keywords: {', '.join([w[0] for w in top_words[:5]])}")
    
    print("\n" + "=" * 70)
    print(f"Total Tokens: ~{total_tokens}")
    print(f"Contexts: {len(contexts)}")
    print("=" * 70)
    
    # Suggest loading strategy
    print("\nRecommended Loading Strategy:")
    print("  1. Always load: identity (core personality)")
    print("  2. Load on-demand based on query keywords:")
    
    keyword_map = {
        "agent": ["execute", "command", "action", "task"],
        "tools": ["file", "system", "utility", "function"],
        "skill": ["learn", "ability", "capability", "training"],
        "heartbeat": ["status", "health", "monitor", "check"],
        "soul": ["purpose", "ethics", "values", "philosophy"]
    }
    
    for ctx, keywords in keyword_map.items():
        print(f"     - {ctx}: {', '.join(keywords)}")
    
    # Calculate progressive loading scenarios
    print("\n" + "=" * 70)
    print("Progressive Loading Scenarios:")
    print("=" * 70)
    
    scenarios = [
        (["identity"], "Minimal (identity only)"),
        (["identity", "agent"], "Basic operations"),
        (["identity", "agent", "tools"], "File/system tasks"),
        (["identity", "agent", "tools", "skill"], "Complex tasks"),
    ]
    
    for context_list, description in scenarios:
        scenario_tokens = sum(c["tokens"] for c in contexts if c["name"].lower() in context_list)
        utilization = (scenario_tokens / 32768) * 100
        print(f"\n{description}:")
        print(f"  Contexts: {', '.join(context_list)}")
        print(f"  Tokens: {scenario_tokens} ({utilization:.1f}% of budget)")
        print(f"  Remaining: {32768 - scenario_tokens} tokens for conversation")


if __name__ == "__main__":
    analyze_contexts()