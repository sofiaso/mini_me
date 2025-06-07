import os 
import re 
from pathlib import Path
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain.document_loaders import TextLoader

DATA_PATH = "data"
INDEX_PATH = "faiss_index"
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

class Index_builder():
    def __init__(self, text):
        self.text = text
        self.docs = self._document_to_chunk(self._load_markdown_files(self._clean_markdown(self.text)))

    def _clean_markdown(self, text: str):
        text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
        text = re.sub(r"\[.*?\]\(.*?\)", "", text)
        text = re.sub(r"#+\s*", "", text)
        return text.strip()

    def _load_markdown_files(self, data: str) -> list[Document]:
        docs = []
        for path in Path(data).glob("#.md"):
            loader = TextLoader(str(path), encoding="utf-8")
            raw_docs = loader.load()
            for doc in raw_docs:
                text = self.clean_markdown(doc.page_content)
                cleaned_doc = Document(page_content=text, metadata=doc.metadata)
                docs.append(cleaned_doc)
        
        return docs

    def _document_to_chunk(self, docs: list[Document], chunk_size=500, chunk_overlap=50):
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_documents(docs)

    def build_index(self, docs: list[Document], path_to_save):
        embeddings = HuggingFaceBgeEmbeddings(model_name=MODEL)
        vector_store = FAISS.from_documents(docs, embeddings)
        vector_store.save_local(path_to_save)

