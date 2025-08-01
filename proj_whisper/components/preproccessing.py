import dotenv
import os
import numpy as np
from proj_whisper.entity.conifg_entity.generator_configs import PREDICTION_PIPELINE_CONFIG, PROCESSING_CONFIG
from proj_whisper.logger.logger import logging
from proj_whisper.exception.exception import CustomException
from pyannote.audio import Pipeline, Model,Inference
import sys
from pyannote.audio.pipelines.utils.hook import ProgressHook
import torchaudio
from pyannote.audio.pipelines.clustering import AgglomerativeClustering
dotenv.load_dotenv(dotenv.find_dotenv())
print("Hugging Face Token:", os.getenv("hugging_face_token"))
MIN_DURATION  = 500
class Preprocessing:
    def __init__(self, config: PROCESSING_CONFIG):
        self.config = config

    def load_model(self):
        try:
            logging.info("Loading diarisation model...")
            self.model = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=os.getenv("hugging_face_token"))
            logging.info("Model loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise CustomException(f"Error loading model: {e}")
    
    def slice_waveform_ms(self,waveform, sample_rate, start_ms, end_ms):
        start_sample = int((start_ms / 1000.0) * sample_rate)
        end_sample = int((end_ms / 1000.0) * sample_rate)
        return {"waveform": waveform[:, start_sample:end_sample], "sample_rate": sample_rate}

    def segment_audio(self):
        self.segments = []
        try:
            logging.info("segmenting audio")
            for segment, _, lb in self.diarisation.itertracks(yield_label=True):
                start = int(segment.start*1000)
                end = int(segment.end*1000)
                if end - start > MIN_DURATION:
                    logging.info(f"Skipping segment from {start} to {end} ms, duration is less than {MIN_DURATION} ms")
                    label = lb
                    logging.info(f"Segment: {label}, Start: {start}, End: {end}")
                    chunk = self.slice_waveform_ms(self.audio['waveform'], self.audio['sample_rate'], start, end)
                    self.segments.append((chunk, label,(start, end)))
                else:
                    logging.info(f"Skipping segment from {start} to {end} ms, duration is less than {MIN_DURATION} ms")
            logging.info("Audio segmentation completed successfully.")
            
        except Exception as e:
            raise CustomException(e,sys)
        
    def diarise_audio_proper(self, audio):
        self.audio = audio
        self.load_model()
        try:
            logging.info("Starting diarization process")
            with ProgressHook() as hook:
                self.diarisation = self.model(self.audio,hook=hook)
            logging.info("Diarization completed successfully")
            self.segment_audio()
            logging.info("Audio segments created successfully")
            return self.segments
        except Exception as e:
            raise CustomException(e,sys)
