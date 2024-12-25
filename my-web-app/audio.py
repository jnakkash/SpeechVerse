import pyaudio
import wave
import requests

# AudD API Key
API_KEY = "028fc09d83866df1c586a113fcc0010b"

# Audio Recording Configuration
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100  # Sample rate
CHUNK = 500
RECORD_SECONDS = 10  # Duration to record
WAVE_OUTPUT_FILENAME = "microphone_recording.wav"

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Start Recording
print("Recording...")
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
frames = []

try:
    while True:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        except OSError as e:
            print(f"Error reading audio stream: {e}")
except KeyboardInterrupt:
    print("Recording stopped")

# Stop Recording
print("Recording finished.")
stream.stop_stream()
stream.close()
audio.terminate()

# Save the recording to a WAV file
with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wave_file:
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(audio.get_sample_size(FORMAT))
    wave_file.setframerate(RATE)
    wave_file.writeframes(b''.join(frames))

# Send the audio file to the AudD API
print("Recognizing audio...")
response = requests.post(
    "https://api.audd.io/",
    data={
        "api_token": API_KEY,
    },
    files={
        "file": open(WAVE_OUTPUT_FILENAME, "rb"),
    },
)

# Display the result
if response.status_code == 200:
    result = response.json()
    if result.get("status") == "success":
        print("Music recognized:")
        print(f"Title: {result['result']['title']}")
        print(f"Artist: {result['result']['artist']}")
        print(f"Album: {result['result']['album']}")
    else:
        print("Recognition failed:", result.get("error", "Unknown error"))
else:
    print(f"Error: {response.status_code}, {response.text}")
