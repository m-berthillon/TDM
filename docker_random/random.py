import os
import random
import shutil

image_folder = "/app/images"
metadata_folder = "/app/metadata"
preferred_folder = "/app/prefered_image"

# Create preferred folder if it doesn't exist
if not os.path.exists(preferred_folder):
    os.makedirs(preferred_folder)

images = [img for img in os.listdir(image_folder) if img.endswith('.jpg')]
random_image = random.choice(images)

# Move image
shutil.move(os.path.join(image_folder, random_image), preferred_folder)

# Move corresponding metadata
metadata_file = random_image.replace('.jpg', '.json')
shutil.move(os.path.join(metadata_folder, metadata_file), preferred_folder)