from dataclasses import dataclass
from proj_whisper.constants.prediction_pipeline import consts as prediction_pipeline
import os
@dataclass
class PREDICTION_PIPELINE_CONFIG:
    results_dir = prediction_pipeline.RESULTS_DIR
    results_transcription_dir = prediction_pipeline.RESULTS_TRANSCRIPTION_DIR
    results_transcription_path = os.path.join(results_dir, results_transcription_dir)

class PROCESSING_CONFIG:
    diarised_dir = prediction_pipeline.DIARISED_DIR
    diarised_path = os.path.join(prediction_pipeline.ARTIFACT_DIR, diarised_dir)