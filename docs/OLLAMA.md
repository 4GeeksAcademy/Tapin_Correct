# Local Ollama Setup

This file contains quick steps to get Ollama running locally and how to
configure the project to use it for development.

1. Install Ollama

- macOS (Homebrew):

  ```bash
  brew install ollama
  ```

- Official installer (cross-platform):
  ```bash
  curl -sSf https://ollama.ai/install.sh | sh
  ```

2. Pull or run a model

- Pull a model (example):

  ```bash
  ollama pull mistral
  ```

- Or run a model interactively:
  ```bash
  ollama run mistral
  ```

3. Verify the HTTP API

- The Ollama HTTP API listens on `http://localhost:11434` by default.
  List models with:
  ```bash
  curl -s http://localhost:11434/api/models | jq .
  ```

4. Configure the project

- Copy `.env.example` to `.env` and set:

  ```ini
  LLM_PROVIDER=ollama
  OLLAMA_MODEL=mistral
  ```

- The backend already attempts to load `.env` during startup (if
  `python-dotenv` is installed). `python-dotenv` is listed in
  `src/backend/requirements.txt`.

5. Quick check script

- Run the small helper to check Ollama setup:
  ```bash
  python3 scripts/check_ollama.py
  ```

If you want me to also make the `HybridLLM` use the Ollama HTTP API
directly as a fallback (when the `langchain_community` connector is not
installed), I can add that change.
