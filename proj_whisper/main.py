import sys
from flask import Flask, render_template, request, jsonify, make_response
from proj_whisper.pipelines.prediction_pipeline import PredictionPipeline
from proj_whisper.exception.exception import CustomException
import os
import shutil
import dotenv
import jwt
import random
from proj_whisper.components.db_connection import DatabaseConnection
dotenv.load_dotenv(dotenv.find_dotenv())
from proj_whisper.logger.logger import logging
from io import BytesIO
import pydub

app = Flask(__name__)
secret_key = os.getenv("secret_key")
@app.route('/')
def index():
    return render_template('index.html')
@app.route("/start", methods=['GET'])
def start_session():
    try:
        unique_id = random.randint(1, 10000000)
        token = jwt.encode({'session_id': unique_id}, secret_key, algorithm='HS256')
        response = make_response("ok",200)
        response.set_cookie('session_id', token, httponly=True, secure=True, samesite=None)
        connection = DatabaseConnection.get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO conversations (ID) VALUES (%s)", (unique_id,))
        connection.commit()
        return response
    except Exception as e:
        logging.error(f"Error starting session: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Database connection closed.")
        if 'cursor' in locals():
            cursor.close()
            print("Cursor closed.")
@app.route('/upload', methods=['POST'])
def upload_file():
    print("entered")
    if 'session_id' not in request.cookies:
        return jsonify({'error': 'Session ID not found in cookies'}), 400
    session_id = request.cookies.get('session_id')
    try:
        decoded = jwt.decode(session_id, secret_key, algorithms=['HS256'])
    except jwt.ExpiredSignatureError as e:
        logging.error(f"Session has expired: {e}")
        return jsonify({'error': 'Session has expired'}), 401
    except jwt.InvalidTokenError as e:
        logging.error(f"Invalid session token: {e}")
        return jsonify({'error': 'Invalid session token'}), 401
    

    print(request.form)
    print(request)
    if 'audio' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    if "global_start" not in request.form:
        return jsonify({'error': 'Global start time not provided'}), 400
    
    file_name = request.files['audio'].filename.split('.')[0] + request.form.get("global_start") +"."+ request.files['audio'].filename.split('.')[-1]
    conv_id = decoded.get('session_id')
    file = request.files['audio']
    print("file:", type(file))
    global_start = int(request.form.get("global_start"))
    print("conv_id:", conv_id, "global_start:", global_start)
    prediction_pipe = PredictionPipeline(
    )
    print("MIME type:", file.mimetype)
    file = file.read()
    #file = repair_blob(file)
    os.makedirs("temp", exist_ok=True)
    with open(f"temp/{file_name}", "wb") as f:
        f.write(file)
    print("File saved successfully.")
    webm_io = BytesIO(file)
    webm_io.seek(0)
    print("Converting webm to wav")
    audio = pydub.AudioSegment.from_file(webm_io, format="webm")
    wav_io = BytesIO()
    audio.export(wav_io, format="wav")
    wav_io.seek(0)
    file = wav_io
    print("file:", type(file))
    segments,transcripts = prediction_pipe.run(file, conv_id,global_start)
    print("transcripts:", transcripts)
    try:
        connection = DatabaseConnection.get_connection()
        cursor = connection.cursor()
        logging.info("Audio segments inserted successfully.")
        return jsonify({
            'transcript': transcripts,
            'update': global_start
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Database connection closed.")
        if 'cursor' in locals():
            cursor.close()
            print("Cursor closed.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)