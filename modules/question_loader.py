import os

def load_questions(filepath: str) -> str:
    """Load all field-specific questions from a given file path."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Questions file not found: {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().strip()
