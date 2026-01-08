import genanki
import os
import re
import random

MODEL_ID_TRANSLATION = 1607392319
MODEL_ID_LISTENING = 1607392320
MODEL_ID_CLOZE = 1607392321

CARD_CSS = """
.card { font-family: arial; font-size: 20px; text-align: center; color: black; background-color: white; }
.word { font-size: 32px; font-weight: bold; color: #2c3e50; margin-bottom: 20px; }
.translation { font-size: 24px; color: #8e44ad; margin-top: 10px;}
.ipa { font-family: "Lucida Sans Unicode", "Arial Unicode MS"; font-size: 18px; color: #7f8c8d; margin-top: 5px; font-style: italic; }
.audio { margin-top: 20px; }
.hint { color: #7f8c8d; font-size: 16px; margin-bottom: 10px; }
.image-container img { max-height: 300px; max-width: 100%; margin-top: 15px; border-radius: 8px; }
"""
# --- TRANSLATION MODEL  ---
# Front: Source Text
# Back: Target Text + Audio + Image + IPA
MODEL_TRANSLATION = genanki.Model(
    MODEL_ID_TRANSLATION,
    'AutoAnki: Translation',
    fields=[
        {'name': 'Question'}, {'name': 'Answer'}, 
        {'name': 'Audio'}, {'name': 'Image'}, {'name': 'IPA'}
    ],
    templates=[{
        'name': 'Translation Card',
        'qfmt': '<div class="word">{{Question}}</div>',
        'afmt': '''
        {{FrontSide}}
        <hr id="answer">
        <div class="translation">{{Answer}}</div>
        <div class="ipa">[{{IPA}}]</div>
        <div class="image-container">{{Image}}</div> 
        <div class="audio">{{Audio}}</div>
        ''',
    }],
    css=CARD_CSS
)

# --- LISTENING MODEL (Oral Comprehension) ---
# Front: Audio (Auto-play) + Icon
# Back: Target Text + Source Text + IPA
MODEL_LISTENING = genanki.Model(
    MODEL_ID_LISTENING,
    'AutoAnki: Listening',
    fields=[
        {'name': 'Question'}, {'name': 'Answer'}, 
        {'name': 'Audio'}, {'name': 'Image'}, {'name': 'IPA'}
    ],
    templates=[{
        'name': 'Listening Card',
        'qfmt': '''
        <div class="hint">🎧 Écoutez et devinez...</div>
        <div class="audio">{{Audio}}</div>
        {{type:Answer}}
        ''',
        'afmt': '''
        {{FrontSide}}
        <hr id="answer">
        {{type:Answer}}
        <div class="ipa">[{{IPA}}]</div>
        <div class="translation"><small>({{Question}})</small></div>
        ''',
    }],
    css=CARD_CSS
)

# --- CLOZE MODEL ---
MODEL_CLOZE = genanki.Model(
    MODEL_ID_CLOZE,
    'AutoAnki: Cloze',
    fields=[
        {'name': 'Text'},
        {'name': 'Extra'},
    ],
    templates=[{
        'name': 'Cloze Card',
        'qfmt': '{{cloze:Text}}\n<br><br>\n{{type:cloze:Text}}',
        'afmt': '{{cloze:Text}}\n<br><br>\n{{type:cloze:Text}}\n<hr>\n{{Extra}}',
    }],
    css=CARD_CSS,
    model_type=genanki.Model.CLOZE
)

def _sanitize_filename(text: str) -> str:
    clean = re.sub(r'[^a-zA-Z0-9]', '', text).lower()
    return clean[:20]

def create_flashcard(audio_bytes: bytes, image_bytes: bytes, front_text: str, back_text: str, ipa_text: str = "", mode: str = "translation") -> dict:
    """
    Create a flashcard selecting the right model based on 'mode'.
    """
    clean_name = _sanitize_filename(back_text if mode == "translation" else front_text)
    rand_id = random.randint(1000,9999)
    media_paths = []
    
    audio_filename = f"anki_audio_{clean_name}_{rand_id}.mp3"
    with open(audio_filename, "wb") as f:
        f.write(audio_bytes)
    media_paths.append(audio_filename)
    audio_field = f"[sound:{audio_filename}]"

    # Handle Image (Only for Translation usually, but logic is generic)
    image_field = ""
    if image_bytes:
        image_filename = f"anki_img_{clean_name}_{rand_id}.jpg"
        with open(image_filename, "wb") as f:
            f.write(image_bytes)
        media_paths.append(image_filename)
        image_field = f'<img src="{image_filename}">'

    if mode == "listening":
        target_model = MODEL_LISTENING
    elif mode == "cloze":
        target_model = MODEL_CLOZE
    else:
        target_model = MODEL_TRANSLATION

    if mode == "cloze":
        # In cloze mode, back_text contains the sentence with <word>.
        # We need to convert <word> to {{c1::word}}.
        # And we put the source word (prompt) in Extra.
        
        # Regex to find <...> and replace with {{c1::...}}
        cloze_text = re.sub(r'<(.*?)>', r'{{c1::\1}}', back_text)
        
        # Extra field: The word to guess (source) + Audio (maybe?)
        extra_field = f"<div class='translation'>{front_text}</div><div class='audio'>{audio_field}</div>"

        fields = [cloze_text, extra_field]
    else:
        fields = [front_text, back_text, audio_field, image_field, ipa_text]

    note = genanki.Note(
        model=target_model,
        fields=fields
    )
    
    return {
        "note": note,
        "media_paths": media_paths 
    }

def create_deck(flashcards_data: list, deck_name: str, output_file: str):
    deck = genanki.Deck(random.randrange(1 << 30, 1 << 31), deck_name)
    all_media_files = []

    for item in flashcards_data:
        deck.add_note(item['note'])
        all_media_files.extend(item['media_paths'])

    package = genanki.Package(deck)
    package.media_files = all_media_files
    package.write_to_file(output_file)
    
    # Clean uptemp files
    for file_path in all_media_files:
        try:
            os.remove(file_path)
        except OSError: pass

    print(f"✅ Deck created: {output_file}")