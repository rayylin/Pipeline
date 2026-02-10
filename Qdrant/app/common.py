from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Tuple

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer

import settings


def get_client() -> QdrantClient:
    return QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)


def get_model() -> SentenceTransformer:
    # 第一次會下載模型（已在 docker-compose 掛 model_cache volume 做快取）
    return SentenceTransformer(settings.MODEL_NAME)


def ensure_collection(client: QdrantClient) -> None:
    # 若已存在就跳過；不存在才建立
    existing = [c.name for c in client.get_collections().collections]
    if settings.COLLECTION_NAME in existing:
        return

    client.create_collection(
        collection_name=settings.COLLECTION_NAME,
        vectors_config=VectorParams(
            size=settings.VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
    )


def normalize_text(s: str) -> str:
    return (s or "").strip()


def build_embedding_text(industry: str, intro: str) -> str:
    # 你指定要「公司簡介 + 產業」做 embedding
    industry = normalize_text(industry)
    intro = normalize_text(intro)
    return f"產業：{industry}\n公司簡介：{intro}"
