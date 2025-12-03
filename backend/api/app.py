import os
import uuid
import traceback
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename
from database import get_session, User, Upload
from explainer_service import process_pdf

app = Flask(__name__)

CORS(app, supports_credentials=True, origins="*")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "shared", "uploads")
OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), "..", "shared", "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route("/", methods=["GET"])
@cross_origin()
def home():
    return jsonify({"status": "backend is live"})


@app.route("/upload", methods=["POST", "OPTIONS"])
@cross_origin()
def upload_file():
    if request.method == "OPTIONS":
        return _cors_response()

    try:
        file = request.files.get("file")
        summary_level = request.form.get("summary_level")
        language = request.form.get("language")

        if not file:
            return jsonify({"error": "No file uploaded"}), 400

        uid = str(uuid.uuid4())
        filename = secure_filename(f"{uid}.pdf")
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        session = get_session()
        upload = Upload(
            uid=uid,
            original_filename=file.filename,
            summary_level=summary_level,
            language=language,
            status="processing"
        )
        session.add(upload)
        session.commit()

        # Process PDF
        process_pdf(path, uid, summary_level, language)

        upload.status = "completed"
        session.commit()

        return jsonify({"uid": uid})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/status/<uid>", methods=["GET"])
@cross_origin()
def check_status(uid):
    try:
        session = get_session()
        upload = session.query(Upload).filter(Upload.uid == uid).first()

        if not upload:
            return jsonify({"error": "UID not found"}), 404

        return jsonify({"status": upload.status})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/download/<uid>", methods=["GET"])
@cross_origin()
def download(uid):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, f"{uid}.pdf")

        if not os.path.exists(file_path):
            return jsonify({"error": "File not ready"}), 404

        return send_from_directory(OUTPUT_FOLDER, f"{uid}.pdf", as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _cors_response():
    response = jsonify({"status": "OK"})
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type")
    response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
