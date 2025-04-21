# VoiceQuerySystem
This is a project I made for my human-centered data management class that converts speech to SQL queries and outputs them in a simple UI.

# REMINDERS:
 -  Anytime you reopen your terminal, you’ll need to re-activate the environment before working on the project.
 Use this command: 
 source .venv/bin/activate
  - To run website use: python -m app.main

## Debugging and Model Selection Journey
### Agent Logs

Step 1: ❌ Tried `SELECT MAX tip FROM receipts` → SQL syntax error  
Step 2: ❌ Tried again with `MAX tip`, still failed  
Step 3: ❌ Used `max TIP`, wrong again  
Step 4: ✅ Finally got `ORDER BY tip DESC LIMIT 1` — perfect query!

This showed how the LLM could *self-correct over multiple steps*, which made it ideal for my project.

Initially, I received errors such as:

- "Model requires Pro subscription"
- "Model is too large to load"
- "Token not authorized"

To fix this, I upgraded to Hugging Face Pro and created a new token with the right permissions (`Make calls to Inference Providers`). I also passed the token explicitly into the `InferenceClientModel()` constructor.

At first, the agent hallucinated fake servers and didn’t realize it had access to real database schema. I solved this by injecting the full schema directly into the prompt:

You are an AI assistant working with an SQLite database that contains the following table: ...

This guided the model to write better SQL queries.

# References:
- Yuanfeng Song, Raymond Chi-Wing Wong, Xuefang Zhao, Di Jiang. “VoiceQuerySystem: A Voice-driven Database Querying System Using Natural Language Questions.” SIGMOD '22. https://doi.org/10.1145/3514221.3520158
- OpenAI Whisper Speech-to-Text Model: https://github.com/openai/whisper
- Hugging Face Text2SQL Space by gauravshah: https://huggingface.co/spaces/gauravshah/text2sql
- Flask Web Framework: https://flask.palletsprojects.com
- SQLite Docs: https://www.sqlite.org/docs.html
- MediaRecorder API: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder
- Flask Official Docs: https://flask.palletsprojects.com/en/2.3.x/
- Python venv Docs: https://docs.python.org/3/library/venv.html
- Flask-CORS Docs: https://flask-cors.readthedocs.io/en/latest/
- requests Docs: https://requests.readthedocs.io/en/latest/
- Flask Static Files: https://flask.palletsprojects.com/en/2.3.x/tutorial/static/
- FormData Web API: https://developer.mozilla.org/en-US/docs/Web/API/FormData
- Flask File Uploads: https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/
- Flask render_template: https://flask.palletsprojects.com/en/2.3.x/quickstart/#rendering-templates
- JavaScript MediaRecorder: https://developer.mozilla.org/en-US/docs/Web/API/MediaRecorder
- FormData Web API: https://developer.mozilla.org/en-US/docs/Web/API/FormData
- Whisper Speech-to-Text: https://github.com/openai/whisper
- FormData.append() docs: https://developer.mozilla.org/en-US/docs/Web/API/FormData/append
- JS error handling with try/catch: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/try...catch
- Best practices for status messages in UI: Nielsen Norman Group
- Hugging Face smolagents: https://huggingface.co/docs/smolagents/en/examples/text_to_sql
- Python SQLAlchemy docs: https://docs.sqlalchemy.org/
- Hugging Face Inference API: https://huggingface.co/docs/api-inference/index
- Hugging Face token setup: https://huggingface.co/settings/tokens