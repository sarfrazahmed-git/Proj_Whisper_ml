import sys
from proj_whisper.entity.conifg_entity.ingestion_configs import AUDIO_DATA_INGESTION_config, TRANSCRIPTIONS_DATA_INGESTION_config
from proj_whisper.exception.exception import CustomException
from proj_whisper.logger.logger import logging
from proj_whisper.entity.artifact_entity.return_artifacts import IngestionArtifact
from proj_whisper.utils.main_utils import copy_dir_content
import sys
import os
from proj_whisper.components.preproccessing import Preprocessing
from proj_whisper.entity.conifg_entity.generator_configs import PROCESSING_CONFIG
from proj_whisper.components.transcript_generator import TranscriptGenerator
from proj_whisper.entity.conifg_entity.generator_configs import PREDICTION_PIPELINE_CONFIG

class DataIngestion:
    def __init__(self, audio_config: AUDIO_DATA_INGESTION_config, transcriptions_config: TRANSCRIPTIONS_DATA_INGESTION_config):
        self.audio_config = audio_config
        self.transcriptions_config = transcriptions_config
    def initiate_data_ingestion(self):
        try:
            logging.info("Data Ingestion started")
            os.makedirs(self.audio_config.output_dir_name, exist_ok=True)
            logging.info(f"Output directory created at: {self.audio_config.output_dir_name}")
            copy_dir_content(self.audio_config.input_dir_name, self.audio_config.output_dir_name)

            os.makedirs(self.transcriptions_config.output_dir_name, exist_ok=True)
            logging.info(f"Output directory created at: {self.transcriptions_config.output_dir_name}")
            copy_dir_content(self.transcriptions_config.input_dir_name, self.transcriptions_config.output_dir_name)
            logging.info("Data Ingestion completed successfully")
            res = IngestionArtifact(
                audio_output_dir=self.audio_config.output_dir_name,
                transcriptions_output_dir=self.transcriptions_config.output_dir_name
            )
            return res
        except Exception as e:
            raise CustomException(str(e), sys) from e
        
if __name__ == "__main__":
    # audio_config = AUDIO_DATA_INGESTION_config()
    # transcriptions_config = TRANSCRIPTIONS_DATA_INGESTION_config()
    # data_ingestion = DataIngestion(audio_config, transcriptions_config)
    # artifact = data_ingestion.initiate_data_ingestion()
    # logging.info("Data ingestion process completed.")
    # print(artifact)

    # Preprocessing_config = PROCESSING_CONFIG()
    # preprocessing = Preprocessing(Preprocessing_config)
    # audio_file_path = artifact.audio_output_dir
    # os.listdir(audio_file_path)
    #audio_file_path = os.path.join(audio_file_path, os.listdir(audio_file_path)[0])
    try:
        #time_stamps = preprocessing.diarise_audio(audio_file_path)
        gen_config = PREDICTION_PIPELINE_CONFIG()
        transcript_generator = TranscriptGenerator(gen_config)
        result = transcript_generator.generate_transcript("output/audios", [])

    except CustomException as e:
        logging.error(f"An error occurred during preprocessing: {e}")