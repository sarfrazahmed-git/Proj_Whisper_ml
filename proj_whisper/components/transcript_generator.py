from proj_whisper.entity.conifg_entity.generator_configs import PREDICTION_PIPELINE_CONFIG
from proj_whisper.exception.exception import CustomException
from proj_whisper.logger.logger import logging
from openai import OpenAI
import whisper
import sys
import os
from natsort import natsorted
import dotenv
from proj_whisper.utils.main_utils import tensor_to_wav_bytes
from proj_whisper.components.db_connection import DatabaseConnection
dotenv.load_dotenv(dotenv.find_dotenv())
open_ai_api_key = os.getenv("open_ai_api_key")
class TranscriptGenerator:
    def __init__(self, config: PREDICTION_PIPELINE_CONFIG):
        self.config = config
        self.load_model()

    def load_model(self):
        try:
            self.client = OpenAI(api_key=open_ai_api_key)
            logging.info("openai client loaded successfully")
        except Exception as e:
            raise CustomException(e, sys)
    def generate_transcript(self, audio_segments,conv_id,global_start):
        try:
            logging.info("Starting transcription process")
            transcript = ""
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            logging.info("Database connection established successfully")
            for segment in audio_segments:
                file_input = tensor_to_wav_bytes(segment[0]["waveform"], segment[0]['sample_rate'])
                print("file_input:", file_input)

                result = self.client.audio.transcriptions.create(
                    file=("audio.wav",file_input),
                    model="whisper-1",
                    response_format="text"
                )
                print("result:", result)
                transcript += segment[1] + ":" + " " + result + "\n"
                query = f"INSERT INTO segment (conv_id,transcriptions,start_global,end_global) VALUES (%s, %s,%s,%s)"
                print(segment)
                cursor.execute(query, (conv_id, transcript, segment[2][0], segment[2][1]))

            dummy_script = ""
            query = f"INSERT INTO segment (conv_id,transcriptions,start_global,end_global) VALUES (%s, %s,%s,%s)"
            cursor.execute(query, (conv_id, dummy_script, global_start+10000, global_start +10000))
            connection.commit()
            logging.info("Transcription process completed successfully")
            return transcript
        except Exception as e:
            raise CustomException(e,sys)
        finally:
            if connection and connection.is_connected():
                connection.close()
                logging.info("Database connection closed successfully")
            if cursor:
                cursor.close()
                logging.info("Cursor closed successfully")