from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(override=True)

DATA_DIR = Path("D:/medical_coding_knowledge_base_1/data")
TRACES_DIR = Path(__file__).parent.parent / "traces"
TRACES_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "anthropic/claude-haiku-4-5"
OPENROUTER_BASE_URL = "https://openrouter.ai/api"
OPENROUTER_HEADERS = {
    "HTTP-Referer": "https://github.com/AliTheAnalyst01/medical-coding-agent",
    "X-Title": "Medical Coding Agent",
}
