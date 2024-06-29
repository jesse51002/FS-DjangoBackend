from django.urls import path

from .views import client_views, inference_views

urlpatterns = [
    path("hair_try_on/start/", client_views.start_creation, name="start_creation"),
    path("hair_try_on/hairstyle_presets/", client_views.get_hairstyles_presets, name="hairstyles_presets"),
    path("hair_try_on/upload_photo/", client_views.add_uploaded_picture, name="upload_photo"),
    path("hair_try_on/rendering/start/", client_views.start_rendering, name="rendering_start"),
    path("hair_try_on/rendering/results/", client_views.get_rendering_results, name="rendering_results"),
    
    path("hair_try_on/aws_results_post/embedding/", inference_views.post_embed_result, name="embed_results"),
    path("hair_try_on/aws_results_post/blending/", inference_views.post_blend_result, name="blend_results"),
]