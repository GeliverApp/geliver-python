from __future__ import annotations


# Keep in sync with python/pyproject.toml when running from source.
_FALLBACK_VERSION = "0.3.2"


def sdk_version() -> str:
    try:
        from importlib.metadata import version

        return version("geliver")
    except Exception:
        return _FALLBACK_VERSION


def default_user_agent() -> str:
    return f"geliver-python/{sdk_version()}"

