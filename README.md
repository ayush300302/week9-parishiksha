# Week 9 — Retrieval-Ready Study Assistant
## PariShiksha | NCERT Class 9 Science
### Chapter 8: Force and Laws of Motion

---

## What This Project Does

Builds a retrieval-ready study assistant for NCERT Class 9 Science that:

1. Extracts text from NCERT Chapter 8 PDF using PyMuPDF
2. Compares BERT WordPiece vs T5 SentencePiece tokenizers on 5 passages
3. Chunks text using BERT tokenizer (150 tokens, 30 overlap)
4. Tags chunks by content type (concept, worked_example, activity, figure)
5. Builds BM25 retrieval index on 68 chunks
6. Generates grounded answers using Groq API (llama-3.3-70b-versatile)
7. Evaluates on 17 questions across 3 axes

---

## Evaluation Results

| Metric | Score |
|--------|-------|
| Correct | 10/13 (77%) |
| Grounded | 4/13 (31%) |
| Appropriate Refusals | 4/4 (100%) |

---

## Project Structure

```
week9-parishiksha/
├── notebook.ipynb          # main notebook — runs end to end
├── evaluation_results.csv  # 17 question evaluation table
├── reflection.md           # honest reflection on implementation
└── README.md               # this file
```

---

## Setup Instructions

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

pip install pymupdf rank_bm25 transformers torch groq
```

### API Key Setup

Get free Groq API key from:
https://console.groq.com

In notebook Cell 27, replace:
```python
GROQ_API_KEY = "your-groq-api-key-here"
```

### Data Setup

Download Chapter 8 PDF from NCERT:
https://ncert.nic.in/textbook.php?iesc1=0-11

File name: iesc108.pdf

Place in project root folder.
Do NOT commit PDF to repo.

### Run

1. Open `notebook.ipynb` in VS Code
2. Select venv kernel (top right)
3. Run all cells top to bottom

---

## Pipeline Architecture

```
iesc108.pdf
    │
    ▼
PyMuPDF Extraction (33890 chars, 13 pages)
    │
    ▼
Text Preprocessing
(whitespace, page numbers, hyphens)
    │
    ▼
BERT Tokenizer Comparison
(BERT vs T5 on 5 passages)
    │
    ▼
BERT-based Chunking
(150 tokens, 30 overlap, 68 chunks)
    │
    ▼
Content Type Tagging
(concept, worked_example, activity, figure)
    │
    ▼
BM25 Index + Smart Retrieval
(1.5x boost for matching content type)
    │
    ▼
Groq API Generation
(llama-3.3-70b-versatile, temperature=0)
    │
    ▼
Grounded Answer
{answer, retrieved_chunks}
    │
    ▼
Evaluation (17 questions)
```

---

## Key Design Decisions

### Tokenizer: BERT WordPiece chosen over T5 SentencePiece
- BERT: 48 tokens vs T5: 51 tokens on concept passage
- BERT handles hyphenated terms better (non-uniform: 3 vs 5 tokens)
- BERT trained on Wikipedia — knows physics vocabulary

### Chunk Size: 150 BERT tokens
- 300 words: 27 chunks, score 4.63 on Newton's law query
- 150 words: 55 chunks, score 5.83
- 150 BERT tokens: 68 chunks, score 8.78 ✅

### Retrieval: BM25 with content type boosting
- Single BM25 index on all 68 chunks
- 1.5x score boost for concept chunks on definition queries
- Improved definition retrieval over plain BM25

### Generation: Groq llama-3.3-70b-versatile
- Gemini API had quota issues (429 error)
- Groq free tier works reliably
- Temperature = 0 for reproducible evaluation

---

## Known Limitations

1. F=ma not retrievable — rendered as image in PDF
2. Grounding only 4/13 — Groq uses own knowledge when wrong chunk retrieved
3. No Hindi-English code-switching support
4. Single chapter only — no cross-chapter queries

---

## NCERT Source

Chapter 8 — Force and Laws of Motion:
https://ncert.nic.in/textbook.php?iesc1=0-11

File: iesc108.pdf (do not commit to repo)

---

## Dependencies

```
pymupdf
rank_bm25
transformers
torch
groq
scikit-learn
```

---

## Git History

Minimum 3 commits required for submission gate:
1. Stage 1: PDF extracted, sample passages identified
2. Stage 1+2: preprocessing, tokenizer comparison, chunking, BM25
3. Stage 2: content-type tagging, smart BM25 retrieval
4. Stage 3: Groq API connected, grounding prompt, answer() function
5. Stage 4: evaluation complete 10/13 correct 4/4 refusals