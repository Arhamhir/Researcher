def _classify_decision(avg_score, methodology_score, novelty_score, citation_score, clarity_score, max_similarity):
    """Single, consistently-calibrated decision policy.

    No single noisy sub-score can tank an otherwise strong paper unless it
    reflects a genuinely fundamental problem (unsound methods, or
    near-duplicate content). Everything else is judged on the overall
    average with a floor on the weakest dimensions, so one harsh reviewer
    or one section-detection miss can't override four good signals.
    """
    hard_reject = (
        methodology_score <= 3
        or max_similarity >= 0.99
        # Citation weakness alone isn't disqualifying - papers routinely cite
        # inline without a labeled section, and citation is the noisiest of
        # the four signals. Only treat it as fatal alongside a weak average.
        or (citation_score <= 2 and avg_score < 5.0)
    )
    if hard_reject:
        return "Reject", "High"

    if avg_score >= 8.0 and min(methodology_score, novelty_score, citation_score, clarity_score) >= 6.0:
        return "Accept", "High"
    if avg_score >= 6.5 and min(methodology_score, citation_score, clarity_score) >= 4.5:
        return "Weak Accept", "Medium"
    if avg_score >= 4.5:
        return "Weak Reject", "Medium"
    return "Reject", "High"


def final_decision_node(state: dict) -> dict:
    """Critic node: aggregates the four reviews into one calibrated decision.

    Note: this used to have a "retry" branch that returned a tentative
    decision (with its own, harsher thresholds) whenever it flagged a
    contradiction between reviewers. The graph never actually looped back
    to re-run the reviewers though (critic -> END unconditionally), so that
    tentative decision was silently becoming the permanent one - on the
    coarser of two threshold tables - any time a contradiction heuristic
    fired. Removed; contradictions are now surfaced as informational notes
    only, and every paper is judged by the one calibrated policy below.
    """
    print("[CRITIC] Starting...")
    methodology = state.get("methodology_review") or {}
    novelty = state.get("novelty_review") or {}
    citation = state.get("citation_review") or {}
    clarity = state.get("clarity_review") or {}

    methodology_score = methodology.get("score", 0)
    novelty_score = novelty.get("score", 0)
    citation_score = citation.get("score", 0)
    clarity_score = clarity.get("score", 0)
    max_similarity = novelty.get("similarity_max", 0.0)

    scores = [methodology_score, novelty_score, citation_score, clarity_score]
    avg_score = sum(scores) / len(scores) if scores else 0

    # Informational notes only - none of these override the score-based
    # decision below on their own.
    issues = []
    if novelty_score >= 8 and citation_score <= 4:
        issues.append(
            "Note: high novelty alongside comparatively weak citation support - worth a second look, not necessarily a flaw."
        )
    if methodology_score <= 3 and clarity_score >= 7:
        issues.append(
            "Note: methodology and clarity are being judged independently and diverge here."
        )
    if max_similarity >= 0.95:
        issues.append("Note: high similarity to existing work detected during the novelty check.")

    decision, confidence = _classify_decision(
        avg_score, methodology_score, novelty_score, citation_score, clarity_score, max_similarity
    )

    if decision == "Reject":
        if methodology_score <= 3:
            issues.append("Reject: methodology does not meet minimum scientific rigor.")
        if citation_score <= 2 and avg_score < 5.0:
            issues.append("Reject: insufficient literature grounding.")
        if max_similarity >= 0.99:
            issues.append("Reject: near-duplicate similarity detected.")

    print(f"[CRITIC] Finalized with decision: {decision}, avg score: {avg_score:.2f}")

    return {
        "critic": {
            "status": "finalize",
            "issues": issues,
            "retry_count": 0,
        },
        "final_decision": {
            "decision": decision,
            "confidence": confidence,
            "average_score": round(avg_score, 2),
            "scores": {
                "methodology": methodology_score,
                "novelty": novelty_score,
                "citation": citation_score,
                "clarity": clarity_score,
            },
            "justification": f"Based on {len(scores)} review criteria with average score {avg_score:.1f}/10.",
        },
    }
