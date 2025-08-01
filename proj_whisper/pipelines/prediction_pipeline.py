from proj_whisper.components.preproccessing import Preprocessing
from proj_whisper.components.transcript_generator import TranscriptGenerator
from proj_whisper.components.label_corrector import LabelCorrector
from proj_whisper.entity.conifg_entity.generator_configs import PREDICTION_PIPELINE_CONFIG, PROCESSING_CONFIG
from proj_whisper.components.Transcript_combiner import TranscriptCombiner
from io import BytesIO
import torchaudio
import time
import pydub
from proj_whisper.components.db_connection import DatabaseConnection
from proj_whisper.utils.main_utils import convert_webm_bytes_to_wav
class PredictionPipeline:
    def __init__(self):
        prediction_config = PREDICTION_PIPELINE_CONFIG()
        self.processing_config = PROCESSING_CONFIG()
        self.prediction_config = prediction_config
        self.preprocessor = Preprocessing(self.processing_config)
        self.transcript_generator = TranscriptGenerator(self.prediction_config)
        self.label_corrector = LabelCorrector()

    def run(self, audio, conv_id, global_start):
        print("Starting prediction pipeline...")
        try:
            try:
                while True:
                    print("global_start:", global_start)
                    if(global_start == 0):
                        break
                    connection = DatabaseConnection.get_connection()
                    cursor = connection.cursor()
                    query = "SELECT * FROM segment WHERE conv_id = (%s) AND end_global > %s"
                    cursor.execute(query, (conv_id, global_start-500))
                    result = cursor.fetchall()
                    print(result, global_start)
                    if len(result) == 0:
                        connection.close()
                        cursor.close()
                        print("No segments found, waiting for 5 seconds...")
                        time.sleep(5)
                    else:
                        break
            except Exception as e:
                raise e
            finally:
                if 'connection' in locals() and connection.is_connected():
                    connection.close()
                    print("Database connection closed.")
                if 'cursor' in locals():
                    cursor.close()
                    print("Cursor closed.")

            waveform, sample_rate = torchaudio.load(audio)
            audio_data = {
                "waveform": waveform,
                "sample_rate": sample_rate
            }
            segments = self.preprocessor.diarise_audio_proper(audio_data)
            new_segments = []
            for (segment, label, time_range) in segments:
                new_start = time_range[0] + int(global_start)
                new_end = time_range[1] + int(global_start)
                new_segments.append((segment, label, (new_start, new_end)))
            corrected_segments = self.label_corrector.correct_labels(conv_id, new_segments)
            transcripts = self.transcript_generator.generate_transcript(corrected_segments, conv_id,global_start)
            transcript_combiner = TranscriptCombiner(conv_id)
            combined_transcript = transcript_combiner.combine_transcripts()
            return corrected_segments, combined_transcript
        except Exception as e:
            raise e
