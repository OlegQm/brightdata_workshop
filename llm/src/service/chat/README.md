# LLM Chat Service

Agent orchestration for HotelFinder chat.

Files:

- `chat_service.py` - session state, LangGraph ReAct agent execution, SSE event shaping and hidden hotel JSON extraction.
- `prompts.py` - system prompt and tool-use rules.

The hidden `<<<HOTELS_JSON>>>` block lets the frontend update map results while
keeping the visible answer human-readable.
