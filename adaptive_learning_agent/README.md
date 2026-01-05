# Python Application

This repository contains a Python application that can be run locally with **Python 3.13**.  
Dependencies can be installed using **uv** (recommended) or standard **pip**.

---

## Requirements

- Python **3.13**
- One of the following:
  - `uv` (recommended)
  - `pip`

Check your Python version:
```bash
python --version
```
- Install with uv
```bash
pip install uv
uv pip install -r requirements.txt
```
- Install with pip
```bash
python -m venv venv
source venv/bin/activate    # Linux / macOS
venv\Scripts\activate       # Windows
pip install -r requirements.txt
```
- Create .env file in the root (the same folder with app.py), then add your token (huggingface,gemini,...) without quote (eg: GG="api_key": wrong, GG=api_key: true)
```bash
GOOGLE_API_KEY=your_api_key
HF_TOKEN=your_api_key
```
- Run app
```bash 
python app.py
```
- After run the app, upload the pdf file. Notice that the pdf file's name should not contain "." in the middle (eg: 1.Abc.pdf => won't work but 1_Abc.pdf should work)
- Click to button Add Documents
- Chat and test

- Modify logic in: 
    - config.py: gemini, ollama, ...
    - ui: gradio_app
    - rag_agent: prompts.py, tools.py, nodes.py, edges.py 
