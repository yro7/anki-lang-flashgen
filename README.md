# AutoAnki

AutoAnki generates Anki flashcard decks (`.apkg`) for language learning using Google Gemini and Microsoft Edge TTS.

## Features

- **Topic-Based Generation**: Generates vocabulary lists based on a provided theme (e.g., "Business", "Travel", "Fruits").
- **Audio & Pronunciation**: Adds neural Text-to-Speech (TTS) and IPA transcriptions to every card.
- **Images**: Fetches relevant images for vocabulary cards.
- **Three Learning Modes**:
  - **Translation**: Standard cards (Source → Target + Image + Audio).
  - **Listening**: Audio-focused cards. You listen to the word and must type the answer.
  - **Cloze**: Fill-in-the-blank sentences (e.g., "The monkey eats a {{c1::banana}}").

## Setup

1. **Install Dependencies**
   ```bash
   pip install google-genai edge-tts genanki requests duckduckgo-search phonemizer python-dotenv
   ```
   *Note: `phonemizer` requires `espeak-ng` to be installed on your system:*
   - macOS: `brew install espeak` or `brew install espeak-ng`
   - Linux: `sudo apt install espeak-ng`

2. **Environment API Key**
   Create a `.env` file in the project root:
   ```bash
   GOOGLE_API_KEY="your_api_key_here"
   ```

## Usage

Run the script using `main.py`.

```bash
python main.py --topic "TOPIC" --target LANG_CODE [options]
```

### Arguments

| Flag | Description | Default |
| --- | --- | --- |
| `--topic`, `-p` | Topic for vocabulary generation (e.g., "Fruits"). | **Required** |
| `--target`, `-t` | Target language code (e.g., `pl`, `es`, `en`). | **Required** |
| `--source`, `-s` | Source language code. | `fr` |
| `--count`, `-c` | Number of cards to generate. | `5` |
| `--mode`, `-m` | Mode: `translation`, `listening`, or `cloze`. | `translation` |
| `--explain` | Add detailed grammatical explanations for long sentences (>4 words). | `False` |

### Examples

**Standard Vocabulary (French → Polish)**
```bash
python main.py -p "Fruits" -t pl
```

**Listening Practice (English → Spanish)**
*Audio plays, you type the Spanish word.*
```bash
python main.py -p "Business" -s en -t es -m listening
```

**Cloze Test (Contextual Sentences)**
*Fill in the missing word in a sentence. Includes full translation on the back.*
```bash
python main.py -p "Travel" -s en -t fr -m cloze
```

**With Explanations**
*Generate grammar explanations for sentences longer than 4 words.*
```bash
python main.py -p "Politics" -t de --explain
```

## Supported Languages
Uses Edge TTS neural voices for: `fr`, `en`, `es`, `de`, `pl`, `it`, `pt`, `ru`, `ja`, `zh`.