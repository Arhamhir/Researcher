import os 
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "AI_Research_Paper_Analayst"
ENV = os.getenv("ENV", "development")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
# Accept whichever Supabase key the project was provisioned with.
SUPABASE_KEY = (
    os.getenv("SUPABASE_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_ANON_KEY")
)

# Groq Configuration (OpenAI-compatible chat completions API).
# Groq has no embeddings endpoint, so it is used for chat only - see
# app/services/embeddings.py for how novelty similarity is computed instead.
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_BASE = os.getenv("GROQ_API_BASE", "https://api.groq.com/openai/v1")
# openai/gpt-oss-20b and openai/gpt-oss-120b are the models Groq confirms
# support strict JSON Schema structured outputs (see llm_client.py).
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
# Reasoning depth for gpt-oss models: none/low/medium/high. Kept low by
# default so reasoning tokens don't crowd out the JSON answer within
# max_completion_tokens across four parallel review calls.
GROQ_REASONING_EFFORT = os.getenv("GROQ_REASONING_EFFORT", "low")

# Local embedding vector size used for the novelty similarity check (see
# app/services/embeddings.py). Align with the existing `embedding` column's
# vector dimension in Supabase if one is already provisioned; store_section()
# pads/truncates on mismatch as a fallback.
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "1536"))
