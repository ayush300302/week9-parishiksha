# Week 9 Reflection — Retrieval-Ready Study Assistant
## PariShiksha Project | NCERT Class 9 Science
## Chapter 8: Force and Laws of Motion (iesc108.pdf)

---

## Stage 1 — Corpus Extraction

### PDF Details:
- File: iesc108.pdf (Chapter 8 — Force and Laws of Motion)
- Source: ncert.nic.in
- Total pages: 13
- Total characters before cleaning: 33890
- Total characters after cleaning: 33846
- Characters removed: 44

### Messiness observed in raw PDF:
- Extra whitespace between words
- Page numbers as standalone numbers
- Hyphenated words broken across lines
- Chapter title repeated in fragments:
  "FORCE ORCE ORCE AND AND LAWS AWS OF MOTION OTION"
- "Reprint 2025-26" on every page
- Activity sections mixed with concept paragraphs
- Formulas like F=ma extracted as plain symbols
- Only 44 characters removed — PDF messier than
  preprocessing caught

### Preprocessing applied:
- Removed extra whitespace: re.sub(r'\s+', ' ', text)
- Removed page numbers: re.sub(r'\n\d+\n', ' ', text)
- Fixed hyphenated words: re.sub(r'-\n', '', text)

---

## Stage 1 — Tokenizer Comparison

### 5 Passages tested:
1. Concept paragraph — motion description
2. Worked example — Example 8.1 constant force
3. Formula — Ft = mv - mu
4. End of chapter question — stone on frozen lake
5. Figure caption — Fig 8.5 marble on inclined plane

### Token counts:

| Passage | BERT | T5 |
|---------|------|----|
| Passage 1 (concept para) | 48 | 51 |
| Passage 2 (worked example) | 73 | 80 |
| Passage 3 (formula) | 55 | 66 |
| Passage 4 (end of chapter Q) | 62 | 67 |

### Key word-level observations:

| Word | BERT | T5 |
|------|------|----|
| velocity | 1 token ✅ | 1 token ✅ |
| acceleration | 1 token ✅ | 1 token ✅ |
| uniform | 1 token ✅ | 1 token ✅ |
| non-uniform | 3 tokens ⚠️ | 5 tokens ❌ |
| thermodynamics | 4 pieces ❌ | 3 pieces ⚠️ |

### Decision: BERT WordPiece chosen because:
- Fewer tokens across all passages
- Better handling of hyphenated terms
- Common science words stay whole
- Trained on Wikipedia = knows physics vocabulary

---

## Stage 1 — Chunking

### First attempt (300 words):
- chunk_size = 300 words
- overlap = 50 words
- total chunks = 27

### Second attempt (150 words):
- chunk_size = 150 words
- overlap = 30 words
- total chunks = 55

### Why I changed:
300-word chunks failed on query
"What is Newton's first law of motion?"
→ returned marble on inclined plane (score 4.63)
instead of actual definition.

150-word chunks returned correct chunk (score 5.59):
"An object remains in a state of rest or of
uniform motion in a straight line..."

Reason: chapter uses "force", "motion", "law"
in every paragraph. Smaller chunks reduce noise.

### Final parameters:
- chunk_size = 150 words
- overlap = 30 words
- total chunks = 55
- content_type = general

---

## Stage 2 — BM25 Retrieval

### Index built on: 55 chunks

### Test results:

**Query 1: "What is Newton's first law of motion?"**
- 300-word result: wrong chunk, score 4.63 ❌
- 150-word result: correct chunk, score 5.83 ✅
  → "First law of motion: An object continues
     to be in a state of rest or uniform motion"

**Query 2: "What is the formula for force?"**
- Result: action-reaction chunk, score 6.61 ❌
- Why wrong: F=ma rendered as image in PDF
  not extractable as text by PyMuPDF

**Query 3: "What is inertia?"**
- Result: water-filled tumbler activity, score 5.05 ⚠️
- Why: inertia definition mixed with activity
  sections, BM25 matched activity context

### Chunking experiment summary:

| Metric | 300 words | 150 words |
|--------|-----------|-----------|
| Total chunks | 27 | 55 |
| Newton's law query | Wrong ❌ | Correct ✅ |
| Best score | 4.63 | 5.83 |
| Formula query | Wrong ❌ | Wrong ❌ |

### What still bothers me:
F=ma not retrievable because it was rendered
as image in PDF. Students asking "what is the
formula for force" would get wrong answers.
Fix: manually add formula chunks or use better
PDF parser that handles mathematical notation.
