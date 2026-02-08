# test_progressive_context.py
# Test script to validate the progressive context loading

from os_gateway import ContextManager
import json

def test_context_manager():
    """Test the ContextManager class."""
    
    print("Testing ContextManager...")
    print("=" * 60)
    
    # Initialize
    cm = ContextManager("context_files", 32768, 2000)
    
    print(f"\nScanned {len(cm.contexts)} contexts")
    for name, ctx in cm.contexts.items():
        print(f"  - {name}: {ctx['tokens']} tokens (priority: {ctx['priority']})")
    
    # Test 1: Load initial contexts for a basic query
    print("\n" + "=" * 60)
    print("Test 1: Basic query - 'list files in current directory'")
    print("=" * 60)
    
    contexts, tokens = cm.get_initial_contexts("list files in current directory")
    print(f"Loaded {tokens} tokens")
    print(cm.get_metrics())
    
    # Test 2: Request additional context
    print("\n" + "=" * 60)
    print("Test 2: Request additional context - ['skill']")
    print("=" * 60)
    
    new_contexts, new_tokens = cm.request_contexts(["skill"])
    print(f"Loaded {new_tokens} additional tokens")
    print(cm.get_metrics())
    
    # Test 3: Complex query
    print("\n" + "=" * 60)
    print("Test 3: Complex query - 'explain how you learn new skills'")
    print("=" * 60)
    
    # Reset for new test
    cm = ContextManager("context_files", 32768, 2000)
    contexts, tokens = cm.get_initial_contexts("explain how you learn new skills")
    print(f"Loaded {tokens} tokens")
    print(cm.get_metrics())


if __name__ == "__main__":
    test_context_manager()