CARE+ OFFLINE VOICE ASSISTANT (LOCAL PROTOTYPE)

1. Extract this folder.
2. Open terminal in this folder.
3. Install packages:
     pip install -r requirements.txt
4. Download a Vosk English India model.
   Try the model named vosk-model-small-en-in-0.4 from the official Vosk models page:
     https://alphacephei.com/vosk/models
   Extract it so the folder is alongside app.py and is named exactly:
     vosk-model-small-en-in-0.4
   The final structure should be:
     app.py
     requirements.txt
     vosk-model-small-en-in-0.4/   (contains model files)
5. Run:
     streamlit run app.py

If pip install sounddevice fails on Windows, try updating pip first:
     python -m pip install --upgrade pip
   Then rerun pip install -r requirements.txt.
If the microphone device is not available, check Windows microphone privacy settings and close other apps using it.

This prototype listens for a fixed number of seconds after you press Listen now. Vosk recognition is local/offline after setup.
It recognizes commands and speaks responses; real dashboard navigation is a later integration step.
SOS asks for confirmation and opens the shared Google Meet link; it does not call emergency services.
