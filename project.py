import dotenv
import os
from datetime import datetime
from openai import AzureOpenAI
import azure.cognitiveservices.speech as speech_sdk

os.system('cls' if os.name=='nt' else 'clear')
dotenv.load_dotenv()

# ─── Speech service ────────────────────────────
SPEECH_KEY = os.getenv("SPEECH_KEY")
SPEECH_REGION = os.getenv("SPEECH_REGION")

# ─── Azure OpenAI ──────────────────────────────
AZURE_OPENAI_API_KEY=os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT=os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT=os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION=os.getenv("AZURE_OPENAI_API_VERSION")



# ▸  Guard against forgotten edits
for val in (SPEECH_KEY, AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT):
    if "YOUR_" in val:
        raise ValueError("✖  Fill in the constants at the top of the file before running.")

# ▸  Init Azure OpenAI client
gpt = AzureOpenAI(
    api_key  = AZURE_OPENAI_API_KEY,
    azure_endpoint = AZURE_OPENAI_ENDPOINT,
    api_version = AZURE_OPENAI_API_VERSION,
)

# ▸  Init SpeechConfig once (re‑use for STT & TTS)
speech_config = speech_sdk.SpeechConfig(subscription=SPEECH_KEY, region=SPEECH_REGION)
speech_config.speech_recognition_language = "en-US"
speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"   # pick any Neural voice

# ▸  Helpers
def transcribe_from_mic():
    """Listen on the default microphone and return recognized text (or None)."""
    rec = speech_sdk.SpeechRecognizer(
        speech_config,
        speech_sdk.AudioConfig(use_default_microphone=True)
    )
    print("🎙️  Listening…  (say “quit” to exit)")
    result = rec.recognize_once_async().get()
    if result.reason == speech_sdk.ResultReason.RecognizedSpeech:
        return result.text.strip()
    elif result.reason == speech_sdk.ResultReason.NoMatch:
        print("🤔  Didn’t catch that.")
    else:
        print("✖  STT Error:", result.reason)
    return None

def chat(prompt: str, *, max_tokens: int = 100) -> str:
    """Ask Azure OpenAI and return reply text."""
    resp = gpt.chat.completions.create(
        model     = AZURE_OPENAI_DEPLOYMENT,
        messages  = [{"role": "user", "content": prompt + "please reply in shortly and don't use any special characters"}],
        max_tokens = max_tokens,
    )
    return resp.choices[0].message.content.strip()

def speak(text):
    """Speak text synchronously."""
    synthesizer = speech_sdk.SpeechSynthesizer(speech_config=speech_config)
    result = synthesizer.speak_text_async(text).get()

    if result.reason != speech_sdk.ResultReason.SynthesizingAudioCompleted:
        print("✖  TTS Error:", result.reason)

def tell_time() -> str:
    """Return and speak the current local time in HH:MM AM/PM format."""
    now   = datetime.now()
    reply = now.strftime("It's %I:%M %p.")
    print("⏰", reply)
    speak(reply)
    return reply


def main():
    print("🤖  Voice ChatGPT ready at", datetime.now().strftime("%H:%M:%S"))
    TIME_PATTERNS = (
        "what time", "current time", "tell me the time",
        "time is it", "say the time"
    )

    try:
        while True:
            try:
                user = transcribe_from_mic()
            except KeyboardInterrupt:
                print("\n👋  Interrupted."); break

            if not user:
                continue
            user_lower = user.lower().strip()
            print("🗣️  You :", user)

            # Handle quit
            if user_lower in {"quit", "exit", "quit."}:
                print("👋  Bye!"); break

            # 🔹 If the utterance asks for time, skip GPT
            if any(pat in user_lower for pat in TIME_PATTERNS):
                tell_time()
                continue

            # Otherwise, go to GPT
            try:
                reply = chat(user)
                print("🤖  GPT:", reply)
                speak(reply)
            except Exception as ex:
                print("✖  GPT Error:", ex)

    except (KeyboardInterrupt, EOFError):
        print("\n👋  Bye!")

if __name__ == "__main__":
    main()
