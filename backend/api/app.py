import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import threading
import asyncio
from backend.explainer.explainer_service import main_loop as explainer_main_loop

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from email_validator import validate_email, EmailNotValidError

# ---- INIT FLASK APP (only once!) ----
app = Flask(__name__)

# ************* CORS FIX HERE *************
CORS(app, origins=[
    "http://localhost:3000",
    "https://slidesummarizer-frontend.onrender.com",
    "*"
])
# ******************************************

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
# --------------------------------------

BASE_DIR = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(BASE_DIR))

from database import get_session, User, Upload

UPLOADS_DIR = os.environ.get("UPLOADS_DIR", os.path.join(BASE_DIR, "shared", "uploads"))
OUTPUTS_DIR = os.environ.get("OUTPUTS_DIR", os.path.join(BASE_DIR, "shared", "outputs"))
LOGS_DIR = os.environ.get("LOGS_DIR", os.path.join(BASE_DIR, "shared", "logs", "api2"))

for directory in [UPLOADS_DIR, OUTPUTS_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)


def setup_logger():
    handler = TimedRotatingFileHandler(
        os.path.join(LOGS_DIR, 'api2.log'),
        when='midnight',
        backupCount=5
    )
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.addHandler(handler)
    werkzeug_logger.setLevel(logging.INFO)


setup_logger()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == "pptx"


def validate_summary_level(level):
    return level in ["beginner", "comprehensive", "executive"]


def validate_language(lang):
    return lang in ["en", "he", "ru", "es"]


# ---------- ROUTES ----------

@app.route('/upload', methods=['POST', 'OPTIONS'])
@cross_origin()
def upload_file():
    if request.method == "OPTIONS":
        return jsonify({"status": "OK"}), 200

    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    email = request.form.get('email', '').strip()
    summary_level = request.form.get('summary_level', 'comprehensive').strip().lower()
    language = request.form.get('language', 'en').strip().lower()

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    if not validate_summary_level(summary_level):
        return jsonify({"error": "Invalid summary level"}), 400

    if not validate_language(language):
        return jsonify({"error": "Invalid language"}), 400

    if email:
        try:
            email = validate_email(email, check_deliverability=False).email
        except EmailNotValidError as e:
            return jsonify({"error": str(e)}), 400

    session = get_session()
    try:
        user_id = None

        if email:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                user = User(email=email)
                session.add(user)
                session.flush()
            user_id = user.id

        upload = Upload(filename=file.filename, user_id=user_id, summary_level=summary_level, language=language)
        session.add(upload)
        session.commit()

        file_path = os.path.join(UPLOADS_DIR, f"{upload.uid}.pptx")
        file.save(file_path)

        return jsonify({
            "uid": upload.uid,
            "summary_level": summary_level,
            "language": language
        }), 200

    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Internal error: {str(e)}"}), 500
    finally:
        session.close()


@app.route('/status/<uid>', methods=['GET'])
@cross_origin()
def check_status_by_uid(uid):
    session = get_session()
    try:
        upload = session.query(Upload).filter(Upload.uid == uid).first()
        if not upload:
            return jsonify({"status": "not found"}), 404

        explanation = None
        if upload.is_done and os.path.exists(upload.output_path):
            with open(upload.output_path, 'r', encoding='utf-8') as f:
                explanation = json.load(f)

        return jsonify({
            "status": upload.status,
            "uid": upload.uid,
            "filename": upload.filename,
            "summary_level": upload.summary_level,
            "language": upload.language,
            "upload_time": upload.upload_time.isoformat() if upload.upload_time else None,
            "finish_time": upload.finish_time.isoformat() if upload.finish_time else None,
            "explanation": explanation
        })

    finally:
        session.close()


def start_explainer_background():
    asyncio.run(explainer_main_loop())

if __name__ == '__main__':
    # Start explainer in background
    t = threading.Thread(target=start_explainer_background, daemon=True)
    t.start()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

