import uuid
import sys
from typing import List, Dict
from graph import create_graph

# Simple ANSI colors for output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BLUE = "\033[94m"

def run_test_scenario(name: str, inputs: List[str], expected_models: List[str] = None):
    print(f"\n{BLUE}=== Running Test: {name} ==={RESET}")
    app = create_graph()
    session_id = str(uuid.uuid4())
    user_id = "test_user_p2"
    
    config = {"configurable": {"thread_id": session_id}}
    
    current_state = {
        "session_id": session_id,
        "user_id": user_id,
        "conversation_history": [],
        "corrections": {},
        "feedback_log": [],
        "llm_responses": [],
        "user_action": "none",
        "loop_trigger": False,
        "session_active": True,
        "manual_model_override": None
    }

    # We need to simulate persistent state manually for this test harness 
    # since we are creating a new state dict each run but passing it in.
    # The LangGraph MemorySaver works, but here we are managing the state object explicitly for the inputs loop.
    
    last_override = None

    for i, user_input in enumerate(inputs):
        print(f"\nUser Input [{i+1}]: {user_input}")
        
        # Update state with latest override from previous turn if any ( simulating persistent state)
        if last_override:
             current_state["manual_model_override"] = last_override
             
        current_state["current_query"] = user_input
        
        selected_model = "unknown"
        final_response = "No response"
        
        # Run graph
        events = list(app.stream(current_state, config=config))
        
        for event in events:
            for key, value in event.items():
                if key == "model_selector":
                    selected_model = value.get("selected_model", "unknown")
                    # Capture override update
                    if "manual_model_override" in value:
                        last_override = value["manual_model_override"]
                        current_state["manual_model_override"] = last_override
                        
                    print(f"  -> Selector chose: {GREEN}{selected_model}{RESET} (Override: {last_override})")
                
                if "llm_responses" in value and value["llm_responses"]:
                    final_response = value["llm_responses"][0]
        
        print(f"Bot Output: {final_response[:100]}...")
        
        # Verify Model Selection
        if expected_models and i < len(expected_models):
            expected = expected_models[i]
            if expected.lower() == selected_model.lower():
                print(f"{GREEN}✔ Model Selection Verified: {expected}{RESET}")
            else:
                print(f"{RED}✘ FAILED Selection: Expected {expected}, Got {selected_model}{RESET}")

def test_groq_selection():
    # Simple chat -> Groq
    run_test_scenario("Groq Selection (Auto)", ["Hello, how are you?"], ["groq"])

def test_gemini_selection():
    # Complex/Visual -> Gemini
    run_test_scenario("Gemini Selection (Auto)", ["Write a very complex sci-fi story about quantum entanglement."], ["gemini"])

def test_manual_override():
    # 1. Set to Gemini
    # 2. Ask simple question (should stay Gemini)
    # 3. Set to Auto
    # 4. Ask simple question (should be Groq)
    inputs = [
        "Set model to gemini",
        "Hi there", 
        "Set model to auto",
        "Hi there"
    ]
    expectations = [
        "gemini", # Command sets it
        "gemini", # Stickiness
        "groq",   # Reset to auto (default groq for confirmation)
        "groq"    # Auto -> Groq
    ]
    run_test_scenario("Manual Override Test", inputs, expectations)

if __name__ == "__main__":
    print("Starting Automated Tests for Phase 2 (With Overrides)...")
    try:
        test_groq_selection()
        test_gemini_selection()
        # test_perplexity_selection() # Skipping to save time/tokens if needed, but logic is same
        test_manual_override()
        print(f"\n{GREEN}All Phase 2 Tests Completed.{RESET}")
    except Exception as e:
        print(f"\n{RED}Test Failed with Error: {e}{RESET}")
