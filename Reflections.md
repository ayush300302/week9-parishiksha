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

### Third attempt (150 BERT tokens):
- chunk_size = 150 BERT tokens
- overlap = 30 tokens
- total chunks = 68

### Why I changed from 300 to 150:
300-word chunks failed on query
"What is Newton's first law of motion?"
Returned marble on inclined plane (score 4.63)
instead of actual definition.
150-word chunks returned correct chunk (score 5.83).
Reason: chapter uses "force", "motion", "law"
in every paragraph. Smaller chunks reduce noise.

### Why I switched to BERT tokenizer:
Word count chunking (text.split()) treated
"non-uniform" as 1 word but BERT sees it as
3 tokens. BERT chunking is more precise and
consistent with how the model processes text.
Score improved from 5.83 to 8.78 on Newton's
first law query after switching to BERT chunks.

### Final parameters settled on:
- chunk_size = 150 BERT tokens
- overlap = 30 tokens
- total chunks = 68
- content_type = auto-tagged

---

## Stage 2 — BM25 Retrieval

### Index built on: 68 BERT chunks

### Content type distribution:
- activity: 16 chunks
- worked_example: 16 chunks
- figure: 14 chunks
- concept: 12 chunks
- general: 10 chunks

### Test results:

**Query 1: "What is Newton's first law of motion?"**
- 300-word result: wrong chunk, score 4.63 ❌
- 150-word result: correct chunk, score 5.83 ✅
- 150 BERT tokens: correct chunk, score 8.78 ✅

**Query 2: "What is the formula for force?"**
- Result: action-reaction chunk ❌
- Why wrong: F=ma rendered as image in PDF
  not extractable as text by PyMuPDF
- BERT produced [UNK] tokens for math symbols

**Query 3: "What is inertia?"**
- Result: water-filled tumbler activity ⚠️
- Why: inertia definition mixed with activity
  sections, BM25 matched activity context

### Chunking experiment summary:

| Metric | 300 words | 150 words | 150 BERT |
|--------|-----------|-----------|----------|
| Total chunks | 27 | 55 | 68 |
| Newton's law | Wrong ❌ | Correct ✅ | Correct ✅ |
| Best score | 4.63 | 5.83 | 8.78 |
| Formula query | Wrong ❌ | Wrong ❌ | Wrong ❌ |

---

## Stage 3 — Generation

### API: Groq
### Model: llama-3.3-70b-versatile
### Temperature: 0 (for reproducibility)

### Grounding prompt v1:
```
You are a study assistant for NCERT Class 9 Science.
Answer the question ONLY using the context provided below.
If the answer is not present in the context, say exactly:
"I cannot find this in the provided chapter content."
Do not use any outside knowledge.
```

### Grounding prompt final:
```
You are a strict study assistant for NCERT Class 9 Science.
STRICT RULES:
1. You must ONLY use information from the CONTEXT below.
2. If the exact answer is not in the CONTEXT say:
   I cannot find this in the provided chapter content.
3. Do NOT use your own knowledge under any circumstances.
4. Do NOT add any information not present in CONTEXT.
5. Quote directly from context where possible.
```

### What changed between v1 and final:
v1 was permissive — Groq interpreted "ONLY" as
"prefer context." Added explicit numbered rules
and "under any circumstances" constraint.
Grounding improved from 3/13 to 4/13.
Key learning: "only answer from context" is weaker
than "refuse if not in context" as a constraint.

---

## Stage 4 — Evaluation

### Evaluation set: 17 questions
- Direct from textbook: 10
- Paraphrased: 3
- Out of scope: 4

---

## Part A — Implementation Artifacts

### A1. Chunking Parameters

Final parameters:
- chunk_size = 150 BERT tokens
- overlap = 30 tokens
- total chunks = 68

Experiment that pushed me to these values:
Started with 300-word word-count chunks (27 chunks).
Query "What is Newton's first law?" returned
marble on inclined plane (score 4.63).
Switched to 150 words — correct chunk (score 5.83).
Then switched to BERT tokenizer — score 8.78.
Each change was motivated by a specific retrieval
failure on a real test query.

### A2. Wrong Retrieved Chunk

Query: "What is inertia?"

Wrong chunk returned:
"place a water-filled tumbler on a tray.
hold the tray and turn around as fast as
you can. we observe that the water spills.
why? observe that a groove is provided in
a saucer for placing the tea cup."

Why retriever returned it:
Word "inertia" appears in activity sections
multiple times alongside the definition.
BM25 matched the activity chunk because it
contained "inertia" in experimental context
scoring higher than the pure definition chunk.
This is a vocabulary overlap problem — BM25
cannot distinguish definition context from
example context.

### A3. Grounding Prompt v1 and Final

v1:
"Answer ONLY using the context provided below.
If the answer is not present say I cannot find
this in the provided chapter content."

Final:
"STRICT RULES:
1. Only use information from CONTEXT below.
2. If answer not in CONTEXT say I cannot find.
3. Do NOT use your own knowledge under any
   circumstances.
4. Quote directly from context where possible."

What changed:
v1 was too permissive. Groq used its own training
knowledge for inertia and F=ma even though context
was provided. Adding "under any circumstances" and
numbered rules made the constraint explicit.
Tested on "What is inertia?" — v1 answered from
own knowledge, final version attempted to use
context first.

---

## Part B — Numbers from Evaluation

### B1. Evaluation Scores

Total questions: 17
In-scope: 13
Correct: 10/13 (77%)
Grounded: 4/13 (31%)
Appropriate refusals: 4/4 (100%)

Number that bothered me most: Grounded 4/13
Only 4 answers supported by retrieved chunks.
9 answers came from Groq training knowledge.
This is dangerous for PariShiksha — Groq might
answer from general knowledge that contradicts
NCERT textbook even when answer appears correct.
A parent cannot verify if answer came from
textbook or from model's general knowledge.

### B2. Chunking Experiment

Two chunk sizes compared:
- 300 words — 27 chunks
- 150 words — 55 chunks
- 150 BERT tokens — 68 chunks

Delta on correctness:
- 300 words: 9/13 correct
- 150 BERT tokens: 10/13 correct
- Improvement: +1 correct answer

Delta on refusal-appropriateness:
- Both chunk sizes: 4/4 refusals correct
- Chunk size did not affect refusal behavior
- Refusals depend on grounding prompt not chunk size

### B3. Model Family Comparison

Did not formally compare model families.
Attempted Gemini API but hit quota limit (429 error).
Switched to Groq llama-3.3-70b-versatile.
This is a gap in my submission — formal model
comparison would have strengthened the evaluation.

---

## Part C — Debugging Moments

### C1. Most Frustrating Bug

Extracted only page 1 of iesc108.pdf giving
2332 characters and only 2 chunks. BM25 returned
negative scores (-0.11, -0.19). Spent approximately
20 minutes debugging BM25 retrieval code thinking
the algorithm was broken. Eventually printed
total page count and realized doc[0] extracts
only page 1 not all pages.

Fix: changed to loop over all pages:
for page in doc:
    full_text += page.get_text()

If someone hits this next week: always print
total characters and chunk count immediately
after extraction before touching retrieval code.

### C2. What Still Bothers Me

F=ma is not retrievable. Query "what is the
formula for force?" returns action-reaction chunk.
F=ma was rendered as image in PDF — PyMuPDF
extracts it as [UNK] tokens in BERT chunking.
This is the most common student query and it
fails silently — system returns wrong chunk and
Groq answers from its own training knowledge.

Fix would require: manually adding formula chunks
or using a MathML-aware PDF parser that can
extract mathematical notation as text.

---

## Part D — Architecture and Reasoning

### D1. Why Not Just ChatGPT?

In my evaluation "What is momentum?" was refused
by my system because p=mv formula was not
extracted from PDF as text.

ChatGPT would have answered from general knowledge
— which might be technically correct but NOT from
NCERT textbook specifically.

PariShiksha needs answers grounded in NCERT
because parents trust the textbook wording.
If ChatGPT says "momentum is mass times velocity"
but NCERT says "p = mv where p is momentum, m is
mass and v is velocity" — a teacher checking the
answer would flag the difference.

My system refuses when it cannot find the answer
in context. That is more honest than a confident
answer from ChatGPT that cannot be verified
against the textbook.

### D2. Why Not GANs?

GANs work by having a generator and discriminator
compete. Generator creates content, discriminator
judges if it looks real. This optimizes for
convincing-sounding output not textbook-accurate
output.

For PariShiksha the requirement is opposite of
creative generation. Answers must be strictly
grounded in NCERT content. A GAN has no mechanism
to refuse out-of-scope questions or verify answers
against a specific source.

Deeper principle: match architecture to objective.
GANs optimize for indistinguishability from
training data. RAG systems optimize for
faithfulness to a specific retrieved source.
These are fundamentally different goals.
A parent finding a hallucinated answer would
kill the pilot. GANs make hallucination more
likely not less.

### D3. Honest Pilot Readiness

No. System is not ready for 100 students Monday.

Three specific things to fix first:

1. Grounding: only 4/13 answers grounded in
   retrieved chunks. 9 answers come from Groq
   training knowledge — cannot be verified
   against NCERT textbook.

2. Formula retrieval: F=ma not extractable from
   PDF. Most common student query fails silently
   returning wrong chunk and unverified answer.

3. Evaluation set too small: 17 questions not
   enough to trust system on 100 students with
   diverse real queries including Hindi-English
   code-switching common in Tier-2/3 cities.

---

## Part E — Effort and Self Assessment

### E1. Effort Rating: 7/10

Rated 7 because:
- Genuinely debugged real failures (page extraction,
  BERT chunking, grounding prompt iteration)
- Honestly reported grounding failures in evaluation
  instead of hiding them
- Implemented three chunking strategies and compared
  them with real scores

Genuinely proud of: switching from word-count to
BERT tokenizer-based chunking after seeing retrieval
scores improve, and writing honest evaluation that
shows system weaknesses not just strengths.

### E2. Gap Between Me and Stronger Student

A stronger student would have implemented proper
content-type aware retrieval from the start —
separate BM25 indexes for definitions, worked
examples, and exercises with different retrieval
strategies per query type.

I used a single BM25 index with a simple 1.5x
score boost for content type. This is a rough
approximation that does not fully separate
concept retrieval from activity retrieval.

Did not do this due to time constraints —
1 hour per day was not enough to implement
and test a multi-index retrieval strategy.

### E3. What Would Change With Two More Days

First thing: Fix formula extraction by manually
adding chunks for F=ma, p=mv, Ft=mv-mu with
rich descriptive text so BM25 can match them.
These are the most common student queries and
currently fail completely. This directly impacts
correctness and grounding scores.

Last thing: Add Hindi-English code-switching
test queries to evaluation set since PariShiksha
students in Tier-2/3 cities mix languages —
"Newton ka first law kya hai?" type queries.
Important for production readiness but less
urgent than fixing core retrieval failures first.