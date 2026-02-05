from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

DATA_FILE = "data.csv"

if os.path.exists(DATA_FILE):
    leaderboard = pd.read_csv(DATA_FILE)
else:
    leaderboard = pd.DataFrame(columns=["Name", "Action", "Points", "Photo"])

@app.route("/submit", methods=["POST"])
def submit():
    data = request.form
    name = data.get("name")
    action = data.get("action")
    points = int(data.get("points", 0))
    photo = request.files["photo"].read()

    new_entry = pd.DataFrame([[name, action, points, photo]],
                             columns=["Name", "Action", "Points", "Photo"])
    df = pd.concat([leaderboard, new_entry], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

    return jsonify({"status": "success"})

@app.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        return df.to_json(orient="records")
    return jsonify([])

if __name__ == "__main__":
    app.run(port=5000)
