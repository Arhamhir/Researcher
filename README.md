# Blackline Paper Review

Minimal, sleek, and honest AI peer review for academic papers using multi-agent orchestration.

### Live preview
Visit https://researcher-snowy.vercel.app to start reviewing papers.

## Workflow

1. **Upload** → User uploads a PDF research paper
2. **Parse** → Backend extracts sections (methodology, results, citations, etc.)
3. **Review** → 4 AI agents evaluate in parallel:
   - **Methodology**: Rigor, soundness, experimental design
   - **Novelty**: Contribution relative to existing literature
   - **Citation**: Accuracy and completeness of references
   - **Clarity**: Writing quality and logical flow
4. **Synthesize** → Final critic aggregates scores and verdict
5. **Report** → Dashboard displays 2x2 grid with all feedback

## Architecture

### Backend (FastAPI + LangGraph)
- **PDF Processing**: Extracts text and sections using regex + heading detection
- **Embeddings**: Local hashed bag-of-words vectors (lexical, not semantic - Groq has no embeddings API) for similarity retrieval
- **Vector Store**: Supabase with pgvector for similarity search
- **LLM**: Groq chat completions (`openai/gpt-oss-120b` by default), via the OpenAI-compatible SDK, with strict JSON Schema structured outputs and rate-limit/retry handling

### LangGraph Orchestration
```
START
  ├→ methodology_node (parallel)
  ├→ novelty_node (parallel)
  ├→ citation_node (parallel)
  └→ clarity_node (parallel)
         ↓ (barrier join - waits for all)
      final_decision_node
         ↓
        END
```
**Key**: Parallel nodes enable concurrent review. Critic waits for all agents before synthesizing.

### Frontend (React + Router)
- **UploadPage**: Drag-drop PDF + inline processing loader (no route change)
- **ReviewDashboard**: 2x2 grid layout showing methodology|clarity / citation|novelty feedback
- **Theme**: Black bg, yellow accent (#f4c431), minimal design

## What We Learned

### Technical
- **LangGraph State Management**: Fan-out/fan-in pattern for parallel agent orchestration
- **Groq Structured Outputs**: Strict JSON Schema mode on `gpt-oss` models, with automatic degrade to JSON Object Mode and retry/backoff on rate limits or transient errors
- **PDF Parsing**: Section detection via synonym-rich heading maps + regex fallback
- **Vector Storage**: Pgvector for lexical-similarity retrieval; self-similarity filtering for novelty assessment

### Design
- **Single-Page Processing**: Inline loader avoids route overhead (UX improvement)
- **Barrier Synchronization**: Critic waits for all reviewers (enforces consensus)
- **Graceful Degradation**: Fallback extraction for malformed papers

## Use Case

**Target**: Researchers, reviewers, authors wanting honest, instant peer feedback without human bias.

**Problem Solved**:
- Journal peer review is slow (months)
- Biased by reviewer relationships
- Lacks diverse perspectives

**Solution**: AI agents review 4 core dimensions instantly, with transparent scoring and no favoritism.

## Stack

| Component | Tech |
|-----------|------|
| Frontend | React 18, React Router v6, CSS Grid |
| Backend | Python, FastAPI, LangGraph |
| LLM | Groq (Chat) + local lexical embeddings |
| Database | Supabase (PostgreSQL + pgvector) |
| Deployment | Docker Compose |

## Running Locally

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```


# Researcher
