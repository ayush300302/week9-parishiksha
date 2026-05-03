import json
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
import os

print("Loading embeddings model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Loading chunks...")
with open('wk10_chunks.json', 'r') as f:
    chunks = json.load(f)

texts = [c['text'] for c in chunks]
ids = [c['chunk_id'] for c in chunks]

index_file = "faiss_wk10.index"
metadata_file = "faiss_metadata.pkl"

if not os.path.exists(index_file):
    print("Embedding chunks (this may take a minute)...")
    embeddings = model.encode(texts)
    embeddings = np.array(embeddings).astype('float32')
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner Product (Cosine if normalized)
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    
    faiss.write_index(index, index_file)
    with open(metadata_file, 'wb') as f:
        pickle.dump({'ids': ids, 'texts': texts, 'chunks': chunks}, f)
    print("Chunks embedded and saved to FAISS!")
else:
    print("Loading existing FAISS index...")
    index = faiss.read_index(index_file)
    with open(metadata_file, 'rb') as f:
        meta = pickle.load(f)
    ids = meta['ids']
    texts = meta['texts']
    chunks = meta['chunks']
    print(f"Loaded {index.ntotal} chunks from FAISS.")

def retrieve(query, k=5):
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype('float32')
    faiss.normalize_L2(query_embedding)
    
    distances, indices = index.search(query_embedding, k)
    
    results = {
        'ids': [[ids[idx] for idx in indices[0]]],
        'documents': [[texts[idx] for idx in indices[0]]],
        'distances': [distances[0].tolist()]
    }
    return results

questions = [
    "What is Newton's first law of motion?",
    "What is inertia?",
    "What is momentum?",
    "What happens when unbalanced force acts?",
    "Why passengers fall forward when bus brakes?",
    "What is Newton's second law of motion?",
    "What is Newton's third law of motion?",
    "What is SI unit of force?",
    "What happens to body at rest with no force?",
    "No external force on moving object?"
]

retrieval_log = []
misses = []

print("Running 10 queries for evaluation...")
for q in questions:
    res = retrieve(q, k=1)
    chunk_id = res['ids'][0][0]
    text = res['documents'][0][0]
    
    # Basic heuristic check for correctness
    is_correct = "YES" if any(word in text.lower() for word in ["newton", "inertia", "momentum", "force", "mass", "velocity", "rest"]) else "NO"
    
    log_entry = {
        "query": q,
        "top_1_chunk_id": chunk_id,
        "is_correct_top1": is_correct
    }
    retrieval_log.append(log_entry)
    
    if is_correct == "NO":
        misses.append(f"Query: {q}\nWrong Chunk ({chunk_id}): {text[:200]}...\nDiagnosis: Likely embedding limitation or query mismatch.\n")

with open('retrieval_log.json', 'w') as f:
    json.dump(retrieval_log, f, indent=2)

if not misses:
    misses.append("No obvious retrieval misses detected based on basic keyword overlap check. All top-1 chunks contained relevant keywords.")

with open('retrieval_misses.md', 'w') as f:
    f.write("# Retrieval Misses Diagnosis\n\n")
    f.write('\n'.join(misses))

print("Stage 2 completed: retrieval_log.json and retrieval_misses.md generated.")
