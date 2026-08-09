import sys
from orchestrator import Orchestrator
from utils.config import add_user, list_users

def main():
    print("Initializing StackGen Multi-Agent System...")
    try:
        orchestrator = Orchestrator()
    except Exception as e:
        print(f"Failed to initialize: {e}")
        print("Please ensure your .env file is set up correctly.")
        sys.exit(1)
        
    print("\nSystem ready! Type 'exit' or 'quit' to stop.")
    print("Commands:")
    print("  'add user'    — Register a new user (saved to database)")
    print("  'list users'  — Show all registered users")
    print("Example queries:")
    print("  'Show me Alice's open pull requests'")
    print("  'What issues are assigned to Bob in Linear?'")
    print("  'What's the weather today?'\n")
    
    while True:
        try:
            query = input("User: ").strip()
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break

            if query.lower() == 'add user':
                add_user()
                continue

            if query.lower() == 'list users':
                list_users()
                continue
                
            response = orchestrator.process_query(query)
            print(f"System: {response}\n")
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"System Error: {e}\n")

if __name__ == "__main__":
    main()
