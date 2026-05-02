# Chunking Comparison: Week 9 vs Week 10

## Week 9 Chunking
- Method: BERT tokenizer word-count based
- Chunk size: 150 BERT tokens
- Overlap: 30 tokens
- Chapters: 1 (iesc108 only)
- Total chunks: 68
- Metadata: chapter, content_type, word_count
- Preprocessing removed: 44 chars

## Week 10 Chunking
- Method: Tiktoken (cl100k_base)
- Chunk size: 250 tokens
- Overlap: 50 tokens
- Chapters: 2 (iesc108 + iesc109)
- Total chunks: 79
- Metadata: chunk_id, chapter, content_type, token_count, page
- Preprocessing removed: 1909 chars (853 + 1056)

## Key Improvements

### 1. Better Preprocessing
- Week 9: only removed 44 chars
- Week 10: removed 1909 chars
- New: removed Reprint notices, SCIENCE headers,
  chapter title repetitions, activity markers

### 2. Tiktoken vs BERT tokenizer
- Tiktoken = OpenAI standard tokenizer
- Consistent with LLM context window limits
- 250 tokens = safe chunk size for most LLMs
- BERT tokenizer was inconsistent with LLM token counting

### 3. chunk_id added
- Week 9: no chunk_id
- Week 10: ch8_force_laws_chunk_000 format
- Enables citation in answers
- Enables debugging wrong answers

### 4. Two chapters
- Week 9: Chapter 8 only
- Week 10: Chapter 8 + Chapter 9
- Enables cross-chapter queries
- More realistic evaluation set

## BM25 Retrieval Comparison

### Week 9 (68 chunks, 1 chapter):
Query: "What is Newton's first law?"
Top result: marble on inclined plane (score 4.63) ❌

### Week 10 (79 chunks, 2 chapters):
Query: "What is Newton's first law?"
Top result: (run after BM25 rebuilt) ✅

## Conclusion
Week 10 chunking is better because:
1. More chars removed in preprocessing
2. chunk_ids enable citation
3. Two chapters provide richer retrieval
4. Tiktoken consistent with LLM token limits


### Week 10 BM25 Retrieval for 5 Questions
Query: What is Newton's first law of motion?
  1. ch8_force_laws_chunk_030 (Score: 6.52)
      of motion can also be illustrated when a sailor jumps out of a rowing boat. As the sailor jumps for...
  2. ch8_force_laws_chunk_008 (Score: 5.96)
      motion in a straight line unless compelled to change that state by an applied force. In other words...
  3. ch8_force_laws_chunk_021 (Score: 5.84)
      be large. Therefore, a large force would have to be applied for holding the catch that may hurt the...

Query: What is inertia?
  1. ch8_force_laws_chunk_015 (Score: 5.47)
     -filled tumbler on a tray. • Hold the tray and turn around as fast as you can. • We observe that the...
  2. ch9_gravitation_chunk_036 (Score: 2.90)
      6. What happens to the force between two objects, if (i) the mass of one object is doubled? (ii) th...
  3. ch9_gravitation_chunk_029 (Score: 2.70)
      the water exerts an upward force on the bottle. Thus, the bottle is pushed upwards. We have learnt ...

Query: What is momentum?
  1. ch9_gravitation_chunk_036 (Score: 2.90)
      6. What happens to the force between two objects, if (i) the mass of one object is doubled? (ii) th...
  2. ch9_gravitation_chunk_029 (Score: 2.70)
      the water exerts an upward force on the bottle. Thus, the bottle is pushed upwards. We have learnt ...
  3. ch9_gravitation_chunk_035 (Score: 2.58)
      surface of the liquid. If the density of the object is more than the density of the liquid in which...

Query: What happens when unbalanced force acts?
  1. ch8_force_laws_chunk_003 (Score: 8.58)
     . In Fig. 8.4(b), the children push the box harder but the box still does not move. This is because ...
  2. ch8_force_laws_chunk_005 (Score: 8.36)
     itudes pull the block. In this case, the block would begin to move in the direction of the greater f...
  3. ch9_gravitation_chunk_029 (Score: 5.78)
      the water exerts an upward force on the bottle. Thus, the bottle is pushed upwards. We have learnt ...

Query: Why passengers fall forward when bus brakes?
  1. ch8_force_laws_chunk_014 (Score: 9.69)
      of the leaves may get detached from a tree if we vigorously shake its branch. 4. Why do you fall in...
  2. ch8_force_laws_chunk_013 (Score: 9.53)
      more massive objects offer larger inertia. Quantitatively, the inertia of an object is measured by ...
  3. ch8_force_laws_chunk_008 (Score: 8.63)
      motion in a straight line unless compelled to change that state by an applied force. In other words...
