# System Requirements

## LLM Requirements
1. **Ollama Setup**
   - Ollama must be installed and running locally
   - Ollama server must be accessible at `http://localhost:11434`
   - At least one Ollama model must be installed
   - Models can be installed using: `ollama pull <model_name>`

2. **Model Selection**
   - At startup, the application will:
     - Clear the terminal
     - Display available models in a table format with:
       - Number (1, 2, 3, ...)
       - Letter (A, B, C, ...)
       - Model name
       - Size
       - Last modified date
     - Allow selection by:
       - Number (e.g., "1")
       - Letter (e.g., "A")
       - Full model name (e.g., "llama3.2:latest")
     - Remember the selection for future sessions

3. **Selection Rules**
   - All lists requiring user selection must:
     - Be numbered (1, 2, 3, ...)
     - Have letter options (A, B, C, ...)
     - Be sorted alphabetically when applicable
     - Accept both number and letter inputs
     - Support full text matching when applicable
   - Selection prompts must clearly indicate all input options

4. **Model Verification**
   - Before starting the application, ensure:
     - Ollama service is running (`ollama serve` in background)
     - At least one model is downloaded (`ollama list` to verify)
     - Port 11434 is available and not blocked by firewall

5. **Troubleshooting**
   - If AI features are disabled, check:
     - Ollama service status
     - Model availability
     - Network connectivity to localhost:11434
     - System resources (RAM, CPU)
     - Contents of `llm_session.json`

## Python Requirements
- Python 3.8 or higher
- Required packages listed in requirements.txt
- Sufficient system memory (minimum 8GB recommended for LLM operations)

## Operating System
- Windows 10/11
- Linux (Ubuntu 20.04 or higher)
- macOS 10.15 or higher

## Getting Started
1. Install Ollama from https://ollama.ai
2. Start Ollama service
3. Pull at least one model: `ollama pull <model_name>`
4. Install Python dependencies: `pip install -r requirements.txt`
5. Start application: `python run.py`
6. Select your preferred model when prompted

## Note
The AI features of this application depend on a running LLM service. If the LLM service is not available, the application will still function but with AI features disabled.

## Configuration
- Model selection is stored in `llm_session.json`
- Delete this file to reset model selection
- The application will prompt for model selection if:
  - It's the first run
  - The saved model is no longer available
  - The configuration file is deleted or corrupted 