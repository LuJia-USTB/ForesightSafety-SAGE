from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping


def resolve_api_key(
    config: Mapping[str, Any],
    config_path: str | Path,
) -> str:
    """Resolve an API key only from the explicitly configured environment variable."""
    if "api_key" in config:
        raise ValueError(
            f"Inline api_key values are not supported in {config_path}. "
            "Use api_key_env to reference an environment variable instead."
        )

    api_key_env = config.get("api_key_env")
    if not isinstance(api_key_env, str) or not api_key_env.strip():
        raise ValueError(f"LLM config missing api_key_env: {config_path}")

    api_key_env = api_key_env.strip()
    api_key = os.getenv(api_key_env)
    if not api_key:
        raise RuntimeError(
            f"Environment variable {api_key_env!r} specified by {config_path} is not set."
        )

    return api_key
