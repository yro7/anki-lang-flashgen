import os
import json
import pprint
import asyncio
import random
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

if "GOOGLE_API_KEY" not in os.environ:
    raise ValueError("Missing GOOGLE_API_KEY env variable.")

client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])



VOCAB_SYSTEM_PROMPT = """

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

EXPLANATION_SYSTEM_PROMPT = """
You are an expert linguist.

### GOAL
Provide a **concise and direct** grammatical explanation in the **SOURCE LANGUAGE**.

### RULES
1.  **Language**: Write the ENTIRE explanation in the **Source Language** requested (e.g., if Source is French, explain in French).
2.  **No Chatter**: Do NOT include introduction text ("Here is...", "This sentence is...", "Excellent example!") or conclusion text ("Keep it up!").
3.  **Focus**: Highlight the **Grammar logic** (Cases, Conjugations, Gender agreement).
    *   Avoid analyzing every single word separately if it's trivial. Merge concepts (e.g. "Preposition 'w' + Locative case").
4.  **Format**:
    *   Start with a **Translation** (Literal vs Natural if different).
    *   Follow with a **Key Analysis** bullet list.
    *   **MANDATORY**: End with a **Recap Box** summarizing the specific Conjugations or Declensions used in this sentence.
    *   Use HTML for styling.

### STYLE GUIDE (HTML)
- <b>Verb</b>: <span style='color: #e74c3c;'>Red</span>
- <b>Noun/Subject</b>: <span style='color: #3498db;'>Blue</span>
- <b>Grammar Rule/Case</b>: <span style='color: #27ae60;'>Green</span>
- <b>Recap Box</b>: Use a light border or background (e.g., `<div style='background-color: #f0f0f0; padding: 8px; border-radius: 4px; margin-top: 10px;'>`).

### ONE-SHOT EXAMPLE OUTPUT (HTML)
<div style="font-size: 15px;">
  <p><b>Traductions :</b><br>
  <i>Lit :</i> Je vais au magasin.<br>
  <i>Nat :</i> Je vais faire des courses.</p>
  
  <p><b>Analyse :</b></p>
  <ul>
    <li><span style='color: #e74c3c;'><b>Idę</b></span> : Verbe <i>iść</i> (aller), 1ère pers. sing. (sujet 'Ja' implicite).</li>
    <li><span style='color: #3498db;'><b>do sklepu</b></span> : "au magasin". La préposition <i>do</i> déclenche le <span style='color: #27ae60;'><b>Génitif</b></span> (<i>sklep</i> → <i>sklepu</i>).</li>
  </ul>

  <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 10px; border-left: 4px solid #3498db;'>
    <b>Rappel Grammaire :</b><br>
    🔹 <b>Génitif (Masc.)</b> : Terminaison <i>-u</i> ou <i>-a</i> (ici <i>sklep</i> + <i>u</i>).<br>
    🔹 <b>Verbe <i>Iść</i> (Présent)</b> : Idę, Idziesz, Idzie...
  </div>
</div>

### OUTPUT FORMAT
Return ONLY the raw HTML string.
"""

async def generate_vocab(topic: str, source_lang: str, target_lang: str, count: int, mode: str = "translation") -> list:
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
        - "translation": The full sentence translated back into Source Language.
        Example: Source="Banana", Target="The monkey eats a <banana>.", Translation="Le singe mange une banane."
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
                system_instruction=VOCAB_SYSTEM_PROMPT,
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
    res = asyncio.run(generate_vocab("Salutations", "fr", "en", 2, mode="translation"))
    print(json.dumps(res, indent=2))
    
    print("\n--- Test Listening ---")
    res = asyncio.run(generate_vocab("Salutations", "fr", "en", 2, mode="listening"))
    print(json.dumps(res, indent=2))

    print("\n--- Test Explanation ---")
    expl = asyncio.run(generate_explanation("J'habite à Paris.", "fr", "en"))
    print(expl)

async def generate_explanation(sentence: str, source_lang: str, target_lang: str) -> str:
    """
    Generate a grammatical explanation for a sentence.
    """
    prompt = f"""
    Source Language: "{source_lang}"
    Target Language: "{target_lang}"
    Sentence to explain: "{sentence}"
    
    Explain the grammar, structure, and nuances.
    """
    
    print(f"🧠 (Gemini) Generating explanation for : '{sentence}'...")

    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=EXPLANATION_SYSTEM_PROMPT,
                    temperature=0.7,
                    response_mime_type="text/plain"
                )
            )
            return response.text
        except Exception as e:
            error_str = str(e)
            if "503" in error_str or "429" in error_str:
                if attempt < max_retries - 1:
                    wait_time = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"⚠️ Service overloaded, retrying in {wait_time:.1f}s... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    continue
            
            print(f"❌ Gemini API Error (Explanation) : {e}")
            return "<p>Error generating explanation.</p>"
            
    return "<p>Error: Could not generate explanation (Service Busy).</p>"