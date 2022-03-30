import os
import pathlib
import shutil
from jina import Flow, Document, DocumentArray
from jina import Executor, Flow, requests
import torch
from transformers import CLIPFeatureExtractor, CLIPModel, CLIPTokenizer
from typing import Optional, Dict, List, Sequence
from docarray import DocumentArray, Document
from docarray.array.sqlite import SqliteConfig



class SimpleIndexer(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # print(os.path.join(self.workspace, 'index.db'))
        self._index = DocumentArray(
            storage='sqlite',
            config={
                'connection': os.path.join(self.workspace, 'index.db'),
                'table_name': 'clip',
            },
        )

    @requests(on='/index')
    def index(self, docs: DocumentArray, **kwargs):
        self._index.extend(docs)
        
    @requests(on='/search')
    def search(self, docs: DocumentArray, **kwargs):
        docs.match(self._index)

