from dataclasses import dataclass
from proj_whisper.constants.prediction_pipeline import consts as prediction_pipeline
import os
@dataclass
class AUDIO_DATA_INGESTION_config:
    input_dir_name = prediction_pipeline.AUDIO_DIR
    output_dir_name = os.path.join(prediction_pipeline.ARTIFACT_DIR,prediction_pipeline.OUTPUT_AUDIO_DIR)

@dataclass
class TRANSCRIPTIONS_DATA_INGESTION_config:
    input_dir_name = prediction_pipeline.TRANSCRIPTIONS_DIR
    output_dir_name = os.path.join(prediction_pipeline.ARTIFACT_DIR, prediction_pipeline.TRANSCRIPTIONS_OUTPUT_DIR)
