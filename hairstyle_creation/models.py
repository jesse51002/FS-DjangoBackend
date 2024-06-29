from datetime import datetime, timedelta
import typing
from typing import Literal, Optional
from uuid import uuid4

from pydantic import BaseModel

EVENT_TIMEOUT = timedelta(hours=1)

class Hairstyle(BaseModel):
    hairstyle_id: int
    hairstyle_name: str
    
    color_id: int
    color_name: str
    
class UploadPicture(BaseModel):
    file_location: str
    bbox: tuple[int, int, int, int]

class EmbeddingInferenceResult(BaseModel):
    inference_eventid: str
    hairchange_eventid: str
    
    upload_picture: UploadPicture
    
    embedded_file_location: str
    segmentation_file_location: str
    
    embedding_file_expire_time: datetime
    
    errored: bool
    
class BlendInferenceResult(BaseModel):
    inference_eventid: str
    hairchange_eventid: str
    
    upload_picture: UploadPicture
    hairstyle: Hairstyle
    
    result_img_location: str
    
    errored: bool

class HairstyleChangeEvent(BaseModel):
    eventid: str
    account_identifier: str
    
    uploaded_picture: UploadPicture = None
    hairstyles: list[Hairstyle] = None
    
    embedding_inference_id: str = None
    blend_inference_ids: list[str] = None
    
    start_timestamp: datetime
    
    uploaded_picture_timestamp: datetime = None
    picked_hairstyles_timestamp: datetime = None
    
    finished_timestamp: datetime = None
    
    event_timeout: datetime

        
    def __init__(self, **data: typing.Any) -> None:
        data["start_timestamp"] = datetime.now()
        data["event_timeout"] = datetime.now() + EVENT_TIMEOUT
        super().__init__(**data)


class InferenceEvent(BaseModel):
    inference_eventid: str
    hairchange_eventid: str
    account_identifier: str
    
    type: Literal["Embedding", "Blending"]
    
    start_timestamp: datetime = None
    
    uploaded_picture: UploadPicture = None
    hairstyle: Hairstyle = None
    
    embedding_result: EmbeddingInferenceResult
    blending_result: BlendInferenceResult = None

    queue_timestamp: datetime = None
    finished_timestamp: datetime = None
        
    event_timeout: datetime = None

    def __init__(self, **data: typing.Any) -> None:
        data["start_timestamp"] = datetime.now()
        super().__init__(**data)

database : dict[str, HairstyleChangeEvent] = {}
inference_database : dict[str, InferenceEvent] = {}

def create_eventid() -> str:
    """
    Creates a unique event ID using the current date and time.

    Returns:
        eventid (str): The unique event ID.

    This function generates a unique event identifier using the current date and time,
    and a random UUID. It then returns the event identifier as a string.
    """
    eventid = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
    return eventid