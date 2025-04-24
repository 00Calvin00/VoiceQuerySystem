# 🎙️ VoiceQuerySystem

A voice-powered natural language interface for querying SQL databases.
Created for my Human-Centered Data Management class.

# 🔍 What It Does

VoiceQuerySystem lets users ask natural language questions out loud (like:

“Which artist sold the most tracks?”)
...and instantly see the corresponding SQL query and the results from the Chinook SQLite database.
It’s designed for beginners who want to explore data without needing to know SQL.

# 🚀 How to Run Locally

 1. Activate your virtual environment
source .venv/bin/activate

 2. Launch the web app
python -m app.main
Then visit http://localhost:5000 in your browser.

# 🛠️ How It Works

🎤 Records user speech via the MediaRecorder API
🗣️ Converts audio to text using Whisper API (via Lemonfox)
🧠 Translates natural language into SQL using Hugging Face + smolagents + LLaMA 3
🧾 Runs SQL on a local SQLite database
📊 Displays results and raw SQL in a simple, teachable UI
🧪 Debugging & Development Notes

# 🤖 Agent Self-Correction
Step 1: ❌ Tried SELECT MAX tip FROM receipts → SQL syntax error  
Step 2: ❌ Tried again with MAX tip → still failed  
Step 3: ❌ Used max TIP → also failed  
Step 4: ✅ Finally got ORDER BY tip DESC LIMIT 1 — perfect query!
The model learned from its own mistakes — a huge reason I chose to use smolagents.

# 🧩 Token Setup & Prompt Engineering
I initially hit issues like:

"Model requires Pro subscription"
"Token not authorized"
"Too large to load"
To fix this:

I upgraded to Hugging Face Pro
Generated a token with the correct Inference Provider scopes
Explicitly passed the token into InferenceClientModel()
To stop the model from hallucinating irrelevant databases, I injected a detailed schema into the prompt:

“You are working with the Chinook SQLite database. Here are the tables and relationships...”
This drastically improved accuracy.

# 📚 References & Tools

 # Core Research
- VoiceQuerySystem Paper (SIGMOD '22): https://doi.org/10.1145/3514221.3520158
 # APIs & Frameworks
- OpenAI Whisper: https://github.com/openai/whisper
- Hugging Face smolagents (Text-to-SQL): https://huggingface.co/docs/smolagents/en/examples/text_to_sql
- Flask Web Framework: https://flask.palletsprojects.com
- SQLite Docs: https://www.sqlite.org/docs.html
- MediaRecorder API: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder
 # Developer Docs
- Flask File Uploads: https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/
- Flask CORS Setup: https://flask-cors.readthedocs.io/en/latest/
- Python venv Docs: https://docs.python.org/3/library/venv.html
- requests Python Library: https://requests.readthedocs.io/en/latest/
- SQLAlchemy Docs: https://docs.sqlalchemy.org/en/20/
- Hugging Face Inference API: https://huggingface.co/docs/api-inference/index
- Hugging Face Token Setup: https://huggingface.co/settings/tokens
- FormData Web API: https://developer.mozilla.org/en-US/docs/Web/API/FormData
- JavaScript FormData.append(): https://developer.mozilla.org/en-US/docs/Web/API/FormData/append
- JS try/catch (error handling): https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/try...catch
- Flask render_template: https://flask.palletsprojects.com/en/2.3.x/quickstart/#rendering-templates

# 🙌 Thanks

To Professor Professor Fariha and everyone in the Human-Centered Data Management class.
This was my favorite project to build.

