import asyncio
from embeddings import Embedder
from llm import LLM
from tts import TTS
from stt import STT

class ChatbotOrchestrator:
    def __init__(self, api_key, base_url):
        self.embedder = Embedder(persist_directory="chroma_agents")  # shared DB
        self.llm = LLM(api_key, base_url)
        self.tts = TTS()
        self.stt = STT()

    def add_documents(self, documents):
        return self.embedder.add_documents(documents)

    def ping(self):
        return True 
    
    def retrieve_docs(self, query, k=5):
        docs = self.embedder.retrieve(query, k)
        # print(f"NUm of docs {len(docs)}  Retrieved {docs}")
        return docs
    
    def retrieve_id(self,id):
        docs = self.embedder.retrieve_id(id)
        # print(f"NUm of docs {len(docs)}  Retrieved {docs}")
        return docs
    
    def retrieve_all_docs(self):
        docs = self.embedder.retrieve_all()
        # print(f"NUm of docs {len(docs)}  Retrieved {docs}")
        return docs
    
    def delete_docs(self, id):
        return self.embedder.delete_document(id)
    

    def generate_answer(self, docs, question):
        return self.llm.generate_answer(docs, question)

    async def speak(self, text):
        await self.tts.speak(text)

    async def speak_stream(self, text):
        return self.tts.speak_stream(text)

    def transcribe_audio(self, filename):
        return self.stt.transcribe(filename)

    async def chat(self, query):
        docs = self.retrieve_docs(query)
        answer = self.generate_answer(docs, query)

        print(f"Docs used: {docs}")
        # asyncio.create_task(self.speak(answer))  # Run TTS async (does not block)
        return answer
