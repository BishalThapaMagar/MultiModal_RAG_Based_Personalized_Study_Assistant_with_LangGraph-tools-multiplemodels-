from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from langgraph.prebuilt import tools_condition
from nodes import input_session, chat_llm, feedback_correction, corrected_output, analyze_intent, model_selector, tools_node

def create_graph():
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("input_session", input_session)
    workflow.add_node("model_selector", model_selector)
    workflow.add_node("chat_llm", chat_llm)
    workflow.add_node("tools", tools_node) # NEW
    workflow.add_node("feedback_correction", feedback_correction)
    workflow.add_node("corrected_output", corrected_output)
    
    # Set Entry Point
    workflow.set_entry_point("input_session")
    
    # Add Edges
    # Flow: input -> (conditional) -> model_selector (QUERY) OR feedback_correction (CORRECTION)
    # Then model_selector -> chat_llm
    
    workflow.add_conditional_edges(
        "input_session",
        analyze_intent,
        {
            "chat_llm": "model_selector", 
            "feedback_correction": "feedback_correction"
        }
    )
    
    workflow.add_edge("model_selector", "chat_llm")
    
    # Chat LLM -> Tools (if called) OR End
    workflow.add_conditional_edges(
        "chat_llm",
        tools_condition,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # Tool -> Chat LLM (to generate final response based on tool output)
    workflow.add_edge("tools", "chat_llm")
    
    # Correction Loop
    workflow.add_edge("feedback_correction", "model_selector") 
    
    # Compile
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    return app
