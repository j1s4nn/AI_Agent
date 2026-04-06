"""
utils/agent.py
Builds the LangChain ReAct agent with:
  - OpenAI LLM (configurable model)
  - ConversationBufferMemory for multi-turn chat
  - WebSearch + DocumentRetriever tools
"""

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain import hub
from langchain.prompts import PromptTemplate

from utils.config import OPENAI_API_KEY, MODEL_NAME
from utils.tools import ALL_TOOLS


# ── System persona injected into agent prompt ─────────────────────────────────
SYSTEM_PERSONA = """You are a highly capable AI Research Assistant built by Jisan.

You have access to two tools:
1. DocumentRetriever – searches the user's uploaded knowledge base
2. WebSearch – searches the live internet via DuckDuckGo

Guidelines:
- Always check DocumentRetriever first if the question might relate to uploaded files.
- Cite your sources clearly, e.g. "[From uploaded doc]" or "[Web: <url>]".
- If you use multiple tools, synthesize a clear, structured final answer.
- Be concise but complete. Use bullet points for lists.
- If you do not know something, say so – never hallucinate.
- Maintain context from the conversation history.
"""


def build_agent() -> AgentExecutor:
    """
    Instantiate and return a LangChain ReAct AgentExecutor.
    Called once at server startup; the executor is kept in memory.
    """
    llm = ChatOpenAI(
        model=MODEL_NAME,
        temperature=0.2,
        openai_api_key=OPENAI_API_KEY,
        streaming=False,
    )

    # Pull standard ReAct prompt from LangChain Hub and inject persona
    base_prompt = hub.pull("hwchase17/react-chat")
    base_prompt.messages[0].prompt.template = (
        SYSTEM_PERSONA + "\n\n" + base_prompt.messages[0].prompt.template
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )

    agent = create_react_agent(llm=llm, tools=ALL_TOOLS, prompt=base_prompt)

    executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        memory=memory,
        verbose=True,           # prints reasoning steps to terminal (great for demos)
        max_iterations=8,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    )
    return executor


# Singleton – shared across FastAPI requests
_agent_executor: AgentExecutor | None = None


def get_agent() -> AgentExecutor:
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = build_agent()
    return _agent_executor


def reset_agent():
    """Clear memory and rebuild agent (used by /reset endpoint)."""
    global _agent_executor
    _agent_executor = None
    _agent_executor = build_agent()
