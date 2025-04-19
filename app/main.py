from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # enable cross-origin requests for local dev

@app.route("/")
def index():
    return render_template("index.html")  # loads your UI

@app.route("/ping")
def ping():
    return jsonify({"status": "Flask is working!"})

if __name__ == "__main__":
    app.run(debug=True)
