from __future__ import annotations

import pandas as pd
from qdrant_client.models import PointStruct

from common import get_client, get_model, ensure_collection, build_embedding_text
import settings


def main() -> None:
    client = get_client()
    ensure_collection(client)

    df = pd.read_excel(settings.EXCEL_PATH)

    # 期待 Excel 欄位（如你的檔案）
    required_cols = [
        "產業(10類)",
        "產業別代碼",
        "公司代號",
        "公司名稱",
        "公司簡稱",
        "公司網址",
        "公司簡介(約300字)",
        "資料來源",
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Excel 欄位缺少：{missing}\n目前欄位：{list(df.columns)}")

    # 建立 embedding 文字（只用公司簡介 + 產業）
    embed_texts = [
        build_embedding_text(row["產業(10類)"], row["公司簡介(約300字)"])
        for _, row in df.iterrows()
    ]

    model = get_model()
    vectors = model.encode(embed_texts, batch_size=32, show_progress_bar=True, normalize_embeddings=True)

    points = []
    for i, row in df.iterrows():
        company_code = int(row["公司代號"])
        payload = {
            "industry_10": row["產業(10類)"],
            "industry_code": int(row["產業別代碼"]),
            "company_code": company_code,
            "company_name": row["公司名稱"],
            "company_short_name": row["公司簡稱"],
            "company_url": row["公司網址"],
            "company_intro": row["公司簡介(約300字)"],
            "source": row["資料來源"],
        }

        points.append(
            PointStruct(
                id=company_code,
                vector=vectors[i].tolist(),
                payload=payload,
            )
        )

    client.upsert(collection_name=settings.COLLECTION_NAME, points=points)
    print(f"✅ 已匯入 {len(points)} 筆到 Qdrant collection: {settings.COLLECTION_NAME}")


if __name__ == "__main__":
    main()
