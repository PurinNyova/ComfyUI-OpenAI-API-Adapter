# OAI ComfyUI Adapter

A Python adapter that integrates OpenAI-compatible APIs with ComfyUI for image generation.

## Quick Start

1. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

## Configuration

### Environment Setup

Create a `.env` file or modify the configuration with the following variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CONFIG_FILE` | `config.json` | Path to the configuration file |
| `WORKFLOWS_DIR` | `workflows` | Directory containing workflow definitions |
| `SAVE_IMAGE_NODE_ID` | `81` | ComfyUI node for image saving |
| `COMFYUI_BASE_URL` | `http://127.0.0.1:8188` | ComfyUI server URL |
| `APIKEY` | `DidYouKnowThatVaporeon` | API key for authentication |

### Model Configuration

Edit `config.json` to configure available models and their settings.

**Currently Supported Models:**
- ✅ Chroma
- ✅ SDXL
- ✅ Flux
You may make your own workflow following existing ones as example.

## Project Structure

```
OAIAdapter/
├── app.py                 # Main application entry point
├── config.py              # Configuration loader
├── config.json            # Model configurations
├── requirements.txt       # Python dependencies
├── v1/                    # API v1 endpoints
│   ├── images_generations.py
│   └── models.py
└── workflows/             # ComfyUI workflow definitions
    ├── chroma.json
    ├── flux.json
    ├── sdxl.json
    └── sdxl-prompt-control.json
``` 