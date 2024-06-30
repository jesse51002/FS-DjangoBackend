# Setup
```sh
# clone and cd
git clone https://github.com/jesse51002/FS-DjangoBackend.git && cd FS-DjangoBackend

# create conda environment
conda create -n DjangoBackend python=3.12

# activate the environment
conda activate DjangoBackend

# install dependencies
pip install -r requirements.txt
```


# Running the server
```sh
python manage.py runserver
```

# Running Tests
```sh
python manage.py test --pattern="tests_*.py"    
```

# Code
Most code is located here:
https://github.com/jesse51002/FS-DjangoBackend/blob/main/hairstyle_creation/views.py

Links:
- "hairstyle_creation/start/", views.start_creation
- "hairstyle_creation/hairstyle_presets/", views.get_hairstyles_presets
- "hairstyle_creation/custom_img/link/", views.get_custom_hairstyle_link
- "hairstyle_creation/custom_img/imageid/", views.get_custom_hairstyle_id
- "hairstyle_creation/rendering/start/", views.start_rendering
- "hairstyle_creation/rendering/results/", views.get_rendering_results
