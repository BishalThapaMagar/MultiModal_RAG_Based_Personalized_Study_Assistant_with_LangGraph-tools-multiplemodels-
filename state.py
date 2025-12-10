from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator

class AgentState(TypedDict):
    # Session Management
    session_id: str
    user_id: str
    selected_model: str # "groq", "gemini", "perplexity" (default: groq)
    manual_model_override: str | None # If set, forces specific model
    
    # Conversation Data
    conversation_history: Annotated[List[Dict[str, str]], operator.add]
    current_query: str
    llm_responses: List[str]
    
    # LangChain Messages (for Tool Calling)
    messages: Annotated[List[Any], operator.add]
    
    # Feedback & Corrections (Mock for Phase 1)
    corrections: Dict[str, str] # query_hash -> corrected_answer
    feedback_log: List[Dict[str, Any]]
    
    # Control Flow
    user_action: str # "satisfied", "corrects", "switch_model"
    loop_trigger: bool
    session_active: bool
