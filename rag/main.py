from fastapi import FastAPI, Query
from rag.assistant import RAGAssistant
import os
import json
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
PAGE_IDS = json.loads(os.getenv("PAGE_IDS", "[]"))

assistant = RAGAssistant()

app = FastAPI(title="RAG Assistant API")

@app.get("/query")
def ask(text: str = Query(..., description="Your answer")):
    return {"query": text, "answer": assistant.query(text)}

@app.post("/update")
def update_data():
    assistant.update_pages()
    return {"status": "Updated"}

@app.get("/")
def root():
    return {
        "message": "RAG Assistant API працює",
        "endpoints": {
            "GET /query?text=...": "Ask",
            "POST /update": "Update data"
        }
    }