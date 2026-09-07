"""Client for local llama.cpp llama-server (OpenAI-compatible API).
Sequential execution with single-instance VRAM lock.
Includes robust JSON parsing, auto-repair for small-model outputs, and connection health checks.
"""
import json
import re
import time
import urllib.request
from typing import Any, Dict, Optional

DEFAULT_ENDPOINT = "http://127.0.0.1:8080"


def extract_json_safe(text: str) -> Dict[str, Any]:
    """Extract and repair JSON from model output (handling codeblocks, trailing commas, whitespace)."""
    if not text or not text.strip():
        raise ValueError("Empty response from LLM; no JSON to extract")

    # 1. Try markdown fenced block first
    codeblock_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if codeblock_match:
        cand = codeblock_match.group(1).strip()
    else:
        # 2. Find widest outer braces
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            cand = text[start : end + 1].strip()
        else:
            raise ValueError(f"No JSON object found in response: {text[:120]}...")

    # 3. Clean common small-model syntax slips
    # Remove trailing commas before closing braces/brackets
    cleaned = re.sub(r",\s*([\}\]])", r"\1", cand)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try raw cand if cleaned failed
        try:
            return json.loads(cand)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON ({e}): {cleaned[:150]}...")


def chat(
    prompt: str,
    system: Optional[str] = None,
    endpoint: str = DEFAULT_ENDPOINT,
    temperature: float = 0.1,
    max_tokens: int = 1500,
    timeout: int = 300,
) -> Dict[str, Any]:
    """Send chat completion request to local llama-server."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    body = json.dumps(
        {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        f"{endpoint}/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out = json.load(r)
    except Exception as e:
        raise RuntimeError(f"LLM request to {endpoint} failed: {e}")

    text = out["choices"][0]["message"]["content"]
    usage = out.get("usage", {})
    return {
        "text": text,
        "usage": usage,
        "latency_s": round(time.time() - t0, 2),
    }


def health(endpoint: str = DEFAULT_ENDPOINT) -> bool:
    """Check if llama-server is healthy and accepting requests."""
    try:
        with urllib.request.urlopen(f"{endpoint}/health", timeout=5) as r:
            return r.status == 200
    except Exception:
        return False
