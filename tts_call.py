import edge_tts

VOICE_MAPPING = {
    "fr": "fr-FR-VivienneNeural",     
    "pl": "pl-PL-MarekNeural",         
    "en": "en-US-RogerNeural",         
    "es": "es-ES-AlvaroNeural",        
    "de": "de-DE-ConradNeural",        
    "it": "it-IT-DiegoNeural",         
    "pt": "pt-PT-DuarteNeural",        
    "ru": "ru-RU-DmitryNeural",        
    "ja": "ja-JP-KeitaNeural",         
    "zh": "zh-CN-YunxiNeural"          
}

async def generate_audio(text: str, target_language: str) -> bytes:
    """
    Generate audio TTS for the given text in the target language, using Microsoft Edge TTS.
    Returns raw audio bytes.
    """
    voice = VOICE_MAPPING.get(target_language.lower(), "en-US-RogerNeural")
    try:
        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return audio_data

    except Exception as e:
        print(f"❌ Error TTS for generation for '{text}': {e}")
        return b""