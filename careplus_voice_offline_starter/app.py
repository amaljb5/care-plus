import json
import queue
import threading
import time
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Care+ Offline Voice Assistant", page_icon="💚", layout="centered")
SOS_MEET_URL = "https://meet.google.com/dis-vmxc-cxr"
MODEL_PATH = Path(__file__).parent / "vosk-model-small-en-in-0.4"

COMMANDS = {
    "medicines": (["medicine", "medicines", "my medicine", "my medicines", "show my medicines", "medication"], "💊 My Medicines", "Opening My Medicines. Follow the schedule provided by your clinician."),
    "appointments": (["appointment", "appointments", "my appointment", "my appointments", "next appointment"], "🗓️ My Appointments", "Opening My Appointments."),
    "wellbeing": (["wellbeing", "well being", "how am i feeling", "feeling", "daily check in", "check in"], "😊 How Am I Feeling?", "Opening How Am I Feeling. You can record how you feel, pain, and sleep."),
    "contacts": (["family", "doctor", "call family", "call my family", "call doctor", "call my doctor", "contacts"], "📞 Call Family or Doctor", "Opening Call Family or Doctor. Choose a saved contact to place a call."),
    "sos": (["sos", "emergency", "help me", "i need help", "emergency help"], "🆘 SOS", "You asked for emergency help. Please confirm before opening the SOS meeting link."),
}

def recognize_command(transcript):
    normalized = transcript.lower().strip()
    for key, (phrases, label, reply) in COMMANDS.items():
        if any(phrase in normalized for phrase in phrases):
            return key, label, reply
    return "", "", "Sorry, I didn't recognize that. Try medicines, appointments, how am I feeling, call my family, or SOS."

def offline_listen(seconds=6):
    """Capture microphone audio and decode locally using Vosk."""
    try:
        import sounddevice as sd
        from vosk import Model, KaldiRecognizer
    except ImportError as exc:
        raise RuntimeError("Dependencies are missing. Run: pip install -r requirements.txt") from exc

    if not MODEL_PATH.exists():
        raise RuntimeError(
            f"Speech model folder not found: {MODEL_PATH.name}. "
            "Download and extract the English India Vosk model into this folder."
        )

    model = Model(str(MODEL_PATH))
    recognizer = KaldiRecognizer(model, 16000)
    audio_q = queue.Queue()

    def callback(indata, frames, time_info, status):
        audio_q.put(bytes(indata))

    st.info(f"Listening for up to {seconds} seconds. Speak now.")
    with sd.RawInputStream(
        samplerate=16000, blocksize=8000, dtype="int16",
        channels=1, callback=callback
    ):
        deadline = time.time() + seconds
        transcript = ""
        while time.time() < deadline:
            try:
                data = audio_q.get(timeout=0.25)
            except queue.Empty:
                continue
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                transcript = (transcript + " " + result.get("text", "")).strip()
        final_result = json.loads(recognizer.FinalResult())
        transcript = (transcript + " " + final_result.get("text", "")).strip()
    return transcript

def speak(text):
    """Local text-to-speech via pyttsx3; browser audio is not required."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 155)
        engine.say(text)
        engine.runAndWait()
    except Exception:
        # Text response still works if the local OS TTS engine isn't available.
        pass

st.markdown("""
<div style="text-align:center;padding:8px 0">
<div style="font-size:52px">💚</div>
<h1 style="color:#123f35;margin:0">Care+ Offline Voice Assistant</h1>
<p style="color:#607d75">Speech recognition runs locally on your computer.</p>
</div>
""", unsafe_allow_html=True)

st.info("This version does not use Brave's browser speech-recognition service. After the Python packages and model are installed, speech recognition works offline.")

if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "command" not in st.session_state:
    st.session_state.command = ""
if "label" not in st.session_state:
    st.session_state.label = ""
if "reply" not in st.session_state:
    st.session_state.reply = ""
if "sos_confirmed" not in st.session_state:
    st.session_state.sos_confirmed = False

left, right = st.columns([2, 1])
with left:
    listen_seconds = st.selectbox("Listening window", [4, 6, 8, 10], index=1, format_func=lambda x: f"{x} seconds")
with right:
    st.write("")
    st.write("")
    listen_clicked = st.button("🎙️ Listen now", type="primary", use_container_width=True)

if listen_clicked:
    try:
        with st.spinner("Loading offline speech model and listening…"):
            heard = offline_listen(listen_seconds)
        if not heard:
            st.warning("I didn't hear any speech. Check your microphone and try again.")
        else:
            st.session_state.transcript = heard
            cmd, label, reply = recognize_command(heard)
            st.session_state.command = cmd
            st.session_state.label = label
            st.session_state.reply = reply
            st.session_state.sos_confirmed = False
            speak(reply)
    except Exception as exc:
        st.error(str(exc))

st.subheader("Or type a command")
with st.form("typed_command"):
    typed = st.text_input("Command", placeholder="e.g. Show my medicines")
    submitted = st.form_submit_button("Run command", use_container_width=True)
if submitted and typed.strip():
    st.session_state.transcript = typed.strip()
    cmd, label, reply = recognize_command(typed)
    st.session_state.command = cmd
    st.session_state.label = label
    st.session_state.reply = reply
    st.session_state.sos_confirmed = False
    speak(reply)

if st.session_state.transcript:
    st.markdown("#### I heard")
    st.write(f"“{st.session_state.transcript}”")
if st.session_state.reply:
    st.success(st.session_state.reply)

if st.session_state.command:
    st.markdown("---")
    st.subheader("Care+ action")
    st.write(f"**{st.session_state.label}**")
    if st.session_state.command == "sos":
        st.warning("SOS is serious. Confirm before opening the shared Google Meet link.")
        a, b = st.columns(2)
        with a:
            if st.button("Confirm SOS", type="primary", use_container_width=True):
                st.session_state.sos_confirmed = True
        with b:
            if st.button("Cancel SOS", use_container_width=True):
                st.session_state.command = ""
                st.session_state.reply = "SOS cancelled."
                st.session_state.sos_confirmed = False
                st.rerun()
        if st.session_state.sos_confirmed:
            st.link_button("🎥 Join SOS Google Meet", SOS_MEET_URL, use_container_width=True)
    else:
        st.info("The command is recognized. Integration with the real elderly dashboard is the next step.")

with st.expander("Try these commands"):
    st.markdown("- Show my medicines\n- My appointments\n- How am I feeling?\n- Call my family\n- SOS / I need help")

st.caption("Care+ prototype. It does not diagnose, prescribe, change medication, or contact emergency services automatically.")
