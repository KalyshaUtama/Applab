from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableSequence
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field
import langdetect
import time

# ----------------- memory store -----------------
class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    messages: list[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []

store = {}
def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]

# ----------------- LLM class -----------------
class LLM:
    def __init__(self, api_key, base_url, model="Fanar-S-1-7B", temperature=0):
        self.llm = ChatOpenAI(
            model=model,
            openai_api_base=base_url,
            openai_api_key=api_key,
            temperature=temperature
        )

        # Prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant
             Answer in a conversational friendly manner
- Answer strictly based on context  and previous conversation. Refrain from fabrication and don't mention if unfit for query.
- Give entire response in the same language as the user's query. Refrain from switching languages.
-MUST Format cleanly every sentence is a new line
-Exclude any ** or *
"""),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])

        # Runnable chain with history
        self.chain = RunnableWithMessageHistory(
            self.prompt | self.llm,
            get_by_session_id,
            input_messages_key="question",
            history_messages_key="history"
        )

    def generate_answer(self, docs, question, session_id="default"):
        """Generate answer from docs + question using memory."""
        start = time.time()

        # Build context from docs
        context = "\n\n".join([doc.page_content for doc in docs]) if docs else ""
        full_question = f"{question}\n\nContext:\n{context}"
        print(f"[LLM] Context length: {full_question}")
        # Multilingual handling
        if langdetect.detect(question) == "ar":
            full_question = "أجب باللغة العربية فقط: " + full_question

        # Invoke runnable chain
        result = self.chain.invoke(
            {"question": full_question},
            config={"configurable": {"session_id": session_id}}
        ).content

        print(f"[LLM] Time: {time.time() - start:.2f}s")
        return result
