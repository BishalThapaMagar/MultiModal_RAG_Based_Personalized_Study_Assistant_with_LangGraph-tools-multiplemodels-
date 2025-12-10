import uuid
import sys
from typing import List
from graph import create_graph

# Simple ANSI colors for output
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
BLUE = "\033[94m"

def run_test_scenario(name: str, inputs: List[str], expected_tools: List[str] = None):
    print(f"\n{BLUE}=== Running Test: {name} ==={RESET}")
    app = create_graph()
    session_id = str(uuid.uuid4())
    user_id = "test_user_p3"
    
    config = {"configurable": {"thread_id": session_id}}
    
    current_state = {
        "session_id": session_id,
        "user_id": user_id,
        "conversation_history": [],
        "corrections": {},
        "manual_model_override": None,
        "llm_responses": [],
        "messages": [], # Important for tools
        "session_active": True
    }

    for i, user_input in enumerate(inputs):
        print(f"\nUser Input [{i+1}]: {user_input}")
        current_state["current_query"] = user_input
        
        tool_called = False
        final_response = "No response"
        
        events = list(app.stream(current_state, config=config))
        
        for event in events:
            for key, value in event.items():
                if key == "tools":
                    print(f"  -> {GREEN}Tool Executed!{RESET}")
                    tool_called = True
                
                if "llm_responses" in value and value["llm_responses"]:
                    final_response = value["llm_responses"][0]
        
        print(f"Bot Output: {final_response[:150]}...")
        
        # Verify Tool Execution
        if expected_tools and i < len(expected_tools):
            expected = expected_tools[i]
            if expected == "yes" and tool_called:
                print(f"{GREEN}✔ Tool Call Verified{RESET}")
            elif expected == "no" and not tool_called:
                print(f"{GREEN}✔ Verified No Tool Call{RESET}")
            else:
                print(f"{RED}✘ FAILED: Expected Tool Call {expected}, Got {tool_called}{RESET}")

def test_ppt_generation():
    # Should trigger generate_presentation_tool
    # Note: Groq might be used, or we might need to force Gemini if Groq tool calling is unstable
    run_test_scenario("PPT Generation", 
                      ["Create a 3-slide presentation about Space Exploration."], 
                      ["yes"])

def test_normal_chat():
    run_test_scenario("Normal Chat", 
                      ["What is the capital of Japan?"], 
                      ["no"])

if __name__ == "__main__":
    print("Starting Automated Tests for Phase 3 (Tools)...")
    try:
        test_ppt_generation()
        test_normal_chat()
        print(f"\n{GREEN}All Phase 3 Tests Completed.{RESET}")
    except Exception as e:
        print(f"\n{RED}Test Failed with Error: {e}{RESET}")
