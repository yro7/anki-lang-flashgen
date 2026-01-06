# AutoAnki: AI-Powered Flashcard Generator

**AutoAnki** is a command-line tool that automates the creation of high-quality Anki flashcard decks (`.apkg`). By leveraging **Google Gemini** for linguistic intelligence and **Microsoft Edge TTS** for natural-sounding audio, it generates vocabulary lists based on any specific topic you provide.

## 🚀 Features

* **Topic-Based Generation:** Simply provide a theme (e.g., "Business Meetings", "Fruits", "Slang"), and the AI generates relevant vocabulary.
* **Multi-Modal Flashcards:**
* **Text:** Source and target language translations (context-aware).
* **Audio:** High-quality Neural TTS (Text-to-Speech) for pronunciation.
* **Images:** Automatic image fetching for visual association (Translation mode).


* **Dual Modes:**
* `translation`: Standard vocabulary cards (Source → Target + Image + Audio).
* `listening`: Focused on oral comprehension (Audio → Target + Source).


* **Direct Export:** Outputs ready-to-import `.apkg` files.

## 🛠️ Prerequisites

* Python 3.9+
* A Google Gemini API Key

## 📦 Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/autoanki.git
cd autoanki

```


2. **Install dependencies:**
Create a `requirements.txt` with the following content and install it:
```text
google-genai
edge-tts
genanki
requests

```


Run the install command:
```bash
pip install -r requirements.txt

```


3. **Set up Environment Variables:**
You must export your Google API key as an environment variable.
**Linux/macOS:**
```bash
export GOOGLE_API_KEY="your_actual_api_key_here"

```


**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY="your_actual_api_key_here"

```



## 💻 Usage

Run the script using `main.py`. The tool uses `argparse` for flexible configuration.

### Syntax

```bash
python main.py --topic "TOPIC" --target LANG_CODE [options]

```

### Arguments

| Flag | Long Flag | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `-p` | `--topic` | ✅ | - | The subject/theme of the vocabulary list. |
| `-t` | `--target` | ✅ | - | Target language code (e.g., `pl`, `es`, `en`). |
| `-s` | `--source` | ❌ | `fr` | Source language code. |
| `-c` | `--count` | ❌ | `5` | Number of flashcards to generate. |
| `-m` | `--mode` | ❌ | `translation` | Generation mode: `translation` or `listening`. |

### Examples

**1. Standard French to Polish vocabulary (Fruits):**

```bash
python main.py --topic "Fruits" --source fr --target pl --count 10

```

*Generates visual cards with French on the front and Polish on the back.*

**2. English to Spanish Listening Practice:**

```bash
python main.py --topic "Business Meetings" --source en --target es --mode listening

```

*Generates audio-focused cards. The front plays audio; the back reveals the text.*

## 📂 Project Structure

* `main.py`: Entry point. Handles argument parsing and orchestrates the workflow.
* `llm_call.py`: Interfaces with Google Gemini to generate structured JSON vocabulary lists.
* `tts_call.py`: Generates audio assets using `edge-tts`.
* `anki_creator.py`: Uses `genanki` to package media and text into an `.apkg` file.
* `image_api.py`: Fetches relevant images for the cards.

## 🌍 Supported Languages (TTS)

The tool currently supports optimized neural voices for:

* French (`fr`)
* English (`en`)
* Spanish (`es`)
* German (`de`)
* Polish (`pl`)
* Italian (`it`)
* Portuguese (`pt`)
* Russian (`ru`)
* Japanese (`ja`)
* Chinese (`zh`)

*Note: You can extend `VOICE_MAPPING` in `tts_call.py` to add more languages.*

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

---