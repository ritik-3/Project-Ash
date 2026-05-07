from __future__ import annotations

import json
from os import getenv
from pathlib import Path

import httpx
from dotenv import load_dotenv


REQUIRED_ENV = [
    "OLLAMA_BASE_URL",
    "OLLAMA_MODEL",
]


def load_local_env() -> None:
    here = Path(__file__).resolve().parent
    service_root = here.parent
    load_dotenv(service_root / ".env", override=True)


def check_env() -> list[str]:
    missing: list[str] = []
    for name in REQUIRED_ENV:
        if not getenv(name):
            missing.append(name)
    return missing


def check_ollama(base_url: str, model: str) -> tuple[bool, str]:
    try:
        with httpx.Client(timeout=10) as client:
            tags = client.get(f"{base_url.rstrip('/')}/api/tags")
            tags.raise_for_status()
            data = tags.json()
        models = [m.get("name", "") for m in data.get("models", [])]
        if any(m.startswith(model) for m in models):
            return True, "ok"
        return False, f"model '{model}' not found in Ollama tags"
    except Exception as exc:
        return False, str(exc)


def check_piper_paths() -> dict[str, str]:
    report: dict[str, str] = {}
    model_path = getenv("PIPER_VOICE_MODEL_PATH", "").strip()
    config_path = getenv("PIPER_VOICE_CONFIG_PATH", "").strip()

    if not model_path:
        report["tts"] = "Piper not configured; Windows SAPI fallback will be used"
        return report

    model_exists = Path(model_path).exists()
    report["piper_model"] = "ok" if model_exists else f"missing: {model_path}"

    if config_path:
        config_exists = Path(config_path).exists()
        report["piper_config"] = "ok" if config_exists else f"missing: {config_path}"

    return report


def main() -> None:
    load_local_env()
    missing = check_env()
    if missing:
        print(json.dumps({"status": "error", "missing_env": missing}, indent=2))
        raise SystemExit(1)

    base_url = getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = getenv("OLLAMA_MODEL", "llama3.1:8b-instruct")

    ollama_ok, ollama_detail = check_ollama(base_url, model)
    piper_report = check_piper_paths()

    payload = {
        "status": "ok" if ollama_ok else "error",
        "ollama": {
            "base_url": base_url,
            "model": model,
            "ready": ollama_ok,
            "detail": ollama_detail,
        },
        "tts": piper_report,
    }

    print(json.dumps(payload, indent=2))
    if not ollama_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
