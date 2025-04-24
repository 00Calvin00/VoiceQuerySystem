from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from app.speech_to_text import transcribe_audio
from werkzeug.utils import secure_filename
from app.text_to_sql import generate_sql
from app.database_executer import execute_sql_query

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Set up uploads folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload_audio", methods=["POST"])
def upload_audio():
    print("📥 Upload route hit")
    if "audio" not in request.files:
        print("⚠️ No audio file found")
        return jsonify({"error": "No audio file"}), 400

    file = request.files["audio"]
    print(f"📂 Received file: {file.filename}")
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    transcript = transcribe_audio(filepath)
    sql_query = generate_sql(transcript)
    print("🧠 SQL from agent:", sql_query)

    # Handle malformed or irrelevant queries
    if "Sorry, I couldn't generate" in sql_query or "ERROR" in sql_query.upper():
        return jsonify({
            "transcript": transcript,
            "sql": sql_query,
            "results": None,
            "error": "❌ Unable to generate a valid SQL query from the input."
        })

    # Handle direct model result (not a SQL query)
    if sql_query.startswith("[EXECUTED_RESULT]"):
        raw_result = sql_query.replace("[EXECUTED_RESULT]", "").strip()
        return jsonify({
            "transcript": transcript,
            "sql": "(Executed directly by the model)",
            "results": [{"Result": raw_result}]
        })

    # Otherwise, run the SQL
    results = execute_sql_query(sql_query)

    return jsonify({
        "transcript": transcript,
        "sql": sql_query,
        "results": results
    })

if __name__ == "__main__":
    app.run(debug=True)
