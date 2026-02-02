from __future__ import annotations

import json
import os
import time
from typing import Any, Dict

LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "events.jsonl")


def log_event(event: Dict[str, Any]) -> None:
    event = dict(event)
    event.setdefault("ts", time.time())
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
