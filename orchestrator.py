
from embeddings import Embedder
from llm import LLM


class ChatbotOrchestrator:
    """Orchestrates embedding and LLM components."""
    def __init__(self, api_key, base_url):
        self.embedder = Embedder(persist_directory="chroma_agents")  
        self.llm = LLM(api_key, base_url)

    def add_documents(self, documents):
        return self.embedder.add_documents(documents)
    
    def retrieve_docs(self, query, k=5):
        docs = self.embedder.retrieve(query, k)
        return docs

    def generate_answer(self, docs, question):
        return self.llm.generate_answer(docs, question)

    async def chat(self, query):
        docs = self.retrieve_docs(query)
        answer = self.generate_answer(docs, query)
        print(f"Docs used: {docs}")
        return answer
