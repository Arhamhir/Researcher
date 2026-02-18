from app.graph.graph import build_graph
import json

# Test case 1: Good paper that should pass
print("=" * 80)
print("TEST CASE 1: High-quality paper (should finalize without retry)")
print("=" * 80)

state_good = {
    "paper_sections": {
        "abstract": "This paper proposes a novel transformer-based approach for clinical note summarization using domain-specific pretraining and clinician feedback loops.",
        "introduction": "Recent work has explored deep learning methods for text summarization in healthcare. However, existing approaches lack integration of domain expertise.",
        "methodology": "We conduct a rigorous controlled experiment with 500k clinical notes, proper train/test splits, statistical validation using ANOVA (p<0.05), and clinician evaluation with inter-rater reliability (Cohen's kappa=0.82). Our approach includes proper baselines and ablation studies.",
        "related_work": "Prior studies (Smith et al., 2023; Doe et al., 2024) use encoder-decoder models. Recent work by Zhang et al. (2025) explores attention mechanisms. However, few studies integrate clinician feedback loops as shown by Johnson et al. (2024).",
        "conclusion": "We achieve statistically significant improvements over baselines and discuss future integration in EHR systems with proper validation protocols."
    }
}

graph = build_graph()
result_good = graph.invoke(state_good)

print(json.dumps({
    "methodology_review": result_good.get("methodology_review"),
    "novelty_review": result_good.get("novelty_review"),
    "citation_review": result_good.get("citation_review"),
    "clarity_review": result_good.get("clarity_review"),
    "critic": result_good.get("critic"),
    "final_decision": result_good.get("final_decision"),
    "retries": result_good.get("retries", 0)
}, indent=2))

# Test case 2: Poor methodology that should trigger retry
print("\n" + "=" * 80)
print("TEST CASE 2: Weak methodology (should trigger retry)")
print("=" * 80)

state_poor = {
    "paper_sections": {
        "abstract": "This paper uses machine learning.",
        "introduction": "ML is good.",
        "methodology": "We trained a model.",
        "related_work": "",
        "conclusion": "It works."
    }
}

result_poor = graph.invoke(state_poor)

print(json.dumps({
    "methodology_review": result_poor.get("methodology_review"),
    "novelty_review": result_poor.get("novelty_review"),
    "citation_review": result_poor.get("citation_review"),
    "clarity_review": result_poor.get("clarity_review"),
    "critic": result_poor.get("critic"),
    "final_decision": result_poor.get("final_decision"),
    "retries": result_poor.get("retries", 0)
}, indent=2))

