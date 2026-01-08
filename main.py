import asyncio
import argparse
import sys
from dotenv import load_dotenv

load_dotenv()

# Custom modules
import anki_creator
import image_api
import llm_call
import tts_call
import ipa

def parse_arguments():
    """
    Configures and parses CLI arguments.
    """
    parser = argparse.ArgumentParser(
        description="AutoAnki: AI-powered Flashcard Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        "--topic", "-p",
        type=str,
        required=True,
        help="The topic or theme for the vocabulary list (e.g., 'Fruits', 'Business meetings')."
    )

    parser.add_argument(
        "--target", "-t",
        type=str,
        required=True,
        help="Target language code (e.g., 'pl', 'en', 'es')."
    )

    # Optional arguments
    parser.add_argument(
        "--source", "-s",
        type=str,
        default="fr",
        help="Source language code."
    )

    parser.add_argument(
        "--count", "-c",
        type=int,
        default=5,
        help="Number of flashcards to generate."
    )

    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["translation", "listening", "cloze"],
        default="translation",
        help="Generation mode: 'translation' (standard text), 'listening' (audio focus), or 'cloze' (fill-in-the-blank)."
    )

    parser.add_argument(
        "--explain", 
        action="store_true",
        help="Enable detailed grammar explanations for long sentences."
    )

    return parser.parse_args()

def print_usage():
    """
    Prints the manual usage instructions and examples to the console.
    """
    usage_text = """
AutoAnki - AI Flashcard Generator
=================================

Usage:
  python main.py --topic "TOPIC" --target LANG_CODE [options]

Required Arguments:
  -p, --topic    The subject or theme of the vocabulary list (e.g., "Fruits").
  -t, --target   The target language code (e.g., "pl", "en", "es").

Optional Arguments:
  -s, --source   The source language code (default: "fr").
  -c, --count    Number of flashcards to generate (default: 5).
  -m, --mode     Generation mode:
                 • 'translation'   (Standard: Source -> Target + Audio + Image)
                 • 'listening' (Audio Focus: Audio -> Target + Source)

Examples:
  # Standard generation (French to Polish)
  python main.py -p "Les jours de la semaine" -t pl

  # Listening mode with specific count (English to Spanish)
  python main.py --topic "Business Meetings" --source en --target es --mode listening --count 10
    """
    print(usage_text)
    
async def main():
    
    print("aaa")
    if len(sys.argv) == 1:
        print_usage()
        sys.exit(1)
        
    args = parse_arguments()

    print("╔═════════════════════════════════════════╗")
    print("║   AutoAnki - Flashcard Generator        ║")
    print("╚═════════════════════════════════════════╝")
    print(f"🔹 Topic:    {args.topic}")
    print(f"🔹 Mode:     {args.mode}")
    print(f"🔹 Lang:     {args.source} -> {args.target}")
    print(f"🔹 Count:    {args.count}")
    print("-------------------------------------------")

    vocab_list = await llm_call.generate_vocab(
        topic=args.topic,
        source_lang=args.source,
        target_lang=args.target,
        count=args.count,
        mode=args.mode 
    )

    if not vocab_list:
        print("❌ No vocabulary generated. Exiting.")
        sys.exit(1)

    flashcards = []
    for i, card in enumerate(vocab_list, 1):
        print(f"   [{i}/{len(vocab_list)}] Processing: {card['source']} -> {card['target']}")

        # Defaults
        front = ""
        back = ""
        translation_text = ""
        audio = None
        image = None
        text_for_ipa = ""

        if args.mode == "listening":
            front = card['source'] 
            back = card['target']  
            text_for_ipa = card['target']
            audio = await tts_call.generate_audio(card['target'], args.target)
            image = None 

        elif args.mode == "cloze":
            # Cloze:
            # Source = word to guess (displayed in Extra)
            # Target = sentence with <word>
            # Translation = full sentence translation
            front = card['source']
            back = card['target']
            text_for_ipa = "" # usually no IPA for full sentence cloze, or maybe yes? keeping empty for now as per previous logic
            
            translation_text = card.get('translation', '')

            # Audio for the full sentence (removed < > for natural reading)
            clean_sentence = card['target'].replace("<", "").replace(">", "")
            audio = await tts_call.generate_audio(clean_sentence, args.target)
            image = None

        else: 
            # Translation : Front = Source, Back = Target
            front = card['source']
            back = card['target']
            text_for_ipa = card['target']

            audio = await tts_call.generate_audio(back, args.target)
            image = image_api.get(card['source'])

        # --- Explanation Logic ---
        explanation_html = ""
        target_sentence_for_expl = card['target'].replace("<", "").replace(">", "") # Clean for analysis
        word_count = len(target_sentence_for_expl.split())
        
        if args.explain and word_count >= 3:
            explanation_html = await llm_call.generate_explanation(
                sentence=target_sentence_for_expl,
                source_lang=args.source,
                target_lang=args.target
            )

        ipa_transcription = ipa.get_ipa(text_for_ipa, args.target) if text_for_ipa else ""

        flashcard = anki_creator.create_flashcard(
            audio, 
            image, 
            front, 
            back, 
            ipa_text=ipa_transcription,
            translation_text=translation_text,
            explanation_text=explanation_html,
            mode=args.mode,
        )
        flashcards.append(flashcard)

        # Rate limiting kindness
        if args.explain:
            await asyncio.sleep(1.5)

    deck_name = f"{args.mode.capitalize()}: {args.topic}"
    filename = f"anki_{args.topic.replace(' ', '_')}_{args.target}.apkg"
    
    anki_creator.create_deck(flashcards, deck_name=deck_name, output_file=filename)
    
if __name__ == "__main__":
    asyncio.run(main())