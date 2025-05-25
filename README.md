# SLIDEGEN_AI

SLIDEGEN_AI is a Python-based project to generate PowerPoint presentations from AI-generated outlines, using Azure OpenAI, LangChain, python-pptx, and Streamlit for interactive UI.  
It also includes functionality to convert PPTX slides to images using Windows COM automation.

---

## Features

- Generate structured presentation outlines via Azure OpenAI and LangChain prompt templates.
- Convert AI outlines (JSON) into fully formatted PowerPoint (.pptx) slides.
- Interactive web interface using Streamlit to input prompts, preview outlines, and download presentations.
- Convert PowerPoint slides to images (PNG) on Windows using COM automation.
- Modular and well-structured codebase for easy customization and extension.

---

## Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/username/slidegen_ai.git
   cd ai_slide_maker
   ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Configure environment variables:
    ```bash
    @echo off
    set AZURE_OPENAI_API_KEY=your_api_key
    set AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
    set AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
    set AZURE_OPENAI_API_VERSION=2025-01-01-preview

    set PYTHONPATH=%cd%
    ```

## Usage
### Running the Streamlit App

- Run the interactive UI to generate presentations:
    ```bash
    streamlit run app/main.py
    ```

## License
MIT License © 2025 Ubeyd Khoiri