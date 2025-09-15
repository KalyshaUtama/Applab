#vector db handle file upload,retrieve, delete, and add documents
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
import os
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter
#intfloat/multilingual-e5-small 
class Embedder:
    def __init__(self, persist_directory="chroma_agents", model_name="BAAI/bge-m3"):
        self.persist_directory = persist_directory


        # from sentence_transformers import SentenceTransformer
        # import torch
        # device = "cuda" if torch.cuda.is_available() else "cpu"

        self.embedding_model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3",
             model_kwargs={"device": "cpu", "trust_remote_code": True },
    encode_kwargs={"normalize_embeddings": True} # 
        )
        # self.embedding_model  = SentenceTransformer("BAAI/bge-m3")
        self.vectorstore = None
        #self.splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=100,
            separators=["\n\n", "\n", ".", " "]
        )
        self._load_or_create_vectorstore()

    def _load_or_create_vectorstore(self):
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
        # # documents: list of Document or list of str
        # split_docs = []
        # print(f"Adding  documents to vectorstore {documents}")
        #     # Perform semantic chunking on doc content
        # for doc in documents:
        #     print(f"Processing document: {doc}")
        #     # chunks = self.splitter.split_text(doc.page_content)

        #     # Propagate original metadata (like file_name) to each chunk
        # for chunk in chunks:
        #         # print(f"chunk {chunk}")
        #     split_docs.append(Document(page_content=chunk, metadata=documents.metadata))
        # # print(f"Adding documents to vectorstore {split_docs}")
        # ids = self.vectorstore.add_documents(split_docs)
        # return ids
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

    def delete_document(self, doc_id):
        """
        Delete documents by their IDs.
        """
        try:
            self.vectorstore.delete(ids=[doc_id])  # Underscore to access raw Chroma collection
            return True, f"Deleted document with ID '{doc_id}"
        except Exception as e:
            return False, f"Errore: {e}"
        


    def retrieve(self, query, k=5):
        results =self.vectorstore.similarity_search(query, k=k)
        # print(f"time to retrieve: {time.time() - start:.2f}s")
        print("Vector count:", self.vectorstore._collection.count())
        return results
    
    def retrieve_all(self):
        results =self.vectorstore.get()
        return results
    
    def retrieve_id(self, id):
        results =self.vectorstore.get(ids=[id])
        return results
    
