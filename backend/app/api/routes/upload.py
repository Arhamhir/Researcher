import os
import uuid
import json
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_loader import load_pdf_text
from app.services.text_cleaner import clean_text
from app.services.section_parser import parse_sections
from app.services.embeddings import get_embedding
from app.services.vector_store import store_paper, store_section, store_review
from app.graph.graph import build_graph
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=2)


def _resolve_upload_dir() -> Path:
    configured_dir = os.getenv("UPLOAD_DIR")
    if configured_dir:
        upload_dir = Path(configured_dir)
    elif os.getenv("VERCEL"):
        upload_dir = Path(tempfile.gettempdir()) / "researcher_uploads"
    else:
        upload_dir = Path(__file__).resolve().parents[3] / "uploads"

    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir

def run_graph_sync(paper_id: str, paper_text: str, sections: dict):
    """Run the graph synchronously in a thread pool."""
    print(f"[GRAPH_WORKER] Starting review for paper_id: {paper_id}")
    try:
        compiled_graph = build_graph()
        
        initial_state = {
            "paper_id": paper_id,
            "paper_text": paper_text,
            "paper_sections": sections,
            "methodology_review": None,
            "novelty_review": None,
            "citation_review": None,
            "clarity_review": None,
            "final_decision": None,
            "critic": {"status": "review", "retry_count": 0}
        }
        
        # Execute the graph
        print("[GRAPH_WORKER] Invoking graph...")
        result = compiled_graph.invoke(initial_state)
        print(f"[GRAPH_WORKER] Graph completed. Result keys: {result.keys()}")
        
        # Store the review results
        print("[GRAPH_WORKER] Storing review results...")
        store_review(paper_id, result)
        print("[GRAPH_WORKER] Review stored successfully")
    except Exception as e:
        print(f"[GRAPH_WORKER] Error running review graph: {e}")
        import traceback
        traceback.print_exc()

@router.post("/upload")
async def upload_paper(file: UploadFile = File(...)):
    try:
        job_id = str(uuid.uuid4())
        upload_dir = _resolve_upload_dir()
        file_path = upload_dir / f"{job_id}.pdf"

        with open(file_path, "wb") as f:
            f.write(await file.read())

        raw_text = load_pdf_text(str(file_path))
        cleaned = clean_text(raw_text)
        sections = parse_sections(cleaned)

        paper_id = store_paper(file.filename, str(file_path))

        for name, content in sections.items():
            embedding = get_embedding(content)
            store_section(paper_id, name, content, embedding)

        abstract = sections.get("abstract", "")
        introduction = sections.get("introduction", "")
        methodology = sections.get("methodology", "")
        full_text = cleaned
        paper_text = f"{abstract}\n\n{introduction}\n\n{methodology}\n\n{full_text}"

        loop = asyncio.get_event_loop()
        loop.run_in_executor(executor, run_graph_sync, paper_id, paper_text, sections)

        return {
            "job_id": job_id,
            "paper_id": paper_id,
            "sections_stored": list(sections.keys()),
            "status": "processing"
        }
    except Exception as e:
        print(f"[UPLOAD] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
