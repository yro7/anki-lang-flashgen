
import anki_creator
import os
import re

def test_cloze_deck_creation():
    print("Testing Cloze Deck Creation...")
    
    # Dummy data from LLM (simulated)
    # Source: "Banana"
    # Target: "Monkey eats <banana>"
    # In main.py logic (simulated in creat_flashcard logic):
    # front_text = source ("Banana")
    # back_text = target ("Monkey eats <banana>")
    
    front_text = "Banana"
    back_text = "Monkey eats <banana>"
    audio_bytes = b"fake_audio_cloze"
    
    try:
        flashcard = anki_creator.create_flashcard(
            audio_bytes=audio_bytes,
            image_bytes=None,
            front_text=front_text, 
            back_text=back_text, 
            ipa_text="",
            mode="cloze"
        )
        
        note = flashcard['note']
        fields = note.fields
        
        print(f"Fields: {fields}")
        
        # Check Cloze conversion
        if "{{c1::banana}}" in fields[0]:
            print("✅ Cloze conversion successful.")
        else:
            print(f"❌ Cloze conversion FAILED. Got: {fields[0]}")
            exit(1)
            
        # Check Extra field contains source
        if "Banana" in fields[1]:
             print("✅ Extra field contains source word.")
        else:
             print("❌ Extra field missing source word.")
             exit(1)

        filename = "test_cloze_deck.apkg"
        deck_name = "Test Cloze Deck"
        
        anki_creator.create_deck([flashcard], deck_name, filename)
        
        if os.path.exists(filename):
            print(f"✅ Deck file '{filename}' created successfully.")
            os.remove(filename)
        else:
            print(f"❌ Deck file '{filename}' was NOT created.")
            exit(1)

    except Exception as e:
        print(f"❌ Error during test: {e}")
        exit(1)

if __name__ == "__main__":
    test_cloze_deck_creation()
