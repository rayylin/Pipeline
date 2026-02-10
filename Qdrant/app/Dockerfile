FROM python:3.11-slim

WORKDIR /workspace

# 基本編譯工具（部分依賴可能需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r /workspace/requirements.txt

COPY . /workspace

CMD ["python", "query.py", "我想找做半導體、IC設計、跟AI晶片相關的公司"]
