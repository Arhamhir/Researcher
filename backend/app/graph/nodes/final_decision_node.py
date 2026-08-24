def final_decision_node(state: dict) -> dict:
    """Critic node that validates reviews and decides to retry or finalize."""
    print("[CRITIC] Starting...")
    methodology = state.get("methodology_review", {})
    novelty = state.get("novelty_review", {})
    citation = state.get("citation_review", {})
    clarity = state.get("clarity_review", {})

    retries = state.get("retries", 0)
    max_retries = 2

    issues = []
    retry_needed = False

    # Critic logic: check for contradictions and hard quality failures
    if novelty.get("score", 0) >= 8 and citation.get("score", 10) <= 4:
        issues.append(
            "Contradiction: High novelty claimed but citation support is weak."
        )
        retry_needed = True

    if methodology.get("score", 10) <= 3 and clarity.get("score", 10) >= 7:
        issues.append(
            "Contradiction: Paper is well-written but methodology is fundamentally weak."
        )
        retry_needed = True

    if methodology.get("score", 10) <= 2:
        issues.append(
            "Critical: Methodology score below minimum acceptable threshold (2/10)."
        )
        retry_needed = True

    if citation.get("score", 10) <= 2:
        issues.append("Critical: Citation grounding is too weak for acceptance.")
        retry_needed = True

    if novelty.get("similarity_max", 0.0) >= 0.95:
        issues.append("Critical: Extremely high similarity to existing work (possible overlap/plagiarism risk).")
        retry_needed = True

    # If issues found and retries available, trigger retry
    # retries counter tracks how many times we've retried (0 = first attempt, 1 = first retry, 2 = second retry)
    if retry_needed and retries < max_retries:
        next_retry = retries + 1
        print(f"[CRITIC] Retry needed (attempt {next_retry}/{max_retries})")
        
        # Calculate tentative decision even during retry
        scores = [
            methodology.get("score", 0),
            novelty.get("score", 0),
            citation.get("score", 0),
            clarity.get("score", 0)
        ]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        if avg_score >= 8.5:
            tentative_decision = "Accept"
            confidence = "High"
        elif avg_score >= 7.2:
            tentative_decision = "Weak Accept"
            confidence = "Medium"
        elif avg_score >= 5.0:
            tentative_decision = "Weak Reject"
            confidence = "Medium"
        else:
            tentative_decision = "Reject (Retry Needed)"
            confidence = "High"
        
        return {
            "critic": {
                "status": "retry",
                "issues": issues,
                "retry_count": next_retry
            },
            "final_decision": {
                "decision": tentative_decision,
                "confidence": confidence,
                "average_score": round(avg_score, 2),
                "scores": {
                    "methodology": methodology.get("score", 0),
                    "novelty": novelty.get("score", 0),
                    "citation": citation.get("score", 0),
                    "clarity": clarity.get("score", 0)
                },
                "justification": f"Tentative decision based on current scores (retry {next_retry}/{max_retries})."
            },
            "retries": next_retry
        }
    
    # Either no issues found OR max retries reached - finalize with decision
    if retry_needed and retries >= max_retries:
        print(f"[CRITIC] Max retries ({max_retries}) reached. Finalizing despite issues.")

    # Calculate final decision based on average scores
    scores = [
        methodology.get("score", 0),
        novelty.get("score", 0),
        citation.get("score", 0),
        clarity.get("score", 0)
    ]
    avg_score = sum(scores) / len(scores) if scores else 0

    methodology_score = methodology.get("score", 0)
    novelty_score = novelty.get("score", 0)
    citation_score = citation.get("score", 0)
    clarity_score = clarity.get("score", 0)
    max_similarity = novelty.get("similarity_max", 0.0)

    hard_reject = (
        methodology_score <= 3
        or citation_score <= 2
        or max_similarity >= 0.99
    )

    # Stricter decision policy
    if hard_reject:
        decision = "Reject"
        confidence = "High"
        if methodology_score <= 4:
            issues.append("Hard reject: methodology does not meet minimum scientific rigor.")
        if citation_score <= 3:
            issues.append("Hard reject: insufficient literature grounding.")
        if max_similarity >= 0.97:
            issues.append("Hard reject: near-duplicate similarity detected.")
    elif avg_score >= 8.0 and min(methodology_score, novelty_score, citation_score, clarity_score) >= 6.5:
        decision = "Accept"
        confidence = "High"
    elif avg_score >= 6.0 and min(methodology_score, citation_score, clarity_score) >= 5:
        decision = "Weak Accept"
        confidence = "Medium"
    elif avg_score >= 4.0:
        decision = "Weak Reject"
        confidence = "Medium"
    else:
        decision = "Reject"
        confidence = "High"

    print(f"[CRITIC] Finalized with decision: {decision}, avg score: {avg_score:.2f}")

    return {
        "critic": {
            "status": "finalize",
            "issues": issues if issues else [],
            "retry_count": retries
        },
        "final_decision": {
            "decision": decision,
            "confidence": confidence,
            "average_score": round(avg_score, 2),
            "scores": {
                "methodology": methodology.get("score", 0),
                "novelty": novelty.get("score", 0),
                "citation": citation.get("score", 0),
                "clarity": clarity.get("score", 0)
            },
            "justification": f"Based on {len(scores)} review criteria with average score {avg_score:.1f}/10."
        },
        "retries": retries,
    }
