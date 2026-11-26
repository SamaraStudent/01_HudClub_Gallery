import json
from typing import List, Dict, Any
from config import HASHTAGS_JSON

def load_hashtags() -> List[Dict[str, Any]]:
    """Загружает список хештегов и возвращает список словарей."""
    if HASHTAGS_JSON.exists():
        with open(HASHTAGS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_hashtags(data: List[Dict[str, Any]]) -> None:
    """Сохраняет список хештегов в JSON."""
    with open(HASHTAGS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)