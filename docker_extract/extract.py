from pyspark import SparkConf, SparkContext
import os # pour les chemins de fichiers
import json # pour les fichiers JSON
from PIL import Image
from PIL.ExifTags import TAGS # pour les métadonnées
from PIL.TiffImagePlugin import IFDRational

# encodeur json pour les bytes et les rationnels (pour les métadonnées)
class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            try:
                return obj.decode('utf-8')
            except UnicodeDecodeError:
                return obj.decode('utf-8', 'replace')
        elif isinstance(obj, IFDRational):
            return float(obj)
        return json.JSONEncoder.default(self, obj)

# fonction pour extraire les métadonnées d'une image
def extract_metadata(filename):
    # extrait les métadonnées
    image = Image.open(os.path.join(path_to_folder, filename))
    exifdata = image.getexif()
    metadata = {}

    # ajoute les métadonnées à la liste
    for tag_id, value in exifdata.items():
        tag = TAGS.get(tag_id, tag_id)
        metadata[tag] = value

    # Convert the dictionary to JSON and store it in a file
    json_filename = os.path.splitext(filename)[0] + '.json'
    with open(os.path.join('/app/metadata', json_filename), 'w') as f:
        json.dump(metadata, f, cls=MyEncoder)

    return filename

# chemin vers le dossier images
path_to_folder = os.path.abspath('/app/images')

# crée le dossier metadata s'il n'xiste pas
if not os.path.exists('metadata'):
    os.mkdir('metadata')

# configuration de Spark
conf = SparkConf().setAppName("ImageMetadataExtractor")
sc = SparkContext(conf=conf)

# liste des images
image_files = [f for f in os.listdir(path_to_folder) if f.endswith('.jpg') or f.endswith('.jpeg') or f.endswith('.png')]

# parallélise la liste des images et applique la fonction extract_metadata à chaque image
images_rdd = sc.parallelize(image_files)
images_rdd.map(extract_metadata).collect()