# indexing data
# DOCARRAY_PULL_NAME = 'fashion-multimodal-all'
DATA_DIR = "../data/images" # Where are the files?
# WORKSPACE_DIR = "../embeddings"
MAX_DOCS = 100
DEVICE = "cpu"

# serving via REST
PORT = 12345

# metas for executors
TIMEOUT_READY = -1 # Wait forever for executor to be ready. Good for slow connections