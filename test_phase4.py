import uuid
import asyncio
import sys
from database import db
from graph import create_graph

# Simple ANSI colors for output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BLUE = "\033[94m"

async def test_persistence():
    print(f"\n{BLUE}=== Running Test: Persistence ==={RESET}")
    
    # 1. Init DB
    await db.init_db()
    
    # 2. Start Session A
    session_id = "test_persistence_user_1"
    print(f"Session ID: {session_id}")
    
    app = create_graph()
    config = {"configurable": {"thread_id": session_id}}
    
    state_a = {
        "session_id": session_id,
        "user_id": "test_user",
        "conversation_history": [],
        "corrections": {},
        "messages": [],
        "session_active": True,
        "current_query": "My name is Blaze."
    }
    
    print("User: My name is Blaze.")
    async for event in app.astream(state_a, config=config):
        pass
    print("Bot: (Processed)")
    
    # 3. Simulate Restart / New Connection (Clear State)
    print("\n--- Simulating Restart (New process connecting to same DB) ---")
    
    state_b = {
        "session_id": session_id, # SAME SESSION ID
        "user_id": "test_user",
        "conversation_history": [], # Empty initial history
        "corrections": {},
        "messages": [],
        "session_active": True,
        "current_query": "What is my name?"
    }
    
    print("User: What is my name?")
    final_response = ""
    async for event in app.astream(state_b, config=config):
        for key, value in event.items():
            if "llm_responses" in value:
                final_response = value["llm_responses"][0]
                
    print(f"Bot Output: {final_response}")
    
    if "Blaze" in final_response:
        print(f"{GREEN}✔ Persistence Verified: Bot remembered the name.{RESET}")
    else:
        print(f"{RED}✘ FAILED: Bot did not remember.{RESET}")

    await db.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_persistence())
