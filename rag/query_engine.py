from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceBgeEmbeddings
import torch

from rag.const import MODEL, MODEL_ID, INDEX_PATH

class QueryEngine():
    def __init__(self, similarity_threshold=0.6, k=5, max_context_tokens=1000):
        self.index_path = INDEX_PATH
        self.similarity_threshold = similarity_threshold
        self.k = k
        self.max_context_tokens = max_context_tokens

        self.embedding = HuggingFaceBgeEmbeddings(model_name=MODEL)
        self.db = FAISS.load_local(self.index_path, self.embedding)

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(MODEL_ID)
        self.generator = pipeline(
            "text-generation", 
            model=self.model, 
            tokenizer=self.tokenizer, 
            device=torch.device("cuda" if torch.cuda_is_available() else "cpu"))
    
    def build_context(self, query):
        results = self.db.similarity_search_with_score(query, k=self.k)
        context_parts = []

        for doc, score in results:
            if score < self.similarity_threshold:
                continue
            source = doc.metadata.get("source", "unknown source")
            context_parts.append(f"[{source}]\n{doc.page_context.strip()}")
        
        if not context_parts:
            return
        
        context = "\n\n".join(context_parts)
        return context[:self.max_context_tokens]
    
    def build_prompt(self, query, context):
        if not context:
            return(
                f"User asked question: \n{query}\n\n"
                "No context provided. You should response politely that you can not find answer without additional info"
            )
        
        return f"""
        You are an attentive assistant who answers user questions in English based on context from documents. 
        This information from the documents is a small copy of the user and his life. Answer as if you are
        reading information from the brain of that person, who is asking.

        Context:
        ---
        {context}
        ---

        Question:
        {query}

        Respond:
        """
        
    
    def query(self, query: str):
        context = self.build_context(query)
        prompt = self.build_prompt(query, context)
        output = self.generator(prompt, max_new_tokens=200, do_sample=True)[0]["generated_text"]

        return output.split("Respond: ")[-1].strip()

if __name__ == "main":
    engine = QueryEngine()
    user_input = ""
    while True:
        user_input = input("\n Question: ")
        if user_input in {"exit", "stop", "quite"}:
            break
        respond = engine.query(user_input)
        print(respond)