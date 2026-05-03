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

permissive_prompt = PromptTemplate.from_template(
    "Answer the question using the context provided.\n\nContext:\n{context}\n\nQuestion: {question}"
)

strict_prompt = PromptTemplate.from_template(
    "You are a helpful study assistant. Use the provided context to answer the question.\n"
    "If the answer is not present in the context, reply exactly: 'I don't have that in my study materials.'\n"
    "After every factual claim, cite the chunk it came from in square brackets, e.g., [Source: chunk_id].\n\n"
    "Context:\n{context}\n\nQuestion: {question}"
)

def ask(question, prompt_template):
    # 1. Retrieve
    retrieved = retrieve(question, k=5)
    
    # 2. Format context
    context_parts = []
    for chunk_id, text in zip(retrieved['ids'], retrieved['documents']):
        context_parts.append(f"--- Chunk ID: {chunk_id} ---\n{text}")
    context_str = "\n\n".join(context_parts)
    
    # 3. Generate
    chain = prompt_template | llm
    response = chain.invoke({"context": context_str, "question": question})
    
    return {
        "answer": response.content,
        "sources": retrieved['documents'],
        "chunk_ids": retrieved['ids']
    }

queries_to_test = [
    "What is Newton's first law of motion?",  # Direct
    "Why do passengers fall forward when a bus stops?",  # Paraphrased
    "Calculate the gravity on the surface of the Moon." # Out of scope
]

diff_output = []

print("Running Permissive Prompt...")
diff_output.append("# Prompt Comparison\n\n## Permissive Prompt Results")
for q in queries_to_test:
    ans = ask(q, permissive_prompt)
    diff_output.append(f"\n**Query:** {q}\n**Answer:** {ans['answer']}\n")

print("Running Strict Prompt...")
diff_output.append("\n---\n## Strict Prompt Results")
for q in queries_to_test:
    ans = ask(q, strict_prompt)
    diff_output.append(f"\n**Query:** {q}\n**Answer:** {ans['answer']}\n")

with open('prompt_diff.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(diff_output))

print("Stage 3 completed: prompt_diff.md generated.")
