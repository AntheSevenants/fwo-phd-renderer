FROM python:3.11-slim

WORKDIR /app

COPY . /app

# COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x fwo-phd-renderer.py

ENTRYPOINT ["python", "fwo-phd-renderer.py", "/knowledge_base", "--out_path", "/out"]