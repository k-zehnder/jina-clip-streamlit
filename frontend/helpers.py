import base64
from typing import List, Optional, Any
from docarray import DocumentArray, Document
from docarray.array.sqlite import SqliteConfig
from jina import DocumentArray, Document
from jina.clients import Client
from jina.types.request import Request
from docarray import DocumentArray, Document
from docarray.array.sqlite import SqliteConfig
from PIL import Image
import streamlit as st


def get_docs_from_sqlite(connection: str, table: str) -> DocumentArray:
    cfg = SqliteConfig(connection, table)
    return DocumentArray(storage='sqlite', config=cfg)

def create_query_da(search_term: str) -> DocumentArray:
    return DocumentArray(Document(text=search_term))

def get_client(port: int = 12345, show_progress: bool = True) -> Client:
    c = Client(port=port)
    c.show_progress = show_progress
    return c

def resize_image(filename: str, resize_factor: str=2) -> Image:
    image = Image.open(filename)
    w, h = image.size
    return image.resize((w * resize_factor, h * resize_factor), Image.ANTIALIAS)

def search_by_text(query_text, verbose=False):
    client = get_client()
    q = create_query_da(query_text)
    results = client.post('/search', inputs=q, return_results=True)
    if verbose:
        show_results(q, results)
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

