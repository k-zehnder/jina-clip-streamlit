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


class CLIPTextEncoder(Executor):
    """Encode text into embeddings using the CLIP model."""

    def __init__(
        self,
        encode_text=True,
        pretrained_model_name: str = 'openai/clip-vit-base-patch32',
        device: str = 'cpu',
        batch_size: int = 32,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.batch_size = batch_size
        self.device = device

        self.tokenizer = CLIPTokenizer.from_pretrained(
            pretrained_model_name
        )  # load the tokenizer from the transformer library

        self.model = CLIPModel.from_pretrained(
            pretrained_model_name
        )  # load the pretrained clip model from the transformer library

        self.model.eval().to(
            device
        )  # we want to do only inference so we put the model in eval mode

    @requests
    @torch.inference_mode()  # we don't want to keep track of the gradient during inference
    def encode(self, docs: Optional[DocumentArray], parameters: Dict, **kwargs):

        for docs_batch in docs.batch(
            batch_size=self.batch_size
        ):  # we want to compute the embedding by batch of size batch_size
            input_tokens = self._generate_input_tokens(
                docs_batch.texts
            )  # Transformation from raw texts to torch tensor
            docs_batch.embeddings = (
                self.model.get_text_features(**input_tokens).cpu().numpy()
            )  # we compute the embeddings and store it directly in the DocumentArray

    def _generate_input_tokens(self, texts: Sequence[str]):

        input_tokens = self.tokenizer(
            texts,
            max_length=77,
            padding='longest',
            truncation=True,
            return_tensors='pt',
        )
        input_tokens = {k: v.to(self.device) for k, v in input_tokens.items()}
        return input_tokens

# ------------ Driver

flow_search_text = (
    Flow(port=12345)
    .add(uses=CLIPTextEncoder, name='encoder', uses_with={'device': "cpu"})
    .add(uses=SimpleIndexer, name='indexer', workspace='workspace')
)

with flow_search_text:
    # BLOCK
    flow_search_text.block()

