# MajorProject_aiCore (LangGraph Edition)

This project is an advanced conversational AI agent built with **LangGraph**, designing for robustness, persistence, and multi-modal capabilities. It orchestrates multiple LLMs (Groq, Gemini, Perplexity) and integrates various tools for education and content creation.

## Key Features

*   **langGraph Architecture**: A cyclic state-based graph managing the conversation flow, replacing linear chains.
*   **Persistent Memory**: Uses **PostgreSQL** to store session history and user corrections, ensuring continuity across server restarts.
*   **Multi-Model Intelligence**:
    *   **Router**: Automatically selects the best model for the query (or user can manually override).
    *   **Groq (Llama 3)**: Fast, general-purpose chat.
    *   **Gemini (Google)**: Complex reasoning and tool usage.
    *   **Perplexity**: Real-time web search and current events.
*   **Intelligent Tool Use**:
    *   **RAG (Retrieval-Augmented Generation)**: Uses **ChromaDB** to index and retrieve information from local documents (`knowledge_base/`).
    *   **Presentation Generator**: Creates PowerPoint slides (`generate_presentation_tool`).
    *   **Quiz Generator**: Creates quizzes from PDFs (`generate_quiz_tool`).
*   **Self-Correction**: Dedicated feedback loop where the agent learns from user corrections and saves them to the database.

## 🛠️ Architecture

The system is defined in `graph.py` as a `StateGraph`:
1.  **Input Node**: Loads session history and corrections from PostgreSQL.
2.  **Intent Analysis**: Routes to either `Chat` or `Correction` handling.
3.  **Model Selector**: Chooses the LLM (Groq/Gemini/Perplexity).
4.  **Chat LLM**: Invokes the selected model. If the model requests a tool, the **ToolNode** executes it and loops back.
5.  **Persistence**: All interactions are saved to `ai_chat_db`.

## Setup & Installation

### 1. Prerequisites
*   Python 3.10+
*   **PostgreSQL** installed and running.
*   **C++ Build Tools** (for ChromaDB on Windows).

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Setup
1.  Create a PostgreSQL database named `ai_chat_db`:
    ```bash
    createdb ai_chat_db
    ```
2.  Configure `.env` file:
    ```env
    # LLM API Keys
    GROQ_API_KEY=your_groq_key
    GEMINI_API_KEY=your_gemini_key
    PERPLEXITY_API_KEY=your_perplexity_key
    
    # Database Config
    DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_chat_db
    ```

### 4. RAG Ingestion (Optional)
To use the `retrieve_knowledge_tool`, place PDF/TXT files in `knowledge_base/` and run:
```bash
python ingestion.py
```
This populates the local `chroma_db` vector store.

## Usage

### Run the CLI Chatbot
```bash
python main_langgraph.py
```

### Commands
*   **"set model to gemini"**: Manually force the agent to use Gemini.
*   **"create a presentation on [topic]"**: Triggers the PPT tool.
*   **"correction: [text]"**: Updates the system's knowledge about a previous error.

## Testing

Run specific test phases to verify components:
*   `python test_phase4.py`: Verify Database Persistence.
*   `python test_phase5.py`: Verify RAG/Vector Search.
