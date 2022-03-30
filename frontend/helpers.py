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

def get_embedded_da_from_img_files(images_path, num):
    return DocumentArray.from_files(images_path, num).apply(
        lambda d: d.load_uri_to_image_tensor()
        .load_uri_to_image_tensor(200, 200)  # load
        .set_image_tensor_normalization()  # normalize color
        .set_image_tensor_channel_axis(-1, 0)  # switch color axis for the PyTorch model later
    )    

def create_query_da(search_term):
    return DocumentArray(Document(text=search_term))

def get_client(port=12345, show_progress=True):
    c = Client(port=port)
    c.show_progress = show_progress
    return c

def search_by_text(query_text, verbose=False):
    client = get_client()
    q = create_query_da(query_text)
    results = client.post('/search', inputs=q, return_results=True)
    if verbose:
        show_results(q, results)
    return results

def plot_search_results(resp: Request):
    for doc in resp.docs:
        print(f'Query text: {doc.text}')
        print(f'Matches:')
        print('-' * 10)
        print([d.uri for d in doc.matches[:3]])
        print()

def show_results(query, results):
    print(f"query_text: {query[0].text}")
    for d in results:
        for m in d.matches:
            print(d.uri, m.uri, m.scores['cosine'].value)
    return results

def resize_image(filename, resize_factor=2):
    image = Image.open(filename)
    w, h = image.size
    image.resize((w * resize_factor, h * resize_factor), Image.ANTIALIAS)
    return image