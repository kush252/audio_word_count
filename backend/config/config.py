import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class AudioConfig:
    device_index: Optional[int] = None
    sample_rate: int = 16000
    chunk_duration: float = 0.5

@dataclass
class VADConfig:
    threshold: float = 0.5

@dataclass
class TranscriptionConfig:
    model: str = "distil-large-v3"
    language: Optional[str] = "en"

@dataclass
class OutputConfig:
    refresh_rate: float = 1.0
    save_path: str = "counts.json"

@dataclass
class AppConfig:
    keywords: List[str] = field(default_factory=list)
    phrases: List[str] = field(default_factory=list)
    audio: AudioConfig = field(default_factory=AudioConfig)
    vad: VADConfig = field(default_factory=VADConfig)
    transcription: TranscriptionConfig = field(default_factory=TranscriptionConfig)
    output: OutputConfig = field(default_factory=OutputConfig)

def load_config(config_path: str = "config/config.yaml") -> AppConfig:
    """Loads configuration from a YAML file and returns an AppConfig dataclass."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return AppConfig(
        keywords=data.get("keywords", []),
        phrases=data.get("phrases", []),
        audio=AudioConfig(**data.get("audio", {})),
        vad=VADConfig(**data.get("vad", {})),
        transcription=TranscriptionConfig(**data.get("transcription", {})),
        output=OutputConfig(**data.get("output", {}))
    )
