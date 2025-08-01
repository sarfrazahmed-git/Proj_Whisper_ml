from proj_whisper.exception.exception import CustomException
from proj_whisper.logger.logger import logging
from proj_whisper.components.db_connection import DatabaseConnection
import os
import dotenv
dotenv.load_dotenv(dotenv.find_dotenv())
import sys
import google.generativeai as genai

API_KEY = os.getenv("gemini_api_key")
print("Gemini API Key:", API_KEY)
genai.configure(api_key=API_KEY)
class TranscriptCombiner:
    def __init__(self, conv_id):
        self.conv_id = conv_id
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        logging.info("Database connection established successfully")
    def remove_overlap(self, overlap_segments):
        try:
            if not overlap_segments:
                return ""
            prompt = "Below I have provide you with a transcript that have some overlapping segments. Please remove the overlapping segments and return the cleaned transcript. return only the transcript and nothing more. donot remove the speaker headings, keep them\n\n"
            prompt += "Transcript:\n" + overlap_segments + "\n\n"
            response = self.model.generate_content(
                prompt
            )
            cleaned_transcript = response.text.strip()
            logging.info("Overlapping segments removed successfully.")
            return cleaned_transcript
        except Exception as e:
            raise CustomException(e, sys)


    def combine_transcripts(self):
        try:
            connection = DatabaseConnection.get_connection()
            cursor = connection.cursor()
            query = "SELECT * FROM segment WHERE conv_id = %s ORDER BY start_global"
            cursor.execute(query, (self.conv_id,))
            segments = cursor.fetchall()
            if not segments:
                logging.info("No segments found for the given conversation ID.")
                return ""
            combined_transcript = ""
            for segment in segments:
                if segment[1]:
                    combined_transcript += f"{segment[1]} " + "\n"
            logging.info("Transcripts combined successfully.")
            combined_transcript = self.remove_overlap(combined_transcript)
            return combined_transcript.strip()
        except Exception as e:
            raise CustomException(e, sys)
        finally:
            if connection and connection.is_connected():
                connection.close()
                logging.info("Database connection closed successfully.")
            if cursor:
                cursor.close()
                logging.info("Cursor closed successfully.")