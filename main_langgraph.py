import asyncio
import uuid
import sys
from graph import create_graph
from database import db

async def main():
    print("Initializing LangGraph Chatbot (Phase 4: Persistence)...")
    
    # Initialize Database
    try:
        await db.init_db()
    except Exception as e:
        print(f"Database Initialization Failed: {e}")
        print("Please check your .env file and ensure DATABASE_URL is set.")
        return

    # Initialize Graph
    app = create_graph()
    
    # Generate Session ID
    session_id = str(uuid.uuid4())
    print(f"Session ID: {session_id}")
    print("Type 'exit' to quit.")
    
    config = {"configurable": {"thread_id": session_id}}
    
    # Initial State
    current_state = {
        "session_id": session_id,
        "user_id": "cli_user",
        "conversation_history": [],
        "corrections": {},
        "manual_model_override": None,
        "messages": [],
        "session_active": True
    }
    
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                await db.close()
                break
            
            print("Processing...")
            current_state["current_query"] = user_input
            
            # Stream events
            # We use astream for async execution
            async for event in app.astream(current_state, config=config):
                for key, value in event.items():
                    # Handle node outputs...
                    if key == "chat_llm":
                        if "llm_responses" in value and value["llm_responses"]:
                            print(f"Assistant: {value['llm_responses'][0]}")
                    
                    if key == "feedback_correction":
                         print(f"System: Correction received. Regenerating...")

                    if value:
                        current_state.update(value)

        except KeyboardInterrupt:
            print("\nExiting...")
            await db.close()
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
