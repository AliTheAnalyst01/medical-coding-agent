from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

DATA_DIR = Path("D:/medical_coding_knowledge_base_1/data")
TRACES_DIR = Path(__file__).parent.parent / "traces"
TRACES_DIR.mkdir(exist_ok=True)

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
MODEL = "claude-sonnet-4-6"
