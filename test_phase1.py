import uuid
import sys
from typing import List, Dict
from graph import create_graph

# Simple ANSI colors for output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def run_test_scenario(name: str, inputs: List[str], expected_keywords: List[List[str]]):
    print(f"\n{GREEN}=== Running Test: {name} ==={RESET}")
    app = create_graph()
    session_id = str(uuid.uuid4())
    user_id = "test_user"
    
    config = {"configurable": {"thread_id": session_id}}
    
    # We need to maintain state across steps manually if we aren't using the persistence checkpointer fully in this script's loop
    # But MemorySaver in create_graph should handle it per session_id
    
    current_state = {
        "session_id": session_id,
        "user_id": user_id,
        "conversation_history": [],
        "corrections": {},
        "feedback_log": [],
        "llm_responses": [],
        "user_action": "none",
        "loop_trigger": False,
        "session_active": True
    }

    for i, user_input in enumerate(inputs):
        print(f"\nUser Input [{i+1}]: {user_input}")
        current_state["current_query"] = user_input
        
        # We need to pass the *latest* state features if they aren't fully persisted by the in-memory checkpointer 
        # (MemorySaver persists, but we need to pass the dict in)
        # Actually, for MemorySaver, we just pass the input for the *next* turn? 
        # StateGraph with MemorySaver usually takes the update.
        
        # For simplicity in this test harness, we'll just re-feed the updated state if possible, 
        # or rely on the fact that input_session loads from the MOCK_DB.
        
        final_response = ""
        events = list(app.stream(current_state, config=config))
        
        for event in events:
            for key, value in event.items():
                # Capture the chat_llm response
                if "llm_responses" in value and value["llm_responses"]:
                    final_response = value["llm_responses"][0]
                    # Update our local tracker of history for the next input (though the MOCK_DB does this in nodes.py)
        
        print(f"Bot Output: {final_response}")
        
        # assertions
        if expected_keywords[i]:
            passed = any(keyword.lower() in final_response.lower() for keyword in expected_keywords[i])
            if passed:
                print(f"{GREEN}✔ Verified keyword '{expected_keywords[i]}'{RESET}")
            else:
                print(f"{RED}✘ FAILED: Expected '{expected_keywords[i]}' not found.{RESET}")

def test_memory():
    inputs = [
        "My name is TestUserBlaze.",
        "What is my name?"
    ]
    expectations = [
        [], # Don't care about first response
        ["TestUserBlaze", "Blaze"]
    ]
    run_test_scenario("Memory Retention", inputs, expectations)

def test_correction_explicit():
    inputs = [
        "What color is the sun?", # Bot might say White or Yellow
        "Correction: The sun is purple.",
        "What color is the sun?"
    ]
    expectations = [
        [],
        # The bot should regenerate immediately after correction, confirming it.
        # But wait, our flow loops back! So we get a response to "I corrected you..."
        ["Purple", "Correct"], 
        ["Purple"]
    ]
    run_test_scenario("Explicit Correction", inputs, expectations)

def test_correction_implicit():
    inputs = [
        "What is the capital of France?", # Paris
        "No, actually the capital is Mars.",
        "What is the capital of France?"
    ]
    expectations = [
        ["Paris"],
        ["Mars"], # Should acknowledge the correction
        ["Mars"]
    ]
    run_test_scenario("Implicit Correction", inputs, expectations)

if __name__ == "__main__":
    print("Starting Automated Tests for Phase 1...")
    try:
        test_memory()
        test_correction_explicit()
        test_correction_implicit()
        print(f"\n{GREEN}All Tests Completed.{RESET}")
    except Exception as e:
        print(f"\n{RED}Test Failed with Error: {e}{RESET}")
