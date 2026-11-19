import os
from flask import Flask, render_template, request, jsonify, send_file
from dotenv import load_dotenv
import numpy as np
from data_manager import load_dataset, save_uploaded_csv, restore_sample
import analytics
import ai_helper
from report_generator import create_pdf_report

load_dotenv()
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

DATA = load_dataset()

def refresh_data():
    global DATA
    DATA = load_dataset()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/dashboard")
def dashboard_api():
    return jsonify(analytics.dashboard_summary(DATA))

@app.route("/api/traffic")
def traffic_api():
    return jsonify(analytics.series_data(DATA, "traffic"))

@app.route("/api/air-quality")
def aqi_api():
    return jsonify(analytics.series_data(DATA, "aqi"))

@app.route("/api/analytics")
def analytics_api():
    return jsonify(analytics.full_analytics(DATA))

@app.route("/api/predictions")
def predictions_api():
    return jsonify(analytics.predictions(DATA))

@app.route("/api/upload-dataset", methods=["POST"])
def upload_dataset():
    if "file" not in request.files:
        return jsonify({"error": "Please choose a CSV file."}), 400
    try:
        save_uploaded_csv(request.files["file"])
        refresh_data()
        return jsonify({"message": "Dataset uploaded successfully.", "dashboard": analytics.dashboard_summary(DATA)})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        return jsonify({"error": "Could not process this file. Check its format and try again."}), 400

@app.route("/api/restore-sample", methods=["POST"])
def restore():
    restore_sample()
    refresh_data()
    return jsonify({"message": "Original sample dataset restored."})

@app.route("/api/ai/analyze", methods=["POST"])
def analyze():
    return jsonify(ai_helper.analyze(DATA))

@app.route("/api/ai/recommendations", methods=["POST"])
def recommendations():
    return jsonify(ai_helper.recommendations(DATA))

@app.route("/api/ai/ask", methods=["POST"])
def ask():
    question = (request.json or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "Enter a question first."}), 400
    return jsonify(ai_helper.ask(DATA, question))

@app.route("/api/ai/explain", methods=["POST"])
def explain():
    topic = (request.json or {}).get("topic", "overall analysis")
    return jsonify(ai_helper.explain(DATA, topic))

@app.route("/api/ai/generate-report", methods=["POST"])
def generate_report():
    try:
        report_path = create_pdf_report(DATA, analytics.full_analytics(DATA), ai_helper.analyze(DATA))
        return send_file(report_path, as_attachment=True, download_name="smart_city_weekly_report.pdf")
    except Exception as exc:
        return jsonify({"error": f"Report generation failed: {exc}"}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
