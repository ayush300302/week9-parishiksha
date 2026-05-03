import json
from rank_bm25 import BM25Okapi

with open('wk10_chunks.json', 'r') as f:
    chunks = json.load(f)

corpus = [c['text'] for c in chunks]
tokenized_corpus = [doc.lower().split() for doc in corpus]
bm25 = BM25Okapi(tokenized_corpus)

questions = [
    "What is Newton's first law of motion?",
    "What is inertia?",
    "What is momentum?",
    "What happens when unbalanced force acts?",
    "Why passengers fall forward when bus brakes?"
]

results = []
for q in questions:
    tokenized_query = q.lower().split()
    scores = bm25.get_scores(tokenized_query)
    top_n = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
    results.append(f'Query: {q}')
    for i, idx in enumerate(top_n):
        chunk_id = chunks[idx]['chunk_id']
        text = chunks[idx]['text'][:100].replace('\n', ' ')
        results.append(f'  {i+1}. {chunk_id} (Score: {scores[idx]:.2f})')
        results.append(f'     {text}...')
    results.append('')

with open('chunking_diff.md', 'a', encoding='utf-8') as f:
    f.write('\n\n### Week 10 BM25 Retrieval for 5 Questions\n')
    f.write('\n'.join(results))
