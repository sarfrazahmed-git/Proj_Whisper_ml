from dataclasses import dataclass

@dataclass
class IngestionArtifact:
    audio_output_dir: str
    transcriptions_output_dir: str