from supabase import create_client, Client
import uuid
import re
from app.core.config import SUPABASE_URL, SUPABASE_KEY

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def store_paper(title: str, file_path: str) -> str:
    paper_id = str(uuid.uuid4())
    supabase.table("papers").insert({   
        "id": paper_id,
        "title": title,
        "file_path": file_path
    }).execute()
    return paper_id

def store_section(paper_id: str, section_name: str, content: str, embedding: list[float]):
    section_id = str(uuid.uuid4())
    payload = {
        "id": section_id,
        "paper_id": paper_id,
        "section_name": section_name,
        "content": content,
        "embedding": embedding
    }

    try:
        supabase.table("paper_sections").insert(payload).execute()
    except Exception as e:
        message = str(e)
        match = re.search(r"expected\s+(\d+)\s+dimensions,\s+not\s+(\d+)", message)
        if not match:
            raise

        expected_dim = int(match.group(1))
        current_embedding = embedding or []
        current_dim = len(current_embedding)

        if current_dim < expected_dim:
            adjusted_embedding = current_embedding + [0.0] * (expected_dim - current_dim)
        else:
            adjusted_embedding = current_embedding[:expected_dim]

        payload["embedding"] = adjusted_embedding
        supabase.table("paper_sections").insert(payload).execute()

    return section_id

def get_paper_review(paper_id: str) -> dict:
    """
    Retrieve the review for a paper from the database.
    Reconstructs the full review from review_logs entries linked via reviews table.
    Falls back to reviews.verdict/notes if logs are incomplete.
    """
    try:
        print(f"[RETRIEVE] Getting review for paper_id: {paper_id}")

        # Get review record for this paper
        review_result = supabase.table("reviews").select("*").eq("paper_id", paper_id).execute()
        print(f"[RETRIEVE] Reviews query result: {review_result.data}")

        if not review_result.data:
            print(f"[RETRIEVE] No review found for paper {paper_id}")
            return None

        review_row = review_result.data[0]
        review_id = review_row.get("id")
        print(f"[RETRIEVE] Found review_id: {review_id}")

        # Get all review logs for this review
        logs_result = supabase.table("review_logs").select("*").eq("review_id", review_id).order("timestamp").execute()
        print(f"[RETRIEVE] Found {len(logs_result.data)} logs")

        # Reconstruct review from logs
        review = {
            "methodology_review": None,
            "novelty_review": None,
            "citation_review": None,
            "clarity_review": None,
            "final_decision": None,
            "critic": {"status": "processing", "retry_count": 0}
        }

        import json
        if logs_result.data:
            for log in logs_result.data:
                node_name = log.get("node_name", "")
                node_output = log.get("node_output")
                print(f"[RETRIEVE] Processing log: {node_name}")

                if isinstance(node_output, str):
                    try:
                        node_output = json.loads(node_output)
                    except:
                        pass

                # Map node names to review fields
                if "methodology" in node_name and node_output:
                    review["methodology_review"] = node_output
                    print(f"[RETRIEVE] Set methodology_review")
                elif "novelty" in node_name and node_output:
                    review["novelty_review"] = node_output
                    print(f"[RETRIEVE] Set novelty_review")
                elif "citation" in node_name and node_output:
                    review["citation_review"] = node_output
                    print(f"[RETRIEVE] Set citation_review")
                elif "clarity" in node_name and node_output:
                    review["clarity_review"] = node_output
                    print(f"[RETRIEVE] Set clarity_review")
                elif "final_decision" in node_name and node_output:
                    review["final_decision"] = node_output
                    print(f"[RETRIEVE] Set final_decision: {node_output}")
                elif "final_state" in node_name and node_output:
                    # Fallback: use full state payload if logged
                    review.update({
                        "methodology_review": node_output.get("methodology_review") or review.get("methodology_review"),
                        "novelty_review": node_output.get("novelty_review") or review.get("novelty_review"),
                        "citation_review": node_output.get("citation_review") or review.get("citation_review"),
                        "clarity_review": node_output.get("clarity_review") or review.get("clarity_review"),
                        "final_decision": node_output.get("final_decision") or review.get("final_decision"),
                        "critic": node_output.get("critic") or review.get("critic"),
                    })
                    print(f"[RETRIEVE] Applied final_state fallback")

        # If final decision still missing, synthesize from reviews table verdict/notes
        if not review.get("final_decision"):
            verdict = review_row.get("verdict")
            notes = review_row.get("notes")
            if verdict and str(verdict).lower() != "pending":
                review["final_decision"] = {
                    "decision": verdict,
                    "confidence": "Medium",
                    "average_score": None,
                    "scores": {},
                    "justification": notes or ""
                }
                print(f"[RETRIEVE] Synthesized final_decision from verdict/notes")

        print(f"[RETRIEVE] Final review: {review}")
        return review
    except Exception as e:
        print(f"Error retrieving paper review: {e}")
        import traceback
        traceback.print_exc()
        return None


def store_review(paper_id: str, review_data: dict) -> str:
    """
    Store review results in reviews and review_logs tables.
    First creates a review record, then stores each node's output as a log entry.
    """
    try:
        import json
        
        # System reviewer ID for AI reviews (fixed UUID for all AI reviews)
        system_reviewer_id = "00000000-0000-0000-0000-000000000001"

        print(f"[STORE] review_data: {review_data}")
        
        # First, create a review record linking paper to review
        review_id = str(uuid.uuid4())
        supabase.table("reviews").insert({
            "id": review_id,
            "paper_id": paper_id,
            "reviewer_id": system_reviewer_id,
            "verdict": review_data.get("final_decision", {}).get("decision", "Pending"),
            "notes": review_data.get("final_decision", {}).get("justification", "")
        }).execute()
        
        # Store each review component as a log entry linked to this review
        nodes_to_store = [
            ("methodology_node", review_data.get("methodology_review")),
            ("novelty_node", review_data.get("novelty_review")),
            ("citation_node", review_data.get("citation_review")),
            ("clarity_node", review_data.get("clarity_review")),
            ("final_decision_node", review_data.get("final_decision")),
            ("final_state", review_data),
        ]
        
        for node_name, node_output in nodes_to_store:
            if node_output is None:
                continue
                
            log_id = str(uuid.uuid4())
            supabase.table("review_logs").insert({
                "id": log_id,
                "review_id": review_id,
                "node_name": node_name,
                "node_output": json.dumps(node_output) if not isinstance(node_output, str) else node_output
            }).execute()
        
        return review_id
    except Exception as e:
        print(f"Error storing review: {e}")
        import traceback
        traceback.print_exc()
        return None