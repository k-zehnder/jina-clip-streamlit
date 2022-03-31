import os
from jina import Flow, Document, DocumentArray
from jina import Flow, Document, DocumentArray, Executor, Flow, requests
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


class CLIPImageEncoder(Executor):
    """Encode image into embeddings using the CLIP model."""

    def __init__(
        self,
        pretrained_model_name: str = "openai/clip-vit-base-patch32",
        device: str = "cpu",
        batch_size: int = 32,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.batch_size = batch_size

        self.device = device
        self.preprocessor = CLIPFeatureExtractor.from_pretrained(pretrained_model_name)
        self.model = CLIPModel.from_pretrained(
            pretrained_model_name
        )  # load the pretrained clip model from the transformer library

        self.model.to(
            self.device
        ).eval()  # we want to do only inference so we put the model in eval mode

    @requests
    @torch.inference_mode()  # we don't want to keep track of the gradient during inference
    def encode(self, docs: DocumentArray, parameters: dict, **kwargs):

        for batch_docs in docs.batch(
            batch_size=self.batch_size
        ):  # we want to compute the embedding by batch of size batch_size
            tensor = self._generate_input_features(
                batch_docs
            )  # Transformation from raw images to torch tensor
            batch_docs.embeddings = (
                self.model.get_image_features(**tensor).cpu().numpy()
            )  # we compute the embeddings and store it directly in the DocumentArray

    def _generate_input_features(self, docs: DocumentArray):
        docs.apply(lambda d: d.load_uri_to_image_tensor())
        input_features = self.preprocessor(
            images=[d.tensor for d in docs],
            return_tensors="pt",
        )
        input_features = {
            k: v.to(torch.device(self.device)) for k, v in input_features.items()
        }
        return input_features

# ------------ Driver

flow_search_image = (
    Flow(port=12345)
    .add(uses=CLIPImageEncoder, name='encoder', uses_with={'device': "cpu"})
    .add(uses=SimpleIndexer, name='indexer', workspace='workspace')
)

with flow_search_image:
    # BLOCK
    flow_search_image.block()

