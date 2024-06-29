from hairstyle_creation.models import InferenceEvent

ATTEMPTS = 5

def add_to_embedding_queue(inference_event: InferenceEvent) -> None:
    ...

def add_to_blending_queue(inference_event: InferenceEvent) -> None:
    ...