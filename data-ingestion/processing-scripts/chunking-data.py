import os
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

CLEAN_DIR = "../../data/processed/"
PROCESSED_DIR = "../../data/chunks"
os.makedirs(PROCESSED_DIR, exist_ok=True)

"""
Ref : https://docs.langchain.com/oss/python/integrations/splitters#text-structure-based
"""

yt_splitter = RecursiveCharacterTextSplitter(
    chunk_size=2000, 
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)

def process_data():
    all_chunks = []
    
    print(f"Walking through directory: {CLEAN_DIR}")
    
    for root, dirs, files in os.walk(CLEAN_DIR):

        current_folder = os.path.basename(root)
        if current_folder not in ["youtube", "linkedin"]:
            continue
            
        source = current_folder
        print(f"\n Processing {len(files)} files from {source}...")

        for filename in tqdm(files, desc=f"Chunking {source}"):
            if not filename.endswith('.json'):
                continue
                
            file_path = os.path.join(root, filename)
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            text = data.get("text", "")
            if not text:
                continue

            if source == "linkedin":
                # STRATEGY 1: Keep LinkedIn posts as single chunks
                chunk_data = {
                    "chunk_id": f"li_{data.get('post_id', filename)}",
                    "source": "linkedin",
                    "content": text,
                    "metadata": {
                        "url": data.get("url"),
                        "author": data.get("author", "Lenny Rachitsky")
                    }
                }
                all_chunks.append(chunk_data)
                
            elif source == "youtube":
                # STRATEGY 2: Recursively split YouTube transcripts
                chunks = yt_splitter.split_text(text)
                for i, chunk_text in enumerate(chunks):
                    chunk_data = {
                        "chunk_id": f"yt_{data.get('video_id', filename)}_{i}",
                        "source": "youtube",
                        "content": chunk_text,
                        "metadata": {
                            "url": data.get("url"),
                            "author": data.get("author", "Lenny Rachitsky"),
                            "chunk_index": i
                        }
                    }
                    all_chunks.append(chunk_data)

    # Final Save
    output_path = os.path.join(PROCESSED_DIR, "final_chunks.json")
    with open(output_path, "w") as f:
        json.dump(all_chunks, f, indent=2)
        
    print(f"\n Created {len(all_chunks)} total chunks.")
    print(f" Saved to: {output_path}")

if __name__ == "__main__":
    process_data()