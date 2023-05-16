# Gérer les imports
import requests # pour les requêtes HTTP
import os # pour les chemins de fichiers


# image_downloader.py
#

# accès api pexels
url = "https://api.pexels.com/v1/search"
access_key = "MgxBjp4CnSFtTvWe3SeHtkTGp5oUOBWVG5S0PYZAd37hV3T3h2yY4PHp"

# header d'authentification basique
headers = {
    "Authorization": access_key
}

# construction de la requête
path = os.path.abspath("/app/images")
num_images = 60

query_params = {
    "query": "random",
    "per_page": num_images
}

# créée le dossier de destination si il n'existe pas
if not os.path.exists(path):
    os.makedirs(path)

# on veut savoir combien d'images il manque
existing_images = len([f for f in os.listdir(path) if f.endswith(('.jpg', '.jpeg', '.png'))])
missing_images = max(num_images - existing_images, 0)
##print(f"Images manquantes: {missing_images}")

# 
query_params["per_page"] = num_images

# envoi de la requête et téléchargement des images
if missing_images > 0:
    response = requests.get(url, headers=headers, params=query_params)
    json = response.json()
    photos = json.get("photos", [])

    downloaded = 0
    for photo in photos:
        if downloaded >= missing_images:
            break

        image_url = photo["src"]["original"]
        image_id = photo["id"]
        image_extension = ".jpg"
        image_filename = f"{image_id}{image_extension}"
        image_path = os.path.join(path, image_filename)

        if not os.path.exists(image_path):
            # 
            response = requests.get(image_url)
            with open(image_path, "wb") as f:
                f.write(response.content)
            downloaded += 1
