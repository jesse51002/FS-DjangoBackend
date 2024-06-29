from datetime import datetime
import typing

from hairstyle_creation.errors import AlreadyExists
from hairstyle_creation.models import (
    UploadPicture,
    Hairstyle,
    HairstyleChangeEvent,
    BlendInferenceResult,
    create_eventid,
    database,
    inference_database
)


def assert_account_has_event(account_identifier: str, eventid: str):
    """
    Asserts that the given account identifier has a change event with the specified event ID.

    Args:
        account_identifier (str): The identifier of the account.
        eventid (str): The ID of the change event.

    Returns:
        None

    Raises:
        Exception: If the event with the specified ID does not exist.
        Exception: If the account does not have an event with the specified ID.
    """
    if eventid not in database:
        raise Exception(f"The event with id {eventid} does not exist.")
    
    if database[eventid].accout_identifier != account_identifier:
        raise PermissionError(f"Account {account_identifier} does not have an event with id {eventid}.")

def create_new_hairstyle_event(
    account_identifier: str,
    ):
    """
    Creates a new hairstyle change event and uploads it to the database.

    Args:
        account_identifier (str): The identifier of the account associated with the event.

    Returns:
        eventid (str): The unique identifier of the newly created event.

    It then creates a new `HairstyleChangeEvent` object with the
    generated event identifier and the provided account identifier.
    """
    eventid = create_eventid()
    
    # Uploads the event to the database
    database[eventid] = HairstyleChangeEvent(
        eventid = eventid,
        account_identifier = account_identifier
    )
        
    return eventid


def add_hairstyles(account_identifier: str, eventid: str, hairstyles: list[dict[str, typing.Any]]) -> Exception | None:
    """
    Adds hairstyles choices to a change event in the database.

    Args:
        account_identifier (str): The identifier of the account associated with the change event.
        eventid (str): The unique identifier of the change event.
        hairstyles (list[dict[str, typing.Any]]): A list of dictionaries representing the hairstyles choices.

    Returns:
        None
   
    Raises:
        Exception: If the account does not have an event with the provided eventid.
    """
    try:
        assert_account_has_event(account_identifier, eventid)
    except Exception as e:
        return e
    
    if database[eventid].picked_hairstyles_timestamp is not None:
        return AlreadyExists("Already picked hairstyles for this event")
    
    hairstyles: list[Hairstyle] = []
    
    for hairstyle in hairstyles:
        hairstyles.append(Hairstyle(**hairstyle))
    
    database[eventid].hairstyles = hairstyles
    database[eventid].picked_hairstyles_timestamp = datetime.now()
   
 
def add_uploaded_picture(account_identifier: str, eventid: str, picture: dict[str, typing.Any]) -> Exception | None:
    """
    Adds uploaded pictures to a change event in the database.

    Args:
        account_identifier (str): The identifier of the account associated with the change event.
        eventid (str): The unique identifier of the change event.
        pictures (list[dict[str, typing.Any]]): A list of dictionaries representing the uploaded pictures.

    Returns:
        (UserError | None): Either None if the upload was successful, or a UserError if the upload was unsuccessful.
   
    Raises:
        Exception: If the account does not have an event with the provided eventid.
    """
    try:
        assert_account_has_event(account_identifier, eventid)
    except Exception as e:
        return e
    
    if database[eventid].uploaded_picture_timestamp is not None:
        return AlreadyExists("Already uploaded a picture for this event")
            
    database[eventid].uploaded_picture = UploadPicture(**picture)
    database[eventid].uploaded_picture_timestamp = datetime.now()


def get_results(account_identifier: str, eventid: str) -> Exception | list[BlendInferenceResult] | None:
    """
    Get the hair change results for a specific account and event.

    Args:
        account_identifier (str): The identifier of the account associated with the change event.
        eventid (str): The unique identifier of the change event.

    Returns:
        TimeoutError: If the event has timed out.
        list[BlendInferenceResult] | None: The list of hair inference results for the event, or None if the event is not finished.
    """
    try:
        assert_account_has_event(account_identifier, eventid)
    except Exception as e:
        return e
    
    event = database[eventid]
    
    if datetime.now() > event.event_timeout:
        handle_timeout(eventid=eventid)
        return TimeoutError("Event has timed out")
    
    # If it has not started, return False
    if (event.start_timestamp is None or
        event.uploaded_picture_timestamp is None or
        event.picked_hairstyles_timestamp is None or
        event.embedding_inference_id is None or 
        event.blend_inference_ids is None):
        return None
    
    blend_results: list[BlendInferenceResult] = []
    
    for inference_id in event.blend_inference_ids:
        inference_event = inference_database[inference_id]
        
        # If any inference event has not finished, return None because it is not finished
        if inference_event.finished_timestamp is None:
            return None
        
        blend_results.append(inference_event.blending_result)
    
    # If all inference events have finished, set the event as finished
    if event.finished_timestamp is not None:
        event.finished_timestamp = datetime.now()
    
    return blend_results


def handle_timeout(eventid: str):
    raise NotImplementedError()