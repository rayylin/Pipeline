# Qdrant + 免費 Embedding（SentenceTransformers）— 台灣上市公司 Demo

你會得到一個可在 VS Code 直接打開的 Docker 專案：
- `qdrant`：向量資料庫
- `app`：Python 腳本（匯入 Excel → 做 embedding → 寫入 Qdrant；以及查詢 Top-5）

## 1) 先把 Excel 放到 data/
把你的檔案放到：
`data/台灣上市公司_100家_10產業_含簡介.xlsx`

（檔名可改，但要同步修改 `app/settings.py` 裡的 `EXCEL_PATH`）

## 2) 啟動（Docker Compose）
```bash
docker compose up -d --build
```

Qdrant UI：
- http://localhost:6333/dashboard

## 3) 匯入資料（含 embedding）
```bash
docker compose run --rm app python ingest.py
```

## 4) 查詢（你輸入一句描述）
```bash
docker compose run --rm app python query.py "我想找做晶圓代工、先進製程、跟AI晶片相關的公司"
```

你會看到最相近的 5 家公司（含相似度分數與產業/簡介）。

---

## 資料如何存進 Qdrant（同一 row / point）
每一家公司對應一個 Qdrant point：
- **id**：公司代號（例如 2330）
- **vector**：由「公司簡介 + 產業」組合後的文字做 embedding
- **payload**：保留原始欄位（公司名稱、公司網址、資料來源…等）

向量維度：384（`sentence-transformers/all-MiniLM-L6-v2`）

> 你也可以換成其他免費模型（例如 `paraphrase-multilingual-MiniLM-L12-v2` 支援中文更好但較大），只要同步更新 `VECTOR_SIZE`。
