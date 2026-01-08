
import anki_creator
import os

def test_listening_deck_creation():
    print("Testing Listening Deck Creation...")
    
    # Dummy data
    audio_bytes = b"fake_audio_data"
    image_bytes = None
    front_text = "Hello" # In listening mode, this is the source text (e.g. "Bonjour")? No.
    # checking main.py: 
    # if args.mode == "listening":
    #     front = card['source'] 
    #     back = card['target']  
    
    # In anki_creator:
    # clean_name = _sanitize_filename(back_text if mode == "translation" else front_text)
    
    front_text = "House"
    back_text = "Maison"
    ipa_text = "/me.zɔ̃/"
    
    try:
        flashcard = anki_creator.create_flashcard(
            audio_bytes=audio_bytes,
            image_bytes=image_bytes,
            front_text=front_text, # "House"
            back_text=back_text,   # "Maison"
            ipa_text=ipa_text,
            mode="listening"
        )
        
        print("✅ Flashcard created.")
        
        filename = "test_listening_deck.apkg"
        deck_name = "Test Listening Deck"
        
        anki_creator.create_deck([flashcard], deck_name, filename)
        
        if os.path.exists(filename):
            print(f"✅ Deck file '{filename}' created successfully.")
            # os.remove(filename) # Keep it if we want to check, or remove. I'll remove it.
        else:
            print(f"❌ Deck file '{filename}' was NOT created.")
            exit(1)

    except Exception as e:
        print(f"❌ Error during test: {e}")
        exit(1)

if __name__ == "__main__":
    test_listening_deck_creation()
