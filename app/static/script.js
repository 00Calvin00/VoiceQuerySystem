let mediaRecorder;
let audioChunks = [];

// Pull info from UI
const recordButton = document.getElementById("recordButton");
const buttonStatus = document.getElementById("buttonStatus");
const transcript = document.getElementById("transcript");
const errorBox = document.getElementById("error"); // <- New
const sqlOutput = document.getElementById("sql");
const resultsBox = document.getElementById("results");

recordButton.addEventListener("click", async () => {
    console.log("🎯 Button clicked");
    if (mediaRecorder && mediaRecorder.state === "recording") {
        console.log("🛑 Stopping recording...");
        mediaRecorder.stop();
        recordButton.textContent = "Start Recording";
        buttonStatus.textContent = "Status: Stopped recording";
        return;
    }

    console.log("🎙️ Starting new recording...");
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
            sqlOutput.innerHTML = `SQL: <code>${result.sql}</code>`;

            if (
                result.error || 
                result.results === null || 
                result.sql.toLowerCase().startsWith("sorry, i couldn't generate")
            ) {
                errorBox.style.display = "block";
                errorBox.textContent = result.error || "❌ Unable to process your query.";
                resultsBox.innerHTML = "<em>No results to show.</em>";
            } else {
                errorBox.style.display = "none";
                resultsBox.innerHTML = formatResultsTable(result.results);
            }

            console.log("🧾 Raw Results:", result.results);
            buttonStatus.textContent = "Status: Transcription complete";

        } catch (err) {
            console.error("❌ Error during transcription:", err);
            buttonStatus.textContent = "Status: Error during transcription";
            errorBox.style.display = "block";
            errorBox.textContent = "An unexpected error occurred during transcription.";
        }
    };
});

function formatResultsTable(data) {
    if (!data || data.length === 0) return "<p>No results.</p>";

    const headers = Object.keys(data[0]);
    let table = "<table><tr>";
    headers.forEach(h => table += `<th>${h}</th>`);
    table += "</tr>";

    data.forEach(row => {
        table += "<tr>";
        headers.forEach(h => table += `<td>${row[h]}</td>`);
        table += "</tr>";
    });

    table += "</table>";
    return table;
}
