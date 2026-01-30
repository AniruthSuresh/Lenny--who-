import os
import torch
import time
import json
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv  # Add this
from google import genai

load_dotenv()  


# --- CONFIG ---
DATA_PATH = "../data/embedded/mxbai_corpus.pt"
EMBED_MODEL = "mixedbread-ai/mxbai-embed-large-v1"
TOP_K = 6
GEMINI_MODEL = "gemini-2.5-flash-lite"

MAX_RPM = 10 
MAX_RPD = 20

print("Loading embeddings and chunks...")
data = torch.load(DATA_PATH)
corpus_embs = data["embeddings"]
chunks = data["chunks"]

print("Loading embedding model for queries...")
embed_model = SentenceTransformer(EMBED_MODEL, device="cuda" if torch.cuda.is_available() else "cpu")

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

class LennyAgent:
    def __init__(self):
        self.requests_today = 0
        self.last_request_time = 0

    def retrieve_topk(self, question, k=TOP_K):
        q_emb = embed_model.encode(question, convert_to_tensor=True)
        q_emb = q_emb / q_emb.norm()
        corpus_norm = corpus_embs / corpus_embs.norm(dim=1, keepdim=True)
        sims = torch.matmul(corpus_norm, q_emb)
        topk_idx = torch.topk(sims, k).indices.tolist()
        return [chunks[i] for i in topk_idx]

    def ask_lenny(self, question):

        if self.requests_today >= MAX_RPD:
            return "Daily limit reached (20 requests/day). Come back tomorrow!"
        
        now = time.time()
        wait_time = max(0, (60 / MAX_RPM) - (now - self.last_request_time))
        if wait_time > 0:
            time.sleep(wait_time)

        top_chunks = self.retrieve_topk(question)
        context_text = "\n\n".join([c["content"] if "content" in c else c.get("text","") for c in top_chunks])

        system_instruction = (
            "You are Lenny Rachitsky. Answer in his signature tone: thoughtful, analytical, "
            "practical, and founder-focused. Use bullet points and frameworks where appropriate. "
            "Use ONLY the provided context. If the answer is not in the context, say you are unsure."
        )

        prompt = f"Context:\n---\n{context_text}\n---\n\nQuestion: {question}"

        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            
            self.requests_today += 1
            self.last_request_time = time.time()
            return response.text

        except Exception as e:
            return f" Error: {str(e)}"

# --- CLI LOOP ---
if __name__ == "__main__":
    agent = LennyAgent()
    print(f"✨ Virtual Lenny (Gemini 2.5 Flash-Lite) Ready!")
    print(f"Limits: {MAX_RPM} RPM | {MAX_RPD} RPD\n")
    
    while True:
        q = input("You: ")
        if q.lower() in ["exit", "quit"]:
            break
        
        print("Lenny thinking...", end="\r")
        ans = agent.ask_lenny(q)
        print(f"Lenny: {ans}")
        print("-" * 50)