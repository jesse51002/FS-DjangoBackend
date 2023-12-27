from django.urls import path

from . import views

urlpatterns = [
    path("start/", views.start_creation, name="start_creation"),
    path("hairstyle_presets/", views.get_hairstyles_presets, name="hairstyles_presets"),
    path("custom_img/link/", views.get_custom_hairstyle_link, name="custom_hair_link"),
    path("custom_img/imageid/", views.get_custom_hairstyle_id, name="custim_hair_id"),
    path("rendering/start/", views.start_rendering, name="rendering_start"),
    path("rendering/results/", views.get_rendering_results, name="rendering_results"),
]