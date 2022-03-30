import sys
import os
import pathlib
import shutil
from jina import Flow, Document, DocumentArray
from jina import Executor, Flow, requests


# import parent dir so as to be able to locate modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from executor import CLIPImageEncoder
from executor import SimpleIndexer


# ------------ Driver
# NOTE: need to have docker desktop running for this to work on macs
IMAGES_PATH = "./data/tattoo_images/*.jpg"
images = DocumentArray.from_files(IMAGES_PATH)
# images = get_embedded_da_from_img_files(IMAGES_PATH, num=50) # num doesnt reduce array size?
print(images.summary())

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
    print('\n\n[INFO] Finished indexing.')

