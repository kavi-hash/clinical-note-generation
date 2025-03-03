from flask import Flask, request, jsonify, render_template
from pydub import AudioSegment
import speech_recognition as sr
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload_audio():
    if 'audioFile' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    audio_file = request.files['audioFile']
    file_path = os.path.join(UPLOAD_FOLDER, audio_file.filename)
    audio_file.save(file_path)
    
    wav_path = convert_audio_to_wav(file_path)
    transcript = recognize_speech(wav_path)
    
    return jsonify({"transcript": transcript})

def convert_audio_to_wav(audio_path):
    wav_path = os.path.splitext(audio_path)[0] + ".wav"
    audio = AudioSegment.from_file(audio_path)
    audio.export(wav_path, format="wav")
    return wav_path

def recognize_speech(wav_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        recognizer.adjust_for_ambient_noise(source)
        audio_data = recognizer.record(source)
    
    try:
        return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError:
        return "Could not request results from the speech recognition service."

if __name__ == '__main__':
    app.run(debug=True)
