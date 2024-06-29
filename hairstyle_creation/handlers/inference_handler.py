from datetime import datetime
import typing
from uuid import uuid4

from pydantic import BaseModel

from hairstyle_creation.errors import AlreadyExists
from hairstyle_creation.models import (
    InferenceEvent,
    EmbeddingInferenceResult,
    BlendInferenceResult,
    create_eventid,
    database,
    inference_database,
)
from hairstyle_creation.handlers.client_event_handler import assert_account_has_event
from hairstyle_creation.handlers.aws_queue_handler import add_to_embedding_queue, add_to_blending_queue


def start_embedding_inference(account_identifier: str, eventid: str) -> Exception | None:
    """
    Starts the embedding inference process for a given account and event.

    Args:
        account_identifier (str): The identifier of the account.
        eventid (str): The identifier of the event.

    Returns:
        None | AlreadyExists: If the inference process has already started for the event,
        returns a AlreadyExists. Otherwise, returns None.

    Raises:
        None

    Adds all the hairstyles to the embedding queue for the given event.
    """
    try:
        assert_account_has_event(account_identifier, eventid)
    except Exception as e:
        return e
    
    event = database[eventid]
    
    # If embedding has already started
    if event.embedding_inference_id is not None:
        embedding_event = inference_database[event.embedding_inference_id]
        embedding_results = embedding_event.embedding_result
        # If embedding has finished then start blending
        if embedding_results is not None:
            return start_blending_inference(eventid, embedding_results)
        # Else return AlreadyExists
        else:
            return AlreadyExists("Embedding has already started")
    
    if event.uploaded_picture is None:
        return ValueError("There is no uploaded picture to Embed")
    
    inference_eventid = create_eventid()
    inference_event = InferenceEvent(
        inference_eventid = inference_eventid,
        hairchange_eventid = event.eventid,
        type = "Embedding",
        account_identifier = account_identifier,
        uploaded_picture = event.uploaded_picture,
        event_timeout = event.event_timeout
    )
    
    add_to_embedding_queue(inference_event)
    inference_database[inference_eventid] = inference_event
    inference_database[inference_eventid].queue_timestamp = datetime.now()
    
    database[eventid].embedding_inference_id = inference_eventid
        


def post_embed_result(result: dict[str, typing.Any]) -> Exception | None:
    """
    Update the inference event with the embedding results and start the blending inference if the event has already started.

    Args:
        result (dict[str, typing.Any]): A dictionary containing the embedding results.

    Returns:
        None
    """
    embedding_results = EmbeddingInferenceResult(**result)
    
    if embedding_results.inference_eventid not in inference_database:
        return ValueError("Inference event not found")
    
    inference_event = inference_database[embedding_results.inference_eventid]
    
    inference_event.embedding_result = embedding_results
    inference_event.finished_timestamp = datetime.now()
        
    started = start_blending_inference(embedding_results.hairchange_eventid, embedding_results)


def start_blending_inference(hairchange_eventid: str, emdedding_results: EmbeddingInferenceResult) -> Exception | bool:
    """
    Start the blending inference process for a given inference event ID.
    
    Args:
        hairchange_eventid (str): The ID of the inference event.
        emdedding_results (EmbeddingInferenceResult): The embedding results for the inference event.
    
    Raises:
        AssertionError: If the inference event ID is not found in the database.
    
    Returns:
        starting_inference (bool): Whether the inference process was started or not. (True if started, False if not started())
        or
        AlreadyExists: If the inference process has already started for the hairchange event.
    """

    if hairchange_eventid not in database:
        return ValueError("Inference event not found")
    
    event = database[hairchange_eventid]
    
    # Can not start if the hairstyles have not been picked yet
    if event.picked_hairstyles_timestamp is None:
        return False
    
    if event.blend_inference_ids is None:
        event.blend_inference_ids = []
    
    # Makes sure to not add duplicate hairstyles to the blending queue
    hairstyles_to_parse = set(event.hairstyles)
    
    already_added_hairstyles = set()
    
    for blend_inference_id in event.blend_inference_ids:
        blend_inference_event = inference_database[blend_inference_id]
        already_added_hairstyles.add(blend_inference_event.hairstyle)
        
    hairstyles_to_parse = list(hairstyles_to_parse - already_added_hairstyles)
    
    if len(hairstyles_to_parse) == 0:
        return AlreadyExists("Already started Blending")
    
    for hairstyle in hairstyles_to_parse:
        inference_eventid = create_eventid()
        inference_event = InferenceEvent(
            inference_eventid = inference_eventid,
            hairchange_eventid = event.eventid,
            type = "Blending",
            account_identifier = event.account_identifier,
            uploaded_picture = event.uploaded_picture,
            hairstyle = hairstyle,
            embedding_result = emdedding_results,
            event_timeout = event.event_timeout
        )
        
        add_to_blending_queue(inference_event)
            
        inference_database[inference_eventid] = inference_event
        inference_database[inference_eventid].queue_timestamp = datetime.now()   
        
        event.blend_inference_ids.append(inference_eventid) 
        
    return True


def post_blend_result(result: dict[str, typing.Any]):
    """
    Update the blending result for a given inference event.

    Args:
        result (dict[str, typing.Any]): A dictionary containing the blending result.

    Raises:
        AssertionError: If the inference event ID is not found in the inference database.
    """
    blending_results = BlendInferenceResult(**result)
    
    if blending_results.inference_eventid in inference_database:
        return ValueError("Inference event not found")
    
    inference_event = inference_database[blending_results.inference_eventid]
    
    inference_event.blending_result = blending_results
    inference_event.finished_timestamp = datetime.now()