#vector db handle file upload,retrieve, delete, and add documents
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
import os
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter

class Embedder:
    """Handles document embedding and retrieval using Chroma vector store."""
    def __init__(self, persist_directory="chroma_agents", model_name="BAAI/bge-m3"):
        self.persist_directory = persist_directory
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3",
             model_kwargs={"device": "cpu", "trust_remote_code": True },
    encode_kwargs={"normalize_embeddings": True} # 
        )
        self.vectorstore = None
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " "]
        )
        self._load_or_create_vectorstore()

    def _load_or_create_vectorstore(self):
        """Load existing vectorstore or create a new one."""
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                embedding_function=self.embedding_model,
                persist_directory=self.persist_directory
            )
        else:
            # No persisted data yet, create empty vectorstore
            self.vectorstore = Chroma(
                embedding_function=self.embedding_model,
                persist_directory=self.persist_directory
            )


    def add_documents(self, documents):
        """Add documents to the vectorstore, splitting if necessary."""
        if all(isinstance(d, Document) for d in documents):
            splits = []
            for doc in documents:
                splits.extend(self.splitter.split_text(doc.page_content))
            # Create new Document objects from splits
            split_docs = [Document(page_content=s) for s in splits]
            id = self.vectorstore.add_documents(split_docs)
        else:
            # assume list of strings
            splits = self.splitter.create_documents([documents.page_content if isinstance(doc, Document) else doc for doc in documents])
            id = self.vectorstore.add_documents(splits)
        return id


    def retrieve(self, query, k=5):
        """Retrieve top-k similar documents for the query."""
        results =self.vectorstore.similarity_search(query, k=k)
        print("Vector count:", self.vectorstore._collection.count())
        return results
    
  
    
    
    
