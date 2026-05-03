import csv
import json
import os
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Load env variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

print("Loading embeddings model and FAISS index...")
model = SentenceTransformer('all-MiniLM-L6-v2')

index_file = "faiss_wk10.index"
metadata_file = "faiss_metadata.pkl"

index = faiss.read_index(index_file)
with open(metadata_file, 'rb') as f:
    meta = pickle.load(f)
ids = meta['ids']
texts = meta['texts']

def retrieve(query, k=5):
    query_embedding = model.encode([query])
    query_embedding = np.array(query_embedding).astype('float32')
    faiss.normalize_L2(query_embedding)
    
    distances, indices = index.search(query_embedding, k)
    
    results = {
        'ids': [ids[idx] for idx in indices[0]],
        'documents': [texts[idx] for idx in indices[0]]
    }
    return results

print("Initializing Groq LLM...")
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, groq_api_key=groq_api_key)

strict_prompt = PromptTemplate.from_template(
    "You are a helpful study assistant. Use the provided context to answer the question.\n"
    "If the answer is not present in the context, reply exactly: 'I don't have that in my study materials.'\n"
    "After every factual claim, cite the chunk it came from in square brackets, e.g., [Source: chunk_id].\n\n"
    "Context:\n{context}\n\nQuestion: {question}"
)

def ask(question, prompt_template):
    retrieved = retrieve(question, k=5)
    
    context_parts = []
    for chunk_id, text in zip(retrieved['ids'], retrieved['documents']):
        context_parts.append(f"--- Chunk ID: {chunk_id} ---\n{text}")
    context_str = "\n\n".join(context_parts)
    
    chain = prompt_template | llm
    response = chain.invoke({"context": context_str, "question": question})
    
    return {
        "answer": response.content,
        "chunk_ids": retrieved['ids']
    }

questions = [
    "What is Newton's first law of motion?",
    "What is inertia?",
    "What is Newton's second law of motion?",
    "What is momentum?",
    "What is Newton's third law of motion?",
    "What happens when unbalanced force acts?",
    "What is SI unit of force?",
    "Relationship between force mass acceleration?",
    "What is law of conservation of momentum?",
    "What happens to body at rest with no force?",
    "No external force on moving object?",
    "How does mass affect motion?",
    "Why passengers fall forward when bus brakes?",
    "Who is Prime Minister of India?",
    "What is photosynthesis?",
    "What is capital of France?",
    "Explain quantum entanglement?"
]

print("Running evaluation on 17 questions...")

results = []
for i, q in enumerate(questions):
    print(f"[{i+1}/17] Query: {q}")
    res = ask(q, strict_prompt)
    results.append({
        "question": q,
        "answer": res["answer"],
        "retrieved_chunks": ", ".join(res["chunk_ids"])
    })

csv_file = "eval_raw.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["question", "answer", "retrieved_chunks"])
    writer.writeheader()
    writer.writerows(results)

print(f"Stage 4 Generation completed. Saved {len(results)} answers to {csv_file}")
