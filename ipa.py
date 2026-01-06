import logging
import shutil
import os 
import sys 
from phonemizer import phonemize
from phonemizer.backend.espeak.wrapper import EspeakWrapper 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if sys.platform == "darwin":
    possible_paths = [
        '/opt/homebrew/lib/libespeak-ng.dylib', 
        '/usr/local/lib/libespeak-ng.dylib',    
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            EspeakWrapper.set_library(path)
            break

LANG_MAPPING = {
    "en": "en-us",
    "fr": "fr-fr",
    "es": "es",
    "de": "de",
    "it": "it",
    "pt": "pt",
    "pl": "pl",
    "ru": "ru",
    "ja": "ja", 
    "zh": "zh"  
}

def is_backend_available() -> bool:
    """
    Checks if the 'espeak-ng' backend is installed on the system.
    """
    return shutil.which('espeak-ng') is not None or shutil.which('espeak') is not None

def get_ipa(text: str, lang_code: str) -> str:
    """
    Generates the IPA transcription for a given text.
    """
    if not text:
        return ""

    backend_lang = LANG_MAPPING.get(lang_code.lower())
    
    if not backend_lang:
        logger.warning(f"⚠️ Language '{lang_code}' not supported for IPA generation.")
        return ""

    try:
        ipa_transcription = phonemize(
            text,
            language=backend_lang,
            backend='espeak',
            strip=True,
            preserve_punctuation=True,
            with_stress=True,
            njobs=1
        )
        return ipa_transcription

    except Exception as e:
        logger.error(f"❌ IPA Generation error for '{text}': {e}")
        return ""

if __name__ == "__main__":
    print(get_ipa("Hello, how are you today?", "en"))
    print(get_ipa("Bonjour, je voudrais une baguette.", "fr"))