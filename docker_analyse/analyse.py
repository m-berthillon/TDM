import os
import json
from PIL import Image
from PIL.ExifTags import TAGS
import cv2
from colorthief import ColorThief
import pytesseract
import torchvision
import torchvision.transforms as T
from torchvision.models.detection import fasterrcnn_resnet50_fpn

#inisalisation du path to folder
path_to_folder = os.path.abspath('/app/images')

# initialise le modèle ViT en mode évaluation
model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

image_path = os.path.abspath("/app/images")

# fonction pour récupérer les métadonnées d'une image
def get_image_metadata(image_path):
    metadata = {}

    # lire l'image avec PIL et OpenCV
    pil_image = Image.open(image_path)
    cv_image = cv2.imread(image_path)

    # obtenir la couleur dominante et la palette de couleurs
    color_thief = ColorThief(image_path)
    dominant_color = color_thief.get_color(quality=1)
    color_palette = color_thief.get_palette(color_count=5)

    # l'orientation de l'image
    exif_data = pil_image._getexif()
    orientation = exif_data[274] if exif_data and 274 in exif_data else "unknown"

    # reconnaissance faciale
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=3)
    num_faces = len(faces)

    # reconnaissance de texte
    pil_image_rgb = pil_image.convert('RGB')
    text = pytesseract.image_to_string(pil_image_rgb)

    # détection d'objets
    transform = T.Compose([T.Resize(256), T.CenterCrop(224), T.ToTensor()])
    img = transform(Image.open(image_path))
    img = img.unsqueeze(0)
    detections = model(img)

    objects = []
    for label, score in zip(detections[0]["labels"], detections[0]["scores"]):
        if score > 0.5:
            objects.append(label.item())


    # dict des métadonnées
    metadata = {
        "orientation": orientation,
        "dominant_color": dominant_color,
        "color_palette": color_palette,
        "num_faces": num_faces,
        "text": text,
        "objects": objects,
    }

    return metadata

# on boucle sur les images du dossier
metadata_path = os.path.abspath("/app/metadata") # Ajoutez cette ligne
for filename in os.listdir(path_to_folder):
    if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
        # on récupère les métadonnées
        image_path = os.path.join(path_to_folder, filename)
        metadata = get_image_metadata(image_path)

        # on sauvegarde les métadonnées dans un fichier json
        with open(os.path.join(metadata_path, os.path.splitext(filename)[0] + ".json"), "w") as f: # Modifiez cette ligne
            json.dump(metadata, f)