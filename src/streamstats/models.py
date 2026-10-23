from datetime import datetime
from typing import Literal

from pydantic import BaseModel, field_validator


class Event(BaseModel):
    timestamp: datetime
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    source: str
    message: str

    @field_validator("source")
    @classmethod
    def validate_source(cls, value: str):
        if not value.strip():
            raise ValueError("Source cannot be empty")

        return value
