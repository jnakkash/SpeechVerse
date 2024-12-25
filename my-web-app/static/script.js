let mediaRecorder; // To manage recording
let audioChunks = []; // To store audio data

// DOM elements
const recordBtn = document.getElementById("record-btn");
const stopBtn = document.getElementById("stop-btn");
const status = document.getElementById("status");
const recognizedSongDiv = document.getElementById("recognized-song");
const otherSongsDiv = document.getElementById("other-songs");

recordBtn.addEventListener("click", async () => {
    try {
        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        status.textContent = "Recording in progress... 🎙️";
        
        // Set up MediaRecorder
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        // When data is available, push it to audioChunks
        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        // Handle stop event
        mediaRecorder.onstop = async () => {
            const blob = new Blob(audioChunks, { type: "audio/wav" });
            const formData = new FormData();
            formData.append("audio", blob, "recording.wav");

            status.textContent = "Processing audio... 🎧";

            // Send the audio file to the backend
            const response = await fetch("/recognize", {
                method: "POST",
                body: formData,
            });

            const result = await response.json();
            if (result.error) {
                status.textContent = "Recognition failed: " + result.error;
            } else {
                displayResults(result);
                status.textContent = "Recognition complete! ✅";
            }
        };

        // Start recording
        mediaRecorder.start();
        recordBtn.disabled = true;
        stopBtn.disabled = false;
        status.textContent = "Recording started... Press Stop to finish.";
    } catch (err) {
        // Handle errors
        console.error("Microphone access error:", err);
        alert("Failed to access microphone. Please check your browser permissions.");
    }
});

stopBtn.addEventListener("click", () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        recordBtn.disabled = false;
        stopBtn.disabled = true;
        status.textContent = "Recording stopped.";
    }
});

function displayResults(result) {
    // Display the recognized song
    const song = result.recognized_song;
    recognizedSongDiv.innerHTML = `
        <p><strong>${song.title}</strong> by <em>${song.artist}</em></p>
        ${song.album_image ? `<img src="${song.album_image}" alt="Album Art" />` : ""}
    `;

    // Display other songs by the artist
    const otherSongs = result.other_songs;
    otherSongsDiv.innerHTML = otherSongs
        .map((s) => `
            <div class="song-card">
                <img src="${s.album_image || 'https://via.placeholder.com/200'}" alt="Album Art" />
                <p><strong>${s.title}</strong></p>
            </div>
        `)
        .join("");
}
