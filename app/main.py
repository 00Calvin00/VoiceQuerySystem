from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from app.speech_to_text import transcribe_audio
from werkzeug.utils import secure_filename
from app.text_to_sql import generate_sql

# This file acts as the controller that responds to all browser requests. Acts as the first responder to user actions and url changes.
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app) #CORS is Cross-Origin Resource Sharing, helps the front and back end communicate

# Check if there is an upload folder and if not then create one
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# Handle record button being pressed
@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    print("📥 Upload route hit")
    # Check if audio file got sent properly
    if "audio" not in request.files:
        print("⚠️ No audio found in request.files")
        return jsonify({"error": "No audio file"}), 400

    # Create local file from sent over audio file
    file = request.files["audio"]
    print(f"📂 Received file: {file.filename}")
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # Create and return audio transcript and sql query to UI
    transcript = transcribe_audio(filepath)
    sql_query = generate_sql(transcript)
    print("🧠 SQL from agent:", sql_query)
    
    results = execute_sql_query(sql_query)
    
    return jsonify({
        "transcript": transcript,
        "sql": sql_query,
        "results": results
    })

if __name__ == "__main__":
    app.run(debug=True)
