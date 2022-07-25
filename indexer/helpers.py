from imutils import paths
from docarray import DocumentArray, Document
from docarray.array.sqlite import SqliteConfig
from jina import DocumentArray, Document
from jina.clients import Client
from jina.types.request import Request
from docarray import DocumentArray, Document
from docarray.array.sqlite import SqliteConfig
from PIL import Image
import pathlib
import os
import shutil


def get_docs_from_sqlite(connection, table):
    cfg = SqliteConfig(connection, table)
    return DocumentArray(storage='sqlite', config=cfg)

def create_query_da(search_term):
    return DocumentArray(Document(text=search_term))

def get_client(port=12345, show_progress=True):
    c = Client(port=port)
    c.show_progress = show_progress
    return c

def resize_image(filename, resize_factor=2):
    image = Image.open(filename)
    w, h = image.size
    return image.resize((w * resize_factor, h * resize_factor), Image.ANTIALIAS)

def get_images():
    IMAGES_PATH = "./data/tattoo_images/*.jpg"
    yield from DocumentArray.from_files(IMAGES_PATH)
    
def get_embedded_da_from_img_files(images_path, num):
    return DocumentArray.from_files(images_path, num).apply(
        lambda d: d.load_uri_to_image_tensor()
        .load_uri_to_image_tensor(200, 200)  # load
        .set_image_tensor_normalization()  # normalize color
        .set_image_tensor_channel_axis(-1, 0)  # switch color axis for the PyTorch model later
    )    

def remove_workspace():
    current_dir = pathlib.Path(__file__).parent.resolve()
    if os.path.exists(os.path.join(current_dir, "workspace")):
        print("[INFO] removing existing workspace...")
        shutil.rmtree(os.path.join(current_dir, "workspace"))

def finished():
    print("[INFO] program complete.")
