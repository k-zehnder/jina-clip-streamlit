# from jina import Flow
# from helper import get_columns, csv_to_docarray
# from config import DEVICE, MAX_DOCS, WORKSPACE_DIR, CSV_FILE, DIMS, TIMEOUT_READY
# import json
# import sys

# if DEVICE == "cuda":
#     gpu_bool = "-gpu"
# else:
#     gpu_bool = ""

# if len(sys.argv) == 2:
#     MAX_DOCS = int(sys.argv[1])

# print(f"Indexing {MAX_DOCS} documents")

# def index(csv_file, max_docs):
#     docs = csv_to_docarray(file_path=csv_file, max_docs=max_docs)

#     # Get all the column info from first doc
#     columns = get_columns(docs[0])  

#     # Pickle values so search fn can pick up later
#     with open("columns.json", "w") as file:
#         json.dump(columns, file)

#     flow = (
#         Flow()
#         .add(
#             uses=f"jinahub://CLIPEncoder/v0.3.0{gpu_bool}",
#             name="encoder",
#             uses_with={"device": DEVICE},
#             install_requirements=True,
#             uses_metas={"timeout_ready": TIMEOUT_READY},
#             # replicas=2,
#         )
#         .add(
#             name="TensorDeleter",
#             uses="jinahub://TensorDeleter",
#         )
#         .add(
#             uses="jinahub://PQLiteIndexer/latest",
#             name="indexer",
#             uses_with={
#                 "dim": DIMS,
#                 "columns": columns,
#                 "metric": "cosine",
#                 "include_metadata": True,
#             },
#             uses_metas={"workspace": WORKSPACE_DIR},
#             volumes=f"./{WORKSPACE_DIR}:/workspace/workspace",
#             install_requirements=True,
#         )
#     )

#     with flow:
#         docs = flow.index(inputs=docs, show_progress=True, return_results=True)

#     print(f"Indexed {len(docs)} Documents")


# if __name__ == "__main__":
#     index(csv_file=CSV_FILE, max_docs=MAX_DOCS)

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
from helpers import get_embedded_da_from_img_files, plot_search_results, load_caltech


IMAGES_PATH = "../data/images/*.jpg"
# NOTE: need to have docker desktop running for this to work on macs

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
images = get_embedded_da_from_img_files(IMAGES_PATH, num=150)
# images = load_caltech("./data/caltech101", num=1500)
# print(f"images: {images}")

current_dir = pathlib.Path(__file__).parent.resolve()
if os.path.exists(os.path.join(current_dir, "workspace")):
    print("[INFO] removing existing workspace...")
    shutil.rmtree(os.path.join(current_dir, "workspace"))

flow_index = (
    Flow(port=12345)
    .add(uses=CLIPImageEncoder, name='encoder', uses_with={'device': "cpu"})
    .add(uses=SimpleIndexer, name='indexer', workspace='workspace')
)

with flow_index:
    flow_index.post(on='/index', inputs=images, on_done=print, return_results=True)

flow_search_text = (
    Flow(port=12345)
    .add(uses=CLIPTextEncoder, name='encoder', uses_with={'device': "cpu"})
    .add(uses=SimpleIndexer, name='indexer', workspace='workspace')
)

with flow_search_text:
    # BLOCK
    flow_search_text.block()

