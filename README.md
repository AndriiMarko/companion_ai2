# Companion AI

Companion AI is an interactive virtual companion system that combines a **3D animated character**, a **chat-based UI**, and an **AI brain** powered by a local LLM.  
It’s designed to provide a more personal and engaging AI interaction experience.

---

## 📦 Project Overview

The project consists of **three main components**:

### 1. **User App (Unity)**
- Displays a **3D companion character** in a real-time environment.
- Includes a **chat interface** for text-based conversations.
- Handles:
  - Rendering and animations.
  - Sending/receiving chat messages.
  - Displaying AI responses with character expressions.

### 2. **Python Server**
- Acts as the **communication hub** between the User App and the AI model.
- Responsibilities:
  - Managing **WebSocket** or **HTTP** connections with the client.
  - Storing **chat history** for context.
  - Crafting prompts for the AI model.
  - Optionally using **tool calls** for extended functionalities (e.g., fetching data, triggering actions).

### 3. **Ollama Server**
- Hosts and runs the **Local LLM** (Large Language Model).
- Receives prompts from the Python server.
- Returns AI-generated responses.
- Runs completely locally for **privacy** and **offline capability**.

---

## 🛠 Architecture

# Ollama Setup and Usage Guide

This guide walks you through installing Ollama, setting up a custom model folder, adding GGUF and Safetensors models, and using the `OllamaCharacter` and `MessengerUI` Python classes to create a modern messenger-style chat application. The instructions are beginner-friendly and cover Linux, macOS, and Windows.

## Prerequisites

- **Python 3.8+**: Ensure Python is installed. Check with `python --version` or `python3 --version`.
- **pip**: Python's package manager. Verify with `pip --version`.
- **Internet connection**: Required for downloading Ollama and models.
- **Terminal access**: For running commands (Command Prompt on Windows, Terminal on Linux/macOS).

## Step 1: Install Ollama

Ollama is a lightweight tool for running large language models locally. Follow these steps to install it:

### Linux
1. Open a terminal.
2. Run the following command to download and install Ollama:
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
3. Verify installation:
   ```bash
   ollama --version
   ```

### macOS
1. Download the Ollama installer from [ollama.com](https://ollama.com).
2. Double-click the downloaded `.dmg` file and drag the Ollama app to your Applications folder.
3. Open a terminal and run:
   ```bash
   ollama --version
   ```
   If it’s not recognized, ensure `/Applications/Ollama.app/Contents/MacOS` is in your PATH or run `/Applications/Ollama.app/Contents/MacOS/ollama`.

### Windows
1. Download the Ollama installer from [ollama.com](https://ollama.com).
2. Run the `.exe` installer and follow the prompts.
3. Open Command Prompt or PowerShell and verify:
   ```bash
   ollama --version
   ```

### Start the Ollama Server
Run the following command in a terminal to start the Ollama server:
```bash
ollama serve
```
This runs the server at `http://localhost:11434`. Keep this terminal open while using Ollama.

## Step 2: Set a Custom Model Folder

By default, Ollama stores models in `~/.ollama/models` (Linux/macOS) or `%USERPROFILE%\.ollama\models` (Windows). To use a custom folder:

1. **Choose a folder**: For example, `/path/to/custom/models` (Linux/macOS) or `C:\path\to\custom\models` (Windows).
2. **Set the environment variable**:
   - **Linux/macOS**:
     ```bash
     export OLLAMA_MODELS=/path/to/custom/models
     ```
     Add this line to `~/.bashrc` or `~/.zshrc` for persistence.
   - **Windows**:
     Open Command Prompt as Administrator and run:
     ```cmd
     setx OLLAMA_MODELS "C:\path\to\custom\models"
     ```
     Restart your terminal or computer for the change to take effect.
3. **Verify**: Run `ollama serve` and check that models are saved to the custom folder.

Ensure the folder exists and has write permissions. Create it if needed:
```bash
mkdir -p /path/to/custom/models  # Linux/macOS
mkdir C:\path\to\custom\models  # Windows
```

## Step 3: Add GGUF and Safetensors Models

Ollama supports GGUF models natively, but Safetensors models require conversion. Here’s how to add both:

### Adding a GGUF Model
1. **Download a GGUF model**: Visit a model repository like [Hugging Face](https://huggingface.co/models?filter=gguf) and download a GGUF model file (e.g., `llama3.2.gguf`).
2. **Create a Modelfile**: Create a file named `Modelfile` in the same directory as the GGUF file with the following content:
   ```modelfile
   FROM ./llama3.2.gguf
   ```
3. **Import the model**:
   ```bash
   ollama create my-llama3.2 -f /path/to/Modelfile
   ```
   Replace `/path/to/Modelfile` with the path to your `Modelfile`.
4. **Verify**:
   ```bash
   ollama list
   ```
   You should see `my-llama3.2` listed.

### Adding a Safetensors Model
Safetensors models need conversion to GGUF format first.

1. **Download a Safetensors model**: Find a model on [Hugging Face](https://huggingface.co/models?filter=safetensors) (e.g., a model with `.safetensors` files).
2. **Convert to GGUF**:
   - Install the `llama.cpp` conversion tools:
     ```bash
     git clone https://github.com/ggerganov/llama.cpp
     cd llama.cpp
     pip install -r requirements.txt
     ```
   - Convert the Safetensors model to GGUF:
     ```bash
     python convert.py --outtype gguf --outfile converted_model.gguf /path/to/safetensors/model
     ```
     Replace `/path/to/safetensors/model` with the path to your model files.
3. **Create a Modelfile** for the converted GGUF model (as above).
4. **Import the model**:
   ```bash
   ollama create my-converted-model -f /path/to/Modelfile
   ```
5. **Verify**:
   ```bash
   ollama list
   ```

## Step 4: Set Up the Python Environment

To use the `OllamaCharacter` and `MessengerUI` classes, install the required Python packages:

1. **Install dependencies**:
   ```bash
   pip install langchain langchain-community tkinter
   ```
   Note: Tkinter is usually included with Python, but ensure it’s available (`python -m tkinter`).

2. **Save the Python code**:
   - Save the `OllamaCharacter` class as `ollama_character.py`.
   - Save the `MessengerUI` class as `messenger_ui.py`.
   Ensure both files are in the same directory.

## Step 5: Run the Messenger App

Here’s how to use the provided code to interact with your character:

1. **Ensure Ollama server is running**:
   ```bash
   ollama serve
   ```
2. **Run the messenger app**:
   ```bash
   python messenger_ui.py
   ```
   This launches a Tkinter window with a modern chat interface.

3. **Interact with the character**:
   - Type a message in the input field and press Enter or click "Send".
   - The character (e.g., Elara) responds based on their personality, conversation history, and context.

### Example Interaction
Assuming you’re using the `llama3.2` model:

- **User Input**: "Hey Elara, found any treasure lately?"
- **Context**: "On a derelict spaceship"
- **Character Response**: Displayed in a white chat bubble, e.g., "Elara: Argh, matey! Just rummaged through this rusty ol’ spaceship and found a crate of quantum doubloons—shiny, but useless without a decoder!"

The app maintains short-term memory (last 5 interactions) and long-term memory (conversation summary) as defined in `OllamaCharacter`.

## Troubleshooting

- **Ollama not running**: Ensure `ollama serve` is active and the server is accessible at `http://localhost:11434`.
- **Model not found**: Verify the model name (`my-llama3.2`) matches in `ollama list` and `ollama_character.py`.
- **Tkinter issues**: Ensure Tkinter is installed (`python -m tkinter`). On Linux, you may need `sudo apt-get install python3-tk`.
- **Connection errors**: Check firewall settings or try a different port if `11434` is blocked.

## Additional Notes

- **Model storage**: GGUF models are typically smaller and optimized for Ollama. Safetensors conversion may require significant disk space and CPU resources.
- **Performance**: Ensure your system has enough RAM (at least 8GB for smaller models like `llama3.2`).
- **Customization**: Modify `character_name`, `character_description`, and `context` in `messenger_ui.py` to change the character or scenario.

For further details, visit [Ollama’s documentation](https://ollama.com/docs) or [LangChain’s documentation](https://python.langchain.com/docs).
