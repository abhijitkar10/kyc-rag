"""The LLM is a swappable component. This module hides which provider we use.

Picks a provider by which API key is present (checked in this order):
  1. GEMINI_API_KEY / GOOGLE_API_KEY  -> Google Gemini (free tier)
  2. ANTHROPIC_API_KEY                -> Claude Haiku 4.5

Keys are read from the environment, or from a local `.env` file (gitignored)
so the friend can just drop a key in one place. Nothing here logs the key.

Design note (interview-worthy): retrieval is the hard part of this project;
the generator is a commodity behind a one-function interface — proof the
architecture doesn't depend on any single vendor.
"""

import os
from pathlib import Path

# gemini-2.0-flash now has ZERO free-tier quota (Google moved the free tier
# to the 2.5 family) -- 2.5-flash is the current free-tier workhorse.
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
CLAUDE_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5")


def _load_dotenv() -> None:
    """Minimal .env reader (no dependency). KEY=value per line, # comments ok."""
    env = Path(".env")
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def provider() -> tuple[str, str]:
    """Return (provider_name, model) for the key that's available."""
    _load_dotenv()
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return "gemini", GEMINI_MODEL
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "claude", CLAUDE_MODEL
    raise RuntimeError(
        "No LLM key found. Set GEMINI_API_KEY (free key: "
        "https://aistudio.google.com/apikey) in your shell or in a .env file, "
        "or set ANTHROPIC_API_KEY."
    )


def complete(system: str, user: str, max_tokens: int = 1024) -> str:
    """One completion. Deterministic (temperature 0) for reproducible eval."""
    name, model = provider()
    if name == "gemini":
        return _gemini(system, user, max_tokens, model)
    return _claude(system, user, max_tokens, model)


def _gemini(system: str, user: str, max_tokens: int, model: str) -> str:
    from google import genai
    from google.genai import types

    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    client = genai.Client(api_key=key)
    resp = client.models.generate_content(
        model=model,
        contents=user,
        config=types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
            temperature=0,
            # 2.5 models spend "thinking" tokens out of max_output_tokens,
            # which truncates short answers; RAG answers are grounded in the
            # provided context, so buy the full budget back.
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return resp.text or ""


def _claude(system: str, user: str, max_tokens: int, model: str) -> str:
    import anthropic

    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if b.type == "text")


if __name__ == "__main__":
    name, model = provider()
    print(f"active provider: {name} ({model})")
    print(complete("You are terse.", "Say 'ready' and nothing else."))
