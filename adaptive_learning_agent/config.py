import os
# Get the base directory of your project on the E: drive
# Update this string to your EXACT project folder path
BASE_DIR = r"E:\\GenAI_Master\\LLMs\\End2EndAgenticAI\\adaptive_learning_agent"

# --- Directory Configuration ---
MARKDOWN_DIR = os.path.join(BASE_DIR, "markdown_docs")
PARENT_STORE_PATH = os.path.join(BASE_DIR, "parent_store")
QDRANT_DB_PATH = os.path.join(BASE_DIR, "qdrant_db")

# --- Qdrant Configuration ---
CHILD_COLLECTION = "document_child_chunks"
SPARSE_VECTOR_NAME = "sparse"

# --- Model Configuration ---
DENSE_MODEL = "sentence-transformers/all-mpnet-base-v2"
SPARSE_MODEL = "Qdrant/bm25"
GEMINI_MODEL = "gemini-2.5-flash"
# LLM_MODEL = "qwen3:4b-instruct-2507-q4_K_M"
LLM_MODEL = "steamdj/llama3.1-cpu-only:latest"
GROQ_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0

# --- Text Splitter Configuration ---
CHILD_CHUNK_SIZE = 500
CHILD_CHUNK_OVERLAP = 100
MIN_PARENT_SIZE = 2000
MAX_PARENT_SIZE = 10000
HEADERS_TO_SPLIT_ON = [
    ("#", "H1"),
    ("##", "H2"),
    ("###", "H3")
]