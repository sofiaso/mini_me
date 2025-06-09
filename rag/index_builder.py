import re 
from pathlib import Path
from langchain.embeddings import HuggingFaceBgeEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from langchain.document_loaders import TextLoader

from rag.utils import CasheIndexed
from rag.const import MODEL, DATA_PATH

class IndexBuilder():
    def __init__(self):
        self.hash_cashe = CasheIndexed()

    def _clean_markdown(self, text: str):
        text = re.sub(r"!\[.*?\]\(.*?\)", "", text)
        text = re.sub(r"\[.*?\]\(.*?\)", "", text)
        text = re.sub(r"#+\s*", "", text)
        return text.strip()

    def load_markdown_files(self) -> list[Document]:
        docs = []
        for path in Path(DATA_PATH).glob("#.md"):
            loader = TextLoader(str(path), encoding="utf-8")
            raw_docs = loader.load()
            for doc in raw_docs:
                text = self._clean_markdown(doc.page_content)
                content_hash = self.hash_cashe.compute_hash(text)
                if self.hash_cashe.is_new(content_hash):
                    self.hash_cashe.add(content_hash)
                    docs.append(Document(page_content=text, metadata=doc.metadata))
        return docs

    def document_to_chunk(self, docs: list[Document], chunk_size=500, chunk_overlap=50):
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        return splitter.split_documents(docs)

    def build_index(self, docs: list[Document]):
        embeddings = HuggingFaceBgeEmbeddings(model_name=MODEL)
        vector_store = FAISS.from_documents(docs, embeddings)
        vector_store.save_local(DATA_PATH)

