let mediaRecorder;
let audioChunks = [];

// Pull info from UI
const recordButton = document.getElementById("recordButton");
const buttonStatus = document.getElementById("buttonStatus");
const transcript = document.getElementById("transcript");

recordButton.addEventListener("click", async () => {
    console.log("🎯 Button clicked");
  // If already recording, stop it
    if (mediaRecorder && mediaRecorder.state === "recording") {
        console.log("🛑 Stopping recording...");
        mediaRecorder.stop();
        recordButton.textContent = "Start Recording";
        buttonStatus.textContent = "Status: Stopped recording";
        return;
    }

    console.log("🎙️ Starting new recording...");
    // Otherwise, start a new recording
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();
    
    recordButton.textContent = "Stop Recording";
    buttonStatus.textContent = "Status: Recording...";
    console.log("✅ MediaRecorder started");

    audioChunks = [];

    mediaRecorder.ondataavailable = e => {
        console.log("📦 Data available from mic");
        audioChunks.push(e.data);
    };

    mediaRecorder.onstop = async () => {
        console.log("🔁 onstop fired — uploading and transcribing");
        buttonStatus.textContent = "Status: Uploading and transcribing...";

        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append("audio", audioBlob, "recording.wav");

        try {
            const response = await fetch("/upload_audio", {
            method: "POST",
            body: formData
            });

            console.log("📡 Response received");

            const result = await response.json();
            console.log("✅ Transcription result:", result);

            transcript.innerHTML = `Transcript: <strong>${result.transcript}</strong>`;
            document.getElementById("sql").innerHTML = `SQL: <code>${result.sql}</code>`;
            document.getElementById("results").innerHTML = `Results: <strong>${JSON.stringify(result.results)}</strong>`;
            buttonStatus.textContent = "Status: Transcription complete";
        } catch (err) {
            console.error("❌ Error during transcription:", error);
            buttonStatus.textContent = "Status: Error during transcription";
            console.error("Transcription failed:", err);
        }
    };
});
