from pydantic import BaseModel
from typing import List, Optional

class SubtitleSegment(BaseModel):
    start: float
    end: float
    text: str

class SubtitleResponse(BaseModel):
    segments: List[SubtitleSegment]
    language: str

class TranslationRequest(BaseModel):
    file_id: str
    target_language: str
    style_prompt: Optional[str] = None

class TranscriptionResult(BaseModel):
    text: str
    segments: List[SubtitleSegment]
    language: str

class EmbedSubtitlesRequest(BaseModel):
    file_id: str
    language: str = "original"