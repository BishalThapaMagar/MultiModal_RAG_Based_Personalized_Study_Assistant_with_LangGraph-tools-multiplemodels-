import sys
from typing import Dict, Any
from ai_services.GroqClient import generate_completion
from ai_services.GeminiClient import call_gemini
from ai_services.PerplexityClient import call_perplexity_chat
from state import AgentState
from langgraph.prebuilt import ToolNode
from tools import ALL_TOOLS
from database import db

# Create Tool Node
tools_node = ToolNode(ALL_TOOLS) 

async def input_session(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Input & Session
    Initialize state, load session history and corrections from DB.
    """
    session_id = state.get("session_id")
    print(f"--- Node: input_session (Session: {session_id}) ---")
    
    # Initialize DB Session
    await db.create_session_if_not_exists(session_id, user_id=state.get("user_id", "guest"))
    
    # Load history and corrections
    history = await db.get_session_history(session_id)
    all_corrections = await db.get_all_corrections()
    
    return {
        "conversation_history": history, 
        "corrections": all_corrections,
        "session_active": True
    }

def model_selector(state: AgentState) -> Dict[str, Any]:
    """
    Node 2: Model Selector
    Analyze query to select the best model.
    Handles manual overrides.
    """
    print("--- Node: model_selector ---")
    query = state["current_query"].lower()
    current_override = state.get("manual_model_override")
    
    # 1. Check for commands to SWITCH modes
    new_override = None
    if "set model" in query or "use model" in query or "switch to" in query:
        if "groq" in query:
            new_override = "groq"
        elif "gemini" in query:
            new_override = "gemini"
        elif "perplexity" in query:
            new_override = "perplexity"
        elif "auto" in query:
            new_override = "auto" 
    
    if new_override:
        if new_override == "auto":
            print("--- Model Selector: Switched to AUTO mode ---")
            return {"manual_model_override": None, "selected_model": "groq"} 
        else:
            print(f"--- Model Selector: Manual Override set to {new_override} ---")
            return {"manual_model_override": new_override, "selected_model": new_override}

    # 2. Use Override
    if current_override and current_override in ["groq", "gemini", "perplexity"]:
        return {"selected_model": current_override}

    # 3. Auto Selection
    system_message = """You are a router. Select the best AI model.
    1. groq: Simple chat, greetings.
    2. gemini: Visual, complex, creative.
    3. perplexity: News, search, facts.
    Return ONLY: "groq", "gemini", or "perplexity"."""
    
    try:
        selection = generate_completion(state["current_query"], system_message).strip().lower()
        if selection not in ["groq", "gemini", "perplexity"]:
            selection = "groq"
        print(f"--- Model Selected: {selection} ---")
        return {"selected_model": selection}
    except Exception as e:
        print(f"Selector Error: {e}, defaulting to groq")
        return {"selected_model": "groq"}

async def chat_llm(state: AgentState) -> Dict[str, Any]:
    """
    Node 3: Chat LLM Generation
    Generate response using Selected Model (with Tools).
    Saves message to DB.
    """
    print("--- Node: chat_llm ---")
    query = state["current_query"]
    model_name = state.get("selected_model", "groq")
    history = state.get("conversation_history", [])
    corrections = state.get("corrections", {})
    
    # Prepare Tools & Model
    from langchain_groq import ChatGroq
    from langchain_google_genai import ChatGoogleGenerativeAI
    import os
    
    llm = None
    if model_name == "gemini":
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"))
    elif model_name == "perplexity":
        # Placeholder for Perplexity
        pass 
    else:
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
    
    if llm:
        llm_with_tools = llm.bind_tools(ALL_TOOLS)
    
    # Construct Messages
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    
    messages = [SystemMessage(content="You are a helpful AI assistant.")]
    if corrections:
        corr_text = "\n\nPREVIOUS USER CORRECTIONS (Apply these strictly):"
        for q_hash, correction in corrections.items():
            corr_text += f"\n- {correction}"
        messages[0].content += corr_text
        
    for msg in history[-1000:]: 
        if msg['role'] == 'user':
            messages.append(HumanMessage(content=msg['content']))
        elif msg['role'] == 'assistant':
            messages.append(AIMessage(content=msg['content']))
            
    messages.append(HumanMessage(content=query))
    
    # Invoke
    response_msg = None
    if llm:
        try:
            # Async invoke if possible, or fall back to sync invoke if client doesn't support async properly yet
            # LangGraph handles async nodes well.
            response_msg = await llm_with_tools.ainvoke(messages)
        except Exception as e:
            response_msg = AIMessage(content=f"Error calling LLM: {str(e)}")
    else:
        response_msg = AIMessage(content="Perplexity/Other model response placeholder (No Tools)")

    message_content = response_msg.content if response_msg.content else ""
    
    session_id = state["session_id"]
    await db.save_message(session_id, "user", query)
    if message_content and not response_msg.tool_calls:
         # Only save text responses, tool calls are intermediate steps usually?
         # Or save them too? For persistence, we probably want the final answer.
         # For now, save if content exists.
        await db.save_message(session_id, "assistant", message_content)

    return {
        "llm_responses": [message_content],
        "conversation_history": [
            {"role": "user", "content": query},
            {"role": "assistant", "content": message_content}
        ],
        "messages": [response_msg],
        "user_action": "satisfied"
    }

async def feedback_correction(state: AgentState) -> Dict[str, Any]:
    """
    Node 4: Feedback & Correction
    Process feedback and update global corrections DB.
    """
    print("--- Node: feedback_correction ---")
    query = state["current_query"]
    
    # Parse implicit correction
    correction_text = query.replace("correction:", "").strip()
    
    history = state.get("conversation_history", [])
    last_user_query = "unknown_query"
    if len(history) >= 2:
        last_user_query = history[-2]["content"] 
    
    # Save to DB
    await db.add_correction(last_user_query, correction_text)
    
    print(f"--- Correction Applied for: '{last_user_query}' ---")
    
    return {
        "current_query": f"The user corrected the previous answer to '{last_user_query}'. Correction: {correction_text}. Please provide the correct answer now.", 
        "corrections": {last_user_query: correction_text}
    }

def corrected_output(state: AgentState) -> Dict[str, Any]:
    return {} # Unused

def analyze_intent(state: AgentState) -> str:
    """
    Router Logic: Analyze user intent using LLM.
    Returns: "chat_llm" or "feedback_correction"
    """
    query = state["current_query"]
    history = state.get("conversation_history", [])
    
    if not history:
        return "chat_llm"
        
    context_str = ""
    for msg in history[-2:]:
        context_str += f"{msg['role']}: {msg['content']}\n"
        
    system_message = """You are a router. Classify:
1. QUERY: New question.
2. CORRECTION: Feedback/Correction to previous answer.
Return "QUERY" or "CORRECTION"."""

    prompt = f"History:\n{context_str}\nUser: {query}\nClassification:"

    try:
        classification = generate_completion(prompt, system_message).strip().upper()
        print(f"--- Router Classification: {classification} ---")
        
        if "CORRECTION" in classification:
            return "feedback_correction"
        else:
            return "chat_llm"
            
    except Exception as e:
        print(f"Router Error: {e}, defaulting to chat")
        return "chat_llm"
