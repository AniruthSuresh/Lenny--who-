import os
import json
import random
from google import genai
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


with open("../data/chunks/final_chunks.json", "r") as f:
    all_chunks = json.load(f)

li_chunks = [c for c in all_chunks if c['source'] == 'linkedin']

sample_size = min(len(li_chunks), 5)
test_chunks = random.sample(li_chunks, sample_size)

gold_dataset = []
output_json_path = "../data/chunks/linkedin-synthetic-questions.json"

print(f"Generating {sample_size} questions from LinkedIn data...")

for chunk in tqdm(test_chunks):

    
    prompt = (
        "You are an expert at creating RAG evaluation datasets. "
        "Based on the context provided, write a short, natural-sounding question "
        "that this specific text answers perfectly. Do not mention 'the text' or 'the context'.\n\n"
        f"Context: {chunk['content']}"
    )

    try:
        # gemini-2.5-flash is the 2026 stable fast model
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=prompt
        )
        
        question = response.text.strip()
        
        # Storing Question + Correct ID + Original Context for easy manual review
        gold_dataset.append({
            "question": question,
            "correct_id": chunk['chunk_id'],
            "context": chunk['content'].strip() # Added context here
        })

    except Exception as e:
        print(f"\n Error on chunk {chunk.get('chunk_id')}: {e}")

with open(output_json_path, "w", encoding="utf-8") as f:
    json.dump(gold_dataset, f, indent=2, ensure_ascii=False)

print(f"\n Success! Saved {len(gold_dataset)} questions with context to {output_json_path}.")