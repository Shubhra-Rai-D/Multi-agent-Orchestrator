import sys
from dotenv import load_dotenv
load_dotenv()
from orchestrator import Orchestrator

def main():
    orc = Orchestrator()
    
    print("\n--- Test Suite 1: Single turn queries ---")
    test_queries = [
        "Show me Alice's open pull requests",
        "What issues are assigned to Bob in Linear?",
        "What's the weather today?",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"User: {query}")
        result = orc.process_query(query)
        print(f"System: {result}")

    print("\n--- Test Suite 2: Multi-turn flow (Action first, User second) ---")
    print(f"\n{'='*60}")
    print("User: show me repos")
    r1 = orc.process_query("show me repos")
    print(f"System: {r1}")
    print("User: Alice")
    r2 = orc.process_query("Alice")
    print(f"System: {r2}")

    print("\n--- Test Suite 3: Multi-turn flow (User first, Action second) ---")
    print(f"\n{'='*60}")
    print("User: Bob")
    r3 = orc.process_query("Bob")
    print(f"System: {r3}")
    print("User: what issues are assigned?")
    r4 = orc.process_query("what issues are assigned?")
    print(f"System: {r4}")
    
    print(f"\n{'='*60}")
    print("All tests completed!")

if __name__ == "__main__":
    main()

