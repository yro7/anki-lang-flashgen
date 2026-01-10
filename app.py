
import streamlit as st
import asyncio
import os
import time
import llm_call
import tts_call
import image_api
import ipa
import anki_creator

# Page Configuration
st.set_page_config(
    page_title="AutoAnki Generator",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AutoAnki: AI Flashcard Generator")
st.markdown("Create Anki decks automatically with AI-powered translations, images, and audio.")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API Key Handling
    api_key = st.text_input("Google Gemini API Key", type="password", help="Get your key from Google AI Studio")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    
    st.divider()
    
    # Language Selection
    source_lang = st.selectbox("Source Language", ["fr", "en", "es", "de", "it", "pl", "ru", "ja", "zh"], index=0)
    target_lang = st.selectbox("Target Language", ["en", "fr", "es", "de", "it", "pl", "ru", "ja", "zh"], index=5) # Default Polish
    
    st.info(f"Generating cards from **{source_lang.upper()}** to **{target_lang.upper()}**.")

# Main Interface
col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input("Topic / Theme", placeholder="e.g., 'Fruits', 'Business Meetings', 'Travel to Japan'")
    
with col2:
    mode = st.selectbox("Mode", ["translation", "listening", "cloze", "custom", "declension"])

with st.expander("Advanced Options"):
    count = st.slider("Number of cards", min_value=1, max_value=20, value=5)
    explain = st.checkbox("Include Grammar Explanations", value=False, help="Adds detailed grammar explanations for longer sentences.")

# Logic Function (Adapted from main.py)
async def generate_deck(topic, source, target, count, mode, explain, progress_bar, status_text):
    
    # 1. Generate Vocabulary List
    status_text.text("🧠 Generating vocabulary list with Gemini...")
    vocab_list = await llm_call.generate_vocab(
        topic=topic,
        source_lang=source,
        target_lang=target,
        count=count,
        mode=mode
    )
    
    if not vocab_list:
        st.error("❌ No vocabulary generated. Please check your API key or Topic.")
        return None

    flashcards = []
    total = len(vocab_list)
    
    # 2. Process each card
    for i, card in enumerate(vocab_list, 1):
        status_text.text(f"⚡ Processing card {i}/{total}...")
        
        # Determining log names
        if mode == "declension":
            c_source = card.get('root_word', 'Unknown')
            c_target = card.get('declined_word', 'Unknown')
        else:
            c_source = card.get('source', 'Unknown')
            c_target = card.get('target', 'Unknown')
            
        progress_bar.progress(i / total, text=f"Creating: {c_source} -> {c_target}")

        # Defaults
        front = ""
        back = ""
        translation_text = ""
        audio = None
        image = None
        text_for_ipa = ""
        explanation_html = ""
        extra_kwargs = {}

        # --- Mode Specific Logic (Copied & Adapted from main.py) ---
        if mode == "custom":
            front = card['source']
            back = card['target']
            
        elif mode == "declension":
            translation_text = card['sentence_fr']
            root_word = card['root_word']
            declined_word = card['declined_word']
            case_info = f"{card['case_name_source']} ({card['case_name_target']})"
            
            # Formatting for Cloze
            full_sentence = card['sentence_pl_masked'].replace("___", f"{{{{c1::{declined_word}}}}}")
            back = full_sentence 
            
            # Audio & Explanation
            raw_sentence = card['sentence_pl_masked'].replace("___", declined_word)
            audio = await tts_call.generate_audio(raw_sentence, target)
            
            explanation_html = await llm_call.generate_explanation(
                sentence=raw_sentence,
                source_lang=source,
                target_lang=target,
                mode="declension"
            )
            extra_kwargs = {"root_word": root_word, "case_info": case_info}

        elif mode == "listening":
            front = card['source']
            back = card['target']
            text_for_ipa = card['target']
            audio = await tts_call.generate_audio(card['target'], target)

        elif mode == "cloze":
            front = card['source']
            back = card['target']
            translation_text = card.get('translation', '')
            clean_sentence = card['target'].replace("<", "").replace(">", "")
            audio = await tts_call.generate_audio(clean_sentence, target)

        else: # Translation
            front = card['source']
            back = card['target']
            text_for_ipa = card['target']
            audio = await tts_call.generate_audio(back, target)
            image_query = card['source']
            # Run image fetch in a thread/sync way if needed, assuming image_api is sync
            # image_api.get is likely sync based on name, checking main.py... yes it is called directly
            # But in Streamlit we might want to be careful. It's fine.
            image = image_api.get(image_query)

        # --- General Explanation Logic ---
        if mode != "declension":
            target_sentence = card.get('target', '').replace("<", "").replace(">", "")
            word_count = len(target_sentence.split())
            if explain and word_count >= 3:
                explanation_html = await llm_call.generate_explanation(
                    sentence=target_sentence,
                    source_lang=source,
                    target_lang=target
                )

        # IPA
        ipa_transcription = ""
        if text_for_ipa:
            # IPA generation might fail if espeak not installed, but it handles exceptions.
            ipa_transcription = ipa.get_ipa(text_for_ipa, target)

        # Create Card Object
        flashcard = anki_creator.create_flashcard(
            audio, image, front, back, 
            ipa_text=ipa_transcription,
            translation_text=translation_text,
            explanation_text=explanation_html,
            mode=mode,
            **extra_kwargs
        )
        flashcards.append(flashcard)
        
        # Rate Limiting
        if explain:
             await asyncio.sleep(1.0)
    
    # 3. Create Deck File
    deck_name = f"{mode.capitalize()}: {topic}"
    safe_topic = topic.replace(" ", "_").replace("/", "-")
    filename = f"anki_{safe_topic[:30]}_{target}.apkg"
    
    anki_creator.create_deck(flashcards, deck_name=deck_name, output_file=filename)
    return filename

# Button
if st.button("🚀 Generate Deck", type="primary"):
    if not os.environ.get("GOOGLE_API_KEY"):
        st.error("Please enter a Google API Key in the sidebar.")
    elif not topic:
        st.warning("Please enter a Topic.")
    else:
        progress_bar = st.progress(0, text="Starting...")
        status_text = st.empty()
        
        try:
            filename = asyncio.run(generate_deck(topic, source_lang, target_lang, count, mode, explain, progress_bar, status_text))
            
            if filename:
                progress_bar.progress(1.0, text="Done!")
                status_text.success("🎉 Deck generated successfully!")
                
                with open(filename, "rb") as f:
                    btn = st.download_button(
                        label="📥 Download .apkg",
                        data=f,
                        file_name=filename,
                        mime="application/octet-stream"
                    )
                
                # Optional: Display preview of last card?
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
            import traceback
            st.code(traceback.format_exc())

