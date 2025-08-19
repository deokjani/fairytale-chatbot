from src.v2.params import TTS_API_KEY
from google.cloud import texttospeech
import io


async def synthesize_text(text: str, speaker: str, speed: float):
    """Synthesizes speech from the input string of text."""
    client = texttospeech.TextToSpeechClient(client_options={"api_key": TTS_API_KEY})

    input_text = texttospeech.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=speaker,
        # ssml_gender=texttospeech.SsmlVoiceGender.MALE,
    )

    audio_encoding = texttospeech.AudioEncoding.MP3
    if "Chirp" in speaker:
        speed = None
        audio_encoding = texttospeech.AudioEncoding.LINEAR16

    audio_config = texttospeech.AudioConfig(
        speaking_rate=speed,
        audio_encoding=audio_encoding
    )

    response = client.synthesize_speech(
        request={"input": input_text, "voice": voice, "audio_config": audio_config}
    )
    return io.BytesIO(response.audio_content)
