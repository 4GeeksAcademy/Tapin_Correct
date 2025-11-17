#!/usr/bin/env python3
"""Simple health checker for a local Ollama installation.

Checks for either the Ollama HTTP API at localhost:11434 or the
presence of the `ollama` CLI. Prints helpful next steps if not found.
"""
import json
import shutil
import subprocess
import sys
import urllib.request


def check_http_api():
    url = "http://localhost:11434/api/models"
    try:
        with urllib.request.urlopen(url, timeout=2) as resp:
            data = resp.read().decode("utf-8")
            print("Ollama HTTP API reachable at:", url)
            try:
                parsed = json.loads(data)
                print("Models:")
                for m in parsed:
                    print(" -", m.get("name") if isinstance(m, dict) else m)
            except Exception:
                print(data[:1000])
            return True
    except Exception:
        return False


def check_cli():
    if shutil.which("ollama"):
        try:
            out = subprocess.check_output([
                "ollama",
                "ls",
            ], stderr=subprocess.STDOUT, text=True)
            print("Ollama CLI available. Output of `ollama ls`:\n")
            print(out)
            return True
        except subprocess.CalledProcessError as e:
            print("Ollama CLI present but `ollama ls` failed:\n", e.output)
            return False
    return False


def main():
    ok = False
    if check_http_api():
        ok = True
    elif check_cli():
        ok = True

    if ok:
        print("\nOllama appears to be available in your environment.")
        print(
            "Set `OLLAMA_MODEL` in your `.env` to the model name you want to"
        )
        sys.exit(0)

    print("\nOllama does not appear to be running or installed on this"
          " machine.")
    print("Common setup steps:")
    print(" - Install Ollama (macOS Homebrew): `brew install ollama`")
    print(
        " - Or use the official installer:"
    )
    print("   curl -sSf https://ollama.ai/install.sh | sh")
    print(
        " - Pull or start a model, for example: `ollama pull mistral`"
    )
    print("   or: `ollama run mistral`")
    print(" - Start Ollama daemon (if needed) and retry this script:")
    print("     curl -s http://localhost:11434/api/models | jq .")
    sys.exit(2)


if __name__ == "__main__":
    main()
