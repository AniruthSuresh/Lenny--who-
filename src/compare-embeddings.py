import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

with open("../data/chunks/final_chunks.json", "r") as f:
    all_chunks = json.load(f)
with open("../data/chunks/linkedin-synthetic-questions.json", "r") as f:
    gold_set = json.load(f)


model_configs = [
    {"name": "SFR-Embedding-Mistral", "path": "Salesforce/SFR-Embedding-Mistral"},
    # {"name": "text-embedding-3-large", "path": "mixedbread-ai/mxbai-embed-large-v1"} # Using mxbai as a high-perf local proxy
]

def evaluate_retrieval(model_name, model_path, chunks, gold_queries, k=5):
    print(f"\n Benchmarking {model_name}...")
    model = SentenceTransformer(model_path, trust_remote_code=True)
    
    # Pre-calculate embeddings for the entire corpus
    corpus_texts = [c['content'] for c in chunks]
    corpus_embeddings = model.encode(corpus_texts, convert_to_tensor=True, show_progress_bar=True)
    
    hits = 0
    mrr_sum = 0
    
    for item in tqdm(gold_queries, desc="Evaluating Queries"):
        query = item['question']
        correct_id = item['correct_id']
        
        query_emb = model.encode(query, convert_to_tensor=True)
        
        # Semantic search
        search_results = util.semantic_search(query_emb, corpus_embeddings, top_k=k)[0]
        
        # Check if the correct_id is in the top-k results
        retrieved_ids = [chunks[res['corpus_id']]['chunk_id'] for res in search_results]
        
        if correct_id in retrieved_ids:
            hits += 1
            # Reciprocal Rank = 1 / position (1-indexed)
            rank = retrieved_ids.index(correct_id) + 1
            mrr_sum += 1.0 / rank
            
    return {
        "Hit Rate@5": round(hits / len(gold_queries), 4),
        "MRR": round(mrr_sum / len(gold_queries), 4)
    }

final_results = {}
for config in model_configs:
    final_results[config['name']] = evaluate_retrieval(
        config['name'], config['path'], all_chunks, gold_set
    )

print("\n" + "="*30)
print("📊 EVALUATION RESULTS")
print("="*30)
print(json.dumps(final_results, indent=4))