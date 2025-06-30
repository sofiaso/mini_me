import os

from notion_client.notion_client import NotionClient
from rag.index_builder import IndexBuilder
from rag.query_engine import QueryEngine

from dotenv import load_dotenv

class RAGAssistant:
    def __init__(self):
        load_dotenv()
        self._notion_client = NotionClient()
        self._indexer = IndexBuilder()
        self._query_engine = QueryEngine()
        self.pages = os.getenv("PAGE_IDS")
    
    @property
    def pages(self):
        return os.getenv("PAGE_IDS")
    
    def update_pages(self):
        self._notion_client.export_pages(self.pages)
        docs = self._indexer.load_markdown_files()
        documents = self._indexer.document_to_chunk(docs)
        self._indexer.build_index(documents)
    
    def query(self, query_text, prompt=""):
        return self._query_engine.query(query_text, prompt)
    

    
