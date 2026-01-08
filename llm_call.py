import os
import json
import pprint
from google import genai
from google.genai import types

if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("Missing GOOGLE_API_KEY env variable.")

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])


SYSTEM_PROMPT = """

You are an expert linguist and a strict data formatting assistant for an Anki flashcard generator.

### GOAL
Generate a list of high-quality vocabulary words or short phrases based on a specific TOPIC provided by the user, translating them from a SOURCE language to a TARGET language.

### GUIDELINES
1. **Format**: Output strictly a valid JSON array. NO Markdown code blocks (like ```json), NO conversational text. Just the raw JSON string.
2. **Structure**: Each object must have exactly two keys: "source" and "target".
3. **Grammar**: ALWAYS include definite articles for nouns (e.g., "Le chien" instead of "chien", "Der Tisch" instead of "Tisch") to teach gender.
4. **Context**: Choose the translation best suited for the specific TOPIC.

### ONE-SHOT EXAMPLE
User Input:
Topic: "Weather"
Source: "en"
Target: "fr"
Count: 3

Your Output:
[
  {"source": "The sun", "target": "Le soleil"},
  {"source": "The rain", "target": "La pluie"},
  {"source": "The wind", "target": "Le vent"}
]

### INSTRUCTION
Now, generate the JSON for the following request:

"""

async def generate_text(topic: str, source_lang: str, target_lang: str, count: int, mode: str = "translation") -> list:
    """
    Generate vocabulary list.
    Args:
        mode: 'translation' (default) or 'listening'.
    """
    
    mode_instruction = ""
    if mode == "listening":
        mode_instruction = "CONTEXT: This list is for an Oral Comprehension exercise. Choose words/phrases that are distinct and good for listening practice."
    elif mode == "cloze":
        mode_instruction = """CONTEXT: This list is for a CLOZE DELETION test. 
        For each item:
        - "source": The word to guess (in Source Language).
        - "target": A full sentence in Target Language containing the translated word, where the word to guess is surrounded by angle brackets like <word>.
        Example: Source="Banana", Target="The monkey eats a <banana>."
        """

    user_prompt = f"""
    Topic: "{topic}"
    Source: "{source_lang}"
    Target: "{target_lang}"
    Count: {count}
    {mode_instruction}
    
    Generate the JSON list now.
    """

    print(f"⏳ (Gemini) Generation for : '{topic}' (Mode: {mode})...")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.4,
                response_mime_type="application/json"
            )
        )

        raw_content = response.text
        vocab_list = json.loads(raw_content)
        
        print(f"✅ Reçu {len(vocab_list)} cartes.")
        return vocab_list

    except json.JSONDecodeError:
        print("❌ Error: The returned JSON is malformed.")
        return []
    except Exception as e:
        print(f"❌ Gemini API Error : {e}")
        return []

# Quick test
if __name__ == "__main__":
    import asyncio
    print("--- Test Translation ---")
    res = asyncio.run(generate_text("Salutations", "fr", "en", 2, mode="translation"))
    print(json.dumps(res, indent=2))
    
    print("\n--- Test Listening ---")
    res = asyncio.run(generate_text("Salutations", "fr", "en", 2, mode="listening"))
    print(json.dumps(res, indent=2))