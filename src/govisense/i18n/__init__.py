"""
Multi-lingual Internationalization Module for GoviSense
Supports English (en), Sinhala (si), and Tamil (ta) for in-app alert broadcasts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

_TEMPLATES_PATH = Path(__file__).parent / "templates.json"
_TEMPLATES: Dict[str, Dict[str, str]] = {}


def _load_templates() -> Dict[str, Dict[str, str]]:
    global _TEMPLATES
    if not _TEMPLATES and _TEMPLATES_PATH.exists():
        with open(_TEMPLATES_PATH, "r", encoding="utf-8") as f:
            _TEMPLATES = json.load(f)
    return _TEMPLATES


def get_alert_message(message_key: str, lang: str = "en", **params: Any) -> str:
    """
    Renders localized alert message for given key and parameters.
    Falls back to English if requested language template is missing.
    """
    templates = _load_templates()
    key_templates = templates.get(message_key, {})
    template_str = key_templates.get(lang) or key_templates.get("en", f"[{message_key}]")

    try:
        return template_str.format(**params)
    except Exception:
        return template_str
