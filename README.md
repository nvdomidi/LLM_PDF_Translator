# LLM PDF Translator

LLM PDF Translator summarizes and translates PDF documents using local or hosted large language models.

## Features
- Summarize a document to provide translation context.
- Translate PDFs while preserving the original layout.
- Configure different LLM endpoints via `config.yaml`.

## Configuration
Edit `config.yaml` to choose the model and base URL for the desired endpoint.

### Ollama
```yaml
base_url: http://ollama-gpu:11434
model: "gemma3:1b"
```
The `base_url` must use the container name of your Ollama server (e.g., `ollama-gpu`) when running on the `ollama-network` Docker network.

### OpenRouter
```yaml
base_url: "https://openrouter.ai/api/v1"
model: "google/gemma-3-27b-it:free"
```

### OpenAI
```yaml
base_url: "https://api.openai.com/v1"
model: "gpt-4o-mini"
```

When using OpenRouter or OpenAI, update `core/translate.py` to initialize `OpenAIClient` instead of `OllamaClient` so that the correct API client is used.

## Environment Variables
Create a `.env` file with the necessary API keys:
```
OPENAI_API_KEY=your-openai-key
OPENROUTER_API_KEY=your-openrouter-key
```
Only the key for the chosen endpoint is required.

## Build and Run
Build the Docker image:
```bash
docker build -t llm-pdf-translator .
```

Run the container, mapping the Streamlit port and connecting to the Ollama network:
```bash
docker run --rm -it --network=ollama-network -p 8765:8501 llm-pdf-translator
```

The app will be available at `http://localhost:8765`.
