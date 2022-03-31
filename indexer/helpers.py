import os
import cv2
import imutils
from imutils import paths
from docarray import DocumentArray, Document
from docarray.array.sqlite import SqliteConfig
from jina import DocumentArray, Document
from jina.clients import Client
from jina.types.request import Request
from docarray import DocumentArray, Document
from docarray.array.sqlite import SqliteConfig
from PIL import Image



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

