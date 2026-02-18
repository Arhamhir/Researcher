import re

# Map many possible headings to canonical section names
HEADER_MAP = {
    "abstract": "abstract",
    "introduction": "introduction",
    "background": "introduction",
    "related work": "related_work",
    "literature review": "related_work",
    "methodology": "methodology",
    "methods": "methodology",
    "method": "methodology",
    "materials and methods": "methodology",
    "materials & methods": "methodology",
    "approach": "methodology",
    "experimental setup": "methodology",
    "experimental settings": "methodology",
    "implementation": "methodology",
    "implementation details": "methodology",
    "model architecture": "methodology",
    "system architecture": "methodology",
    "experiments": "results",
    "evaluation": "results",
    "results": "results",
    "analysis": "results",
    "discussion": "conclusion",
    "findings": "conclusion",
    "conclusion": "conclusion",
    "conclusions": "conclusion",
    "future work": "conclusion",
    "limitations": "conclusion",
    "discussions": "conclusion",
    "acknowledgements": "acknowledgements",
    "acknowledgments": "acknowledgements",
    "references": "references",
    "bibliography": "references",
}

# Regex to detect section headings at line starts, with optional numbering and punctuation
HEADER_PATTERN = re.compile(
    r"(?im)^(?:\d+(?:\.\d+)*[\.\)]?\s+)?(?P<header>" + "|".join(re.escape(h) for h in HEADER_MAP.keys()) + r")\s*:?\s*$"
)


def _normalize_heading(line: str) -> str:
    normalized = line.strip().lower()
    normalized = re.sub(r"^(section\s+)?(?:\d+(?:\.\d+)*|[ivxlcdm]+)[\.)]?\s+", "", normalized)
    normalized = normalized.replace("&", "and")
    normalized = re.sub(r"\s*:\s*$", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def parse_sections(clean_text: str) -> dict:
    """Parse sections from cleaned text using line-anchored headings.

    Heuristics:
    - Detect numbered headings (e.g., "1 Introduction", "2.3 Methods")
    - Map multiple synonyms to canonical names
    - If there is preface text before the first heading and no explicit abstract,
      treat that preface (up to 1200 chars) as the abstract.
    - If nothing is detected, return full_text fallback.
    """
    lines = clean_text.splitlines()
    headings = []

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # Heading candidates should be reasonably short and line-anchored
        if len(stripped) > 90:
            continue

        normalized = _normalize_heading(stripped)
        canonical = HEADER_MAP.get(normalized)
        if canonical:
            headings.append((idx, canonical))
            continue

        # Allow short headings that start with a known header prefix
        for header in sorted(HEADER_MAP.keys(), key=len, reverse=True):
            if normalized.startswith(header + " "):
                headings.append((idx, HEADER_MAP[header]))
                canonical = HEADER_MAP[header]
                break
        if canonical:
            continue

        match = HEADER_PATTERN.match(stripped)
        if match:
            canonical = HEADER_MAP.get(match.group("header").lower())
            if canonical:
                headings.append((idx, canonical))

    # Keep only first occurrence for each canonical section
    seen = set()
    ordered = []
    for line_idx, name in sorted(headings, key=lambda item: item[0]):
        if name in seen:
            continue
        seen.add(name)
        ordered.append((line_idx, name))

    sections = {}

    # Preface before first heading can act as abstract if plausible length
    if ordered:
        first_idx = ordered[0][0]
        preface = "\n".join(lines[:first_idx]).strip()
        preface_words = len(preface.split())
        if preface and "abstract" not in seen and 40 <= preface_words <= 350:
            sections["abstract"] = preface

    if not ordered:
        return sections if sections else {"full_text": clean_text.strip()}

    for i, (line_idx, name) in enumerate(ordered):
        start = line_idx + 1  # exclude heading line itself
        end = ordered[i + 1][0] if i + 1 < len(ordered) else len(lines)
        content = "\n".join(lines[start:end]).strip()
        if content:
            sections[name] = content

    # Minimal fallbacks when parser misses common titles
    if "introduction" not in sections:
        intro_match = re.search(r"(?is)\bintroduction\b\s*(.+?)(?:\n\s*\d+\.?\s*|\n\s*methods?\b|\n\s*related work\b|\Z)", clean_text)
        if intro_match:
            sections["introduction"] = intro_match.group(1).strip()

    if "methodology" not in sections:
        method_match = re.search(
            r"(?is)\b(methodology|methods?|experimental setup|implementation)\b\s*(.+?)"
            r"(?:\n\s*\d+\.?\s*|\n\s*results?\b|\n\s*experiments?\b|\n\s*evaluation\b|\n\s*discussion\b|\n\s*conclusion\b|\Z)",
            clean_text,
        )
        if method_match:
            sections["methodology"] = method_match.group(2).strip()

    return sections if sections else {"full_text": clean_text.strip()}


