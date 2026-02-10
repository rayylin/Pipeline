import os

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "tw_listed_companies")

# 免費 embedding 模型（384 維）
MODEL_NAME = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
VECTOR_SIZE = 384

EXCEL_PATH = os.getenv("EXCEL_PATH", "/workspace/data/台灣上市公司_100家_10產業_含簡介.xlsx")
