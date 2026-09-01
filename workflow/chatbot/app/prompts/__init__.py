from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent


def load_recommendation_prompt() -> str:
    """Carga la plantilla de recomendación desde app/prompts/."""
    return (PROMPTS_DIR / "recommendation_prompt.txt").read_text(encoding="utf-8")


def load_smalltalk_prompt() -> str:
    """Carga la plantilla de smalltalk desde app/prompts/."""
    return (PROMPTS_DIR / "smalltalk_prompt.txt").read_text(encoding="utf-8")


def load_guide_prompt() -> str:
    """Carga la plantilla de guía conversacional desde app/prompts/."""
    return (PROMPTS_DIR / "guide_prompt.txt").read_text(encoding="utf-8")
