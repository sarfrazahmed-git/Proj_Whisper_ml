from proj_whisper.exception.exception import CustomException
from proj_whisper.logger.logger import logging
from pyannote.audio import Model,Inference
import dotenv
import sys
import json
import numpy as np
import os
from sklearn.metrics.pairwise import cosine_similarity
from proj_whisper.components.db_connection import DatabaseConnection
cosine_threshold = 0.7

dotenv.load_dotenv(dotenv.find_dotenv())
class LabelCorrector:
    def __init__(self):
        self.load_model()
    def get_conn(self):
        try:
            connection = DatabaseConnection.get_connection()
            if connection is not None:
                logging.info("Database connection established successfully.")
                return connection
            else:
                raise CustomException("Failed to connect to the database.")
        except Exception as e:
            logging.error(f"Error connecting to the database: {e}")
            raise CustomException(e, sys)
    def close_conn(self, connection):
        try:
            if connection.is_connected():
                connection.close()
                logging.info("Database connection closed successfully.")
        except Exception as e:
            logging.error(f"Error closing the database connection: {e}")
            raise CustomException(e, sys)
    def load_model(self):
        try:
            logging.info("Loading label correction model...")
            self.model = Model.from_pretrained("pyannote/embedding", use_auth_token=os.getenv("hugging_face_token"))
            self.inference = Inference(self.model, window="whole")
            logging.info("Model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise CustomException(f"Error loading model: {e}")
    
    def both_vectors_empty(self, cursor,connection,embedding,conv_id):
        logging.info("Both speaker vectors are empty, skipping label correction.")
        query = f"UPDATE conversations SET SPEAKER1_vector = '{json.dumps(embedding.tolist())}' WHERE ID = {conv_id}"
        cursor.execute(query)
        return "Speaker 1"
    
    def one_vector_empty(self, cursor,connection,embedding,conv_id,sim_speaker1, sim_speaker2):
        db_change = False
        if sim_speaker1 > cosine_threshold:
            logging.info("Segment matches Speaker 1")
            label = "Speaker 1"
        elif sim_speaker2 > cosine_threshold:
            logging.info("Segment matches Speaker 2")
            label = "Speaker 2"
        elif sim_speaker1 == -2:
            query = f"UPDATE conversations SET SPEAKER1_vector = '{json.dumps(embedding.tolist())}' WHERE ID = {conv_id}"
            cursor.execute(query)
            db_change = True
            label = "Speaker 1"
        elif sim_speaker2 == -2:
            query = f"UPDATE conversations SET SPEAKER2_vector = '{json.dumps(embedding.tolist())}' WHERE ID = {conv_id}"
            cursor.execute(query)
            db_change = True
            label = "Speaker 2"
        return label, db_change

    def correct_labels(self, conv_id, audio_segments):
        try:
            logging.info("Starting label correction process")
            connection = self.get_conn()
            cursor = connection.cursor(dictionary = True)
            query = f"SELECT * FROM conversations WHERE ID = {conv_id}"
            cursor.execute(query)
            result = cursor.fetchone()
            if result is None:
                raise CustomException(f"no such conversation {conv_id}",sys)
            
            speaker_1 = result['SPEAKER1_vector']
            speaker_2 = result['SPEAKER2_vector']
            if speaker_1 is not None:
                speaker_1 = np.array(json.loads(result['SPEAKER1_vector']))

            if speaker_2 is not None:
                speaker_2 = np.array(json.loads(result['SPEAKER2_vector']))
            new_segments = []


            for segment in audio_segments:
                audio = segment[0]
                label = segment[1]
                logging.info(f"Processing segment with label: {label}")
                embedding = self.inference(audio)
                #print(embedding, "embedding")
                #print(audio, "audio")
                embedding = np.array(embedding.data)
                if(speaker_1 is None or speaker_2 is None):
                    sim_speaker1 = -2
                    sim_speaker2 = -2

                    if(speaker_1 is not None):
                        sim_speaker1 = cosine_similarity(embedding.reshape(1, -1),speaker_1.reshape(1, -1))
                        sim_speaker1 = sim_speaker1[0][0]
                    if(speaker_2 is not None):
                        sim_speaker2 = cosine_similarity(embedding.reshape(1, -1),speaker_2.reshape(1, -1))
                        sim_speaker2 = sim_speaker2[0][0]
                    if (sim_speaker1 == -2 and sim_speaker2 == -2):
                        label = self.both_vectors_empty(cursor,connection,embedding,conv_id)
                        speaker_1 = embedding
                    else:
                        label,db_change = self.one_vector_empty(cursor,connection,embedding,conv_id,sim_speaker1, sim_speaker2)
                        if(db_change):
                            if label == "Speaker 1":
                                speaker_1 = embedding
                            else:
                                speaker_2 = embedding
                else:
                    sim_speaker1 = cosine_similarity(embedding.reshape(1, -1),speaker_1.reshape(1, -1))
                    sim_speaker1 = sim_speaker1[0][0]
                    sim_speaker2 = cosine_similarity(embedding.reshape(1, -1),speaker_2.reshape(1, -1))
                    sim_speaker2 = sim_speaker2[0][0]
                    if sim_speaker1 >= sim_speaker2:
                        logging.info("Segment matches Speaker 1")
                        label = "Speaker 1"
                    elif sim_speaker2 > sim_speaker1:
                        logging.info("Segment matches Speaker 2")
                        label = "Speaker 2"
                seg_time = segment[2]
                new_segments.append((audio, label,seg_time))
            connection.commit()
            return new_segments
        except Exception as e:
            raise CustomException(e,sys)
        finally:
            if cursor:
                cursor.close()
            if connection:
                self.close_conn(connection)
                logging.info("Label correction process completed successfully")
