from __future__ import annotations

import os
from typing import Any, Dict, Optional

def is_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY") and os.getenv("LANGFUSE_HOST"))


def get_langfuse_client():
    if not is_enabled():
        return None
    from langfuse import get_client  # type: ignore
    return get_client()


def get_langfuse_callback(trace_id: Optional[str] = None, session_id: Optional[str] = None, user_id: Optional[str] = None):
    if not is_enabled():
        return None
    from langfuse.langchain import CallbackHandler  # type: ignore

    # CallbackHandler supports passing trace/session/user metadata.
    # Not all fields are required; Langfuse will generate IDs if omitted.
    kwargs: Dict[str, Any] = {}
    if trace_id:
        kwargs["trace_id"] = trace_id
    if session_id:
        kwargs["session_id"] = session_id
    if user_id:
        kwargs["user_id"] = user_id
    return CallbackHandler(**kwargs)


def score(trace_id: str, name: str, value: float, comment: str = "", metadata: Optional[Dict[str, Any]] = None) -> None:
    client = get_langfuse_client()
    if not client:
        return
    # v3 SDK supports `score` on the client
    client.score(
        trace_id=trace_id,
        name=name,
        value=value,
        comment=comment or None,
        metadata=metadata or None,
    )
