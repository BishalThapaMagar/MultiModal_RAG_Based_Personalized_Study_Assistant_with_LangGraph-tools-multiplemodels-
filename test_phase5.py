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

async def test_rag():
    print(f"\n{BLUE}=== Running Test: RAG (Phase 5) ==={RESET}")
    
    # 1. Init DB (ensure vector extension is there)
    await db.init_db()
    
    app = create_graph()
    session_id = str(uuid.uuid4())
    user_id = "rag_test_user"
    
    config = {"configurable": {"thread_id": session_id}}
    
    state = {
        "session_id": session_id,
        "user_id": user_id,
        "conversation_history": [],
        "corrections": {},
        "messages": [],
        "session_active": True,
        "manual_model_override": "groq", # Force Groq to ensure tools are bound
        # Question that requires RAG from sample.txt
        "current_query": "What is the capital of Mars?" 
    }
    
    print(f"User: {state['current_query']}")
    final_response = ""
    tool_executed = False
    
    async for event in app.astream(state, config=config):
        for key, value in event.items():
            if key == "tools":
                print(f"  -> {GREEN}Tool Executed (Retrieval)!{RESET}")
                tool_executed = True
                
            if "llm_responses" in value and value["llm_responses"]:
                final_response = value["llm_responses"][0]
                
    print(f"Bot Output: {final_response}")
    
    if "ElonCity" in final_response:
        print(f"{GREEN}✔ RAG Verified: Answered 'ElonCity'.{RESET}")
    else:
        print(f"{RED}✘ FAILED: Did not find 'ElonCity' in answer.{RESET}")

    if tool_executed:
         print(f"{GREEN}✔ Tool Call Verified.{RESET}")
    else:
         print(f"{RED}✘ Tool Not Called.{RESET}")

    await db.close()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_rag())
