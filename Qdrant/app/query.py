from __future__ import annotations

import sys
from common import get_client, get_model, ensure_collection
import settings


def main() -> None:
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        raise SystemExit("請提供查詢句子，例如：python query.py \"我想找做晶圓代工的公司\"")

    client = get_client()
    ensure_collection(client)

    model = get_model()
    qvec = model.encode([query], normalize_embeddings=True)[0].tolist()

    # 直接用 Qdrant ANN + cosine 距離做 Top-5
    # （若你想更像你前面說的「先取 500 再精排」，可把 limit 改 500 然後自行 cosine rerank）
    results = client.search(
        collection_name=settings.COLLECTION_NAME,
        query_vector=qvec,
        limit=5,
        with_payload=True,
        # 調大 ef 讓 ANN 更準（資料量更大時可再調）
        search_params={"hnsw_ef": 256},
    )

    print("\n🔎 Query:", query)
    print("Top 5 最相似公司：\n")
    for r in results:
        p = r.payload or {}
        print(f"- {p.get('company_short_name')}（{p.get('company_code')}）| score={r.score:.4f}")
        print(f"  產業：{p.get('industry_10')}")
        intro = (p.get('company_intro') or '').strip()
        if len(intro) > 120:
            intro = intro[:120] + "..."
        print(f"  簡介：{intro}")
        print(f"  網址：{p.get('company_url')}")
        print()

if __name__ == "__main__":
    main()
