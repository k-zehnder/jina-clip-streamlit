import base64
from docarray import DocumentArray, Document
from docarray.array.sqlite import SqliteConfig
from jina import DocumentArray, Document
from jina.clients import Client
from PIL import Image
import streamlit as st
from config import IMAGE_RESIZE_FACTOR


def get_docs_from_sqlite(connection: str, table: str) -> DocumentArray:
    cfg = SqliteConfig(connection, table)
    return DocumentArray(storage='sqlite', config=cfg)

def create_query_da(search_term: str) -> DocumentArray:
    return DocumentArray(Document(text=search_term))

def get_client(port: int = 12345, show_progress: bool = True) -> Client:
    c = Client(port=port)
    c.show_progress = show_progress
    return c

def resize_image(filename: str, resize_factor: str=IMAGE_RESIZE_FACTOR) -> Image:
    image = Image.open(filename)
    w, h = image.size
    return image.resize((w * resize_factor, h * resize_factor), Image.ANTIALIAS)

def search_by_text(query_text, verbose=False):
    client = get_client()
    input_docarray = create_query_da(query_text)
    results = client.post('/search', inputs=input_docarray, return_results=True, show_progress=True)
    if verbose:
        show_results(input_docarray, results)
    return results

def search_by_image(input):
    data = input.read()
    query_doc = Document(blob=data)
    query_doc.convert_blob_to_image_tensor()
    query_doc.set_image_tensor_shape((80, 60))

    client = get_client()
    results = client.post('/search',
        query_doc,
        return_results=True,
        show_progress=True
    )
    return results

def show_results(query, results):
    print(f"query_text: {query[0].text}")
    for d in results:
        for m in d.matches:
            print(d.uri, m.uri, m.scores['cosine'].value)
    return results

def set_bg_hack_url(url: str) -> None:
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url({url});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

def sidebar_bg(side_bg: str) -> None:
   side_bg_ext = 'png'
   st.markdown(
      f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
          background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
      }}
      </style>
      """,
      unsafe_allow_html=True,
      )

