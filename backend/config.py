"""
config.py – Centralised application configuration
===================================================
All environment variables are loaded here.  Every other module should import
from this file rather than calling os.getenv() directly.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (two levels up from this file)
_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")

# ── Logging ───────────────────────────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── LLM Provider ─────────────────────────────────────────────────────────────
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai").lower()
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GOOGLE_MODEL: str = os.getenv("GOOGLE_MODEL", "gemini-3.6-flash")

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_PATH: str = os.getenv("DATABASE_PATH", str(_ROOT / "financial_advisor.db"))

# ── OCR ───────────────────────────────────────────────────────────────────────
TESSERACT_PATH: str | None = os.getenv("TESSERACT_PATH")

# ── Knowledge Base ────────────────────────────────────────────────────────────
KNOWLEDGE_BASE_DIR: Path = _ROOT / os.getenv("KNOWLEDGE_BASE_DIR", "knowledge_base")
CHROMA_PERSIST_DIR: Path = _ROOT / os.getenv("CHROMA_PERSIST_DIR", "chroma_db")

# ── App ───────────────────────────────────────────────────────────────────────
APP_DEBUG: bool = os.getenv("APP_DEBUG", "false").lower() == "true"

# ── Supported file extensions ─────────────────────────────────────────────────
SUPPORTED_IMAGE_EXTENSIONS: tuple[str, ...] = (".jpg", ".jpeg", ".png")
SUPPORTED_PDF_EXTENSIONS: tuple[str, ...] = (".pdf",)

# ── Expense categories ────────────────────────────────────────────────────────
EXPENSE_CATEGORIES: list[str] = [
    "Food",
    "Transport",
    "Shopping",
    "Entertainment",
    "Bills",
    "Healthcare",
    "Education",
    "Groceries",
    "Travel",
    "Rent",
    "Utilities",
    "Others",
]


def get_llm_api_key() -> str:
    """Return the API key for the active LLM provider.

    Raises
    ------
    EnvironmentError
        If the required key is not set.
    """
    if LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise EnvironmentError(
                "OPENAI_API_KEY is not set. "
                "Please add it to your .env file or environment variables."
            )
        return OPENAI_API_KEY
    elif LLM_PROVIDER == "google":
        if not GOOGLE_API_KEY:
            raise EnvironmentError(
                "GOOGLE_API_KEY is not set. "
                "Please add it to your .env file or environment variables."
            )
        return GOOGLE_API_KEY
    else:
        raise EnvironmentError(
            f"Unsupported LLM_PROVIDER '{LLM_PROVIDER}'. "
            "Set LLM_PROVIDER to 'openai' or 'google'."
        )


def get_llm():
    """Return an initialised LangChain LLM for the active provider.

    Returns
    -------
    BaseChatModel
        A LangChain chat model instance.
    """
    get_llm_api_key()  # validate key exists first

    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=OPENAI_MODEL,
            api_key=OPENAI_API_KEY,
            temperature=0.3,
        )
    elif LLM_PROVIDER == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=GOOGLE_MODEL,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.3,
        )


def extract_llm_text(response) -> str:
    """Extract plain text from an LLM response, handling both old and new
    langchain-google-genai response formats.

    Older versions return response.content as a str.
    Newer versions return response.content as a list of content blocks.
    """
    content = response.content if hasattr(response, "content") else str(response)
    if isinstance(content, list):
        # New format: [{'type': 'text', 'text': '...', ...}, ...]
        parts = [
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        ]
        return "".join(parts)
    return str(content)
