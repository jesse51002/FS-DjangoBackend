from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest

from datetime import datetime
from uuid import uuid4
import json

# Links for the hairstyles
HAIRSTYLE_PRESET_LINKS = [
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQQk0WZTFFVUB6WVoVzpJUL1e9CnUKcC4NFFQ&usqp=CAU",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQqw-QW4mIv2iUX4lGZlhbX0fh644yRVfwEwA&usqp=CAU",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSTNhll_-c0syMENDjudM9K-KFiitxIZ4iumg&usqp=CAU",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRs5mHctzXpwLoaD7DMpXaMg67hh-9zmf-BQw&usqp=CAU",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShUzrAMs9I-qU5p_SZgWRoQYno7M57WDWEiKhZWiLbqtst8_L4KmeXHB_j5LQ36HcIT8A&usqp=CAU",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoZxffMAns0_2l7DBCcIt-KG7NTCMRx7KxKg&usqp=CAU"
    ]

DIRECTIONS = ["front", "right", "left", "back"]


custom_hairstyle_events = {}

hairstyle_rendering_events = {}

# This is called at the start of the hairstyle creation in order to get the Creation ID
# Input: None
# Output: EventID
def start_creation(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Must use a GET request")
    
    # Generates ID
    eventid = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
    
    return JsonResponse({"eventid": eventid})

# This supplies the image links and id for all the hairstyle presets
# Input: EventID
# Output: List of Hairstyles IDs and links
def get_hairstyles_presets(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Must use a GET request")

    eventid = request.GET.get('eventid')
    print("EventID: ",eventid)
    # Valides eventID
    if eventid == None:
        return HttpResponseBadRequest("Invalid or missing EventID")
    
    # Creates a list of links and ids
    hairstyles = []
    for i, link in enumerate(HAIRSTYLE_PRESET_LINKS):
        hairstyles.append({
            "hairstlye_id":i, 
            "hairstyle_url": link
            }
            )
    
    # Returns data
    return JsonResponse({"Hairstyles": hairstyles})

# This returns client custom hairstyle upload link
# Input: EventID
# Output: Client custom hairstyle upload link
def get_custom_hairstyle_link(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Must use a GET request")
    
    eventid = request.GET.get('eventid')
    print("EventID: ",eventid)
    # Valides eventID
    if eventid == None:
        return HttpResponseBadRequest("Invalid or missing EventID")
    
    # Saves the eventid as a custom hairstyle event
    custom_hairstyle_events[eventid] = 0
    
    # Link to be sent for the custom upload
    custom_link = "www.google.com"
    
    # Returns data
    return JsonResponse({"link": custom_link})

# This returns the hairstyle id of the custom image of a eventid or its current status
# Will return true after being called 3 or more times
# Input: EventID
# Output: custom image id and in_progress boolean
def get_custom_hairstyle_id(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Must use a GET request")
    
    eventid = request.GET.get('eventid')
    print("EventID: ",eventid)
    # Valides eventID
    if eventid == None:
        return HttpResponseBadRequest("Invalid or missing EventID")
    
    # if the event doesnt exist then invalid request
    if eventid not in custom_hairstyle_events:
        return HttpResponseBadRequest("Event ID does not have a custom hairstyle event")
    
    # Adds the ping to the id
    custom_hairstyle_events[eventid] += 1
    
    # Must be pinged 3 times in order for the correct ID to be sent
    inprogress = custom_hairstyle_events[eventid] < 3
    
    # Returns data
    return JsonResponse({
        "inprogress": inprogress,
        "hairstyle_id": 20 if not inprogress else -1
        })
    
    

# This returns client custom hairstyle upload link
# Input: EventID, hairstyleID, Each Photo Direction image url/id
# Output: Success Bool
def start_rendering(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Must use a GET request")
    
    eventid = request.GET.get('eventid')
    print("EventID: ",eventid)
    # Valides eventID
    if eventid == None:
        return HttpResponseBadRequest("Invalid or missing EventID")
    
    body_data = json.loads(request.body)
    print("Inputed Data: ", body_data)
    
    # Valides hairstyleID
    if "hairstyle_id" not in body_data:
        return HttpResponseBadRequest("Invalid or missing HairstyleID")
    
    # Valides Photo_ids
    if "photo_ids" not in body_data or not isinstance(body_data["photo_ids"], dict):
        return HttpResponseBadRequest("Invalid or missing PhotoID")
    # Makes sure all angles are in the request
    for d in DIRECTIONS:
        if d not in body_data["photo_ids"]:
            return HttpResponseBadRequest(f"Missing {d} photo direction")
    
    # Saves the eventid as a custom hairstyle event
    hairstyle_rendering_events[eventid] = 0

    # Returns data
    return JsonResponse({"sucess": True})



# This returns the image transformation results or its status
# Will return true after being called 3 or more times
# Input: EventID
# Output: custom image id and in_progress boolean
def get_rendering_results(request):
    if request.method != "GET":
        return HttpResponseBadRequest("Must use a GET request")
    
    eventid = request.GET.get('eventid')
    print("EventID: ",eventid)
    # Valides eventID
    if eventid == None:
        return HttpResponseBadRequest("Invalid or missing EventID")
    
    # if the event doesnt exist then invalid request
    if eventid not in hairstyle_rendering_events:
        return HttpResponseBadRequest("Event ID does not have a rendering event")
    
    # Adds the ping to the id
    hairstyle_rendering_events[eventid] += 1
    
    # Must be pinged 3 times in order for the correct ID to be sent
    inprogress = hairstyle_rendering_events[eventid] < 3
    
    # Creates output
    results_output = {}
    for d in DIRECTIONS:
        results_output[d] = HAIRSTYLE_PRESET_LINKS[0]
        
    # Returns data
    return JsonResponse({
        "inprogress": inprogress,
        "hairstyle_id": results_output if not inprogress else None
        })