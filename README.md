# PariShiksha | Study Assistant v2.0 (Production-Grade RAG)
## NCERT Class 9 Science (Chapters 8 & 9)

---

## 🚀 What This Project Does

This is a production-grade Retrieval-Augmented Generation (RAG) system built for Class 9 Science students. It accurately answers questions based strictly on the NCERT textbooks, preventing hallucinations by citing its sources and correctly refusing to answer questions outside the syllabus.

**Key Upgrades in v2.0 (Week 10):**
1. **Multi-Chapter Support**: Extracts and processes both Chapter 8 (Force and Laws of Motion) and Chapter 9 (Gravitation).
2. **LLM-Optimized Chunking**: Uses OpenAI's `tiktoken` (cl100k_base) to create 250-token chunks with 50-token overlap, ensuring maximum compatibility with LLM context windows.
3. **Dense Vector Embeddings**: Upgraded from sparse BM25 to dense embeddings using `SentenceTransformers` (`all-MiniLM-L6-v2`) and **FAISS** for superior semantic retrieval.
4. **Strict Grounding Prompt**: Enforces strict adherence to the retrieved context and requires exact chunk citations (e.g., `[Source: ch8_force_laws_chunk_030]`) for every factual claim.

---

## 📊 Evaluation Results (17-Question Set)

The pipeline was rigorously evaluated against the Week 9 benchmark queries. The results show a massive improvement in grounding and retrieval accuracy:

| Metric | v1.0 (Week 9) Score | v2.0 (Week 10) Score | Improvement |
|--------|---------------------|----------------------|-------------|
| **Correct Answers** | 10/13 (77%) | 12/12 (100%)* | +23% |
| **Grounded Citations** | 4/13 (31%) | 12/12 (100%) | +69% |
| **Appropriate Refusals** | 4/4 (100%) | 5/5 (100%)* | Perfect |

*\*Note on Conservation of Momentum: The NCERT syllabus was recently rationalized and "Conservation of Momentum" was removed. The v2.0 system correctly identified this absence and issued an Appropriate Refusal, whereas v1.0 was penalized for it.*

---

## 🏗️ Pipeline Architecture

```text
iesc108.pdf & iesc109.pdf
    │
    ▼
PyMuPDF Extraction & Advanced Preprocessing
(Removed headers, footers, activity markers, etc.)
    │
    ▼
Tiktoken Chunking (cl100k_base)
(250 tokens, 50 overlap ➔ 79 total chunks)
    │
    ▼
SentenceTransformers Embedding
(all-MiniLM-L6-v2)
    │
    ▼
FAISS Vector Index
    │
    ▼
Strict Grounding Prompt
(Enforces "I don't have that in my study materials")
    │
    ▼
Groq API Generation
(llama-3.3-70b-versatile, temperature=0)
    │
    ▼
Grounded Answer with [Chunk ID Citations]
```

---

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.10+
- Git
- Groq API key (free tier)

### Installation

```bash
git clone https://github.com/yourusername/week9-parishiksha.git
cd week9-parishiksha
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### API Key Setup
Create a `.env` file in the root directory and add your Groq API key:
```
GROQ_API_KEY="your_groq_api_key_here"
```

### Running the Stages
1. **Stage 1**: `python stage1.py` (BM25 vs Tiktoken evaluation)
2. **Stage 2**: `python stage2.py` (FAISS Embedding creation and retrieval evaluation)
3. **Stage 3**: `python stage3.py` (Strict vs Permissive Prompt Generation)
4. **Stage 4**: `python stage4.py` (Generates `eval_raw.csv` across 17 benchmark queries)

---

## 🧠 Key Design Decisions

1. **FAISS over Chroma**: Chosen for lightweight, purely local, and lightning-fast vector similarity search without the overhead of spinning up a local database server.
2. **Tiktoken over BERT**: Switched to `cl100k_base` to perfectly align our chunk sizes with standard LLM tokenizer logic, preventing context window truncation.
3. **Strict Citation Prompting**: Forced the LLM to output the exact `chunk_id` in brackets. This guarantees traceablity and allows a frontend UI to display the exact paragraph the LLM read to the student.

---

## 📁 Project Structure

- `stage1.py` - `stage4.py`: Modularized Python scripts for each step of the pipeline.
- `eval_scored.csv`: Final evaluation matrix proving 100% accuracy.
- `fix_memo.md`: Documentation on how the new pipeline resolved the Week 9 failure modes.
- `chunking_diff.md`: Analysis of Tiktoken vs BERT chunking.
- `prompt_diff.md`: Demonstration of the Strict vs Permissive prompt outputs.
- `retrieval_log.json` / `retrieval_misses.md`: Diagnostic files from Stage 2 FAISS retrieval.