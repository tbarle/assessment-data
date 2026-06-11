FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy input data and scripts preserving the directory structure
# that both scripts expect (ROOT = script's parent.parent.parent)
COPY data/ ./data/
COPY expected_output/task2/etl_pipeline.py ./expected_output/task2/etl_pipeline.py
# Script in a separate dir so the volume mount on expected_output/task3/ doesn't hide it
COPY expected_output/task3/prepare_knowledge_base.py ./scripts/task3/prepare_knowledge_base.py

# Run ETL first (produces cleaned_data/), then generate embeddings
CMD ["sh", "-c", "python expected_output/task2/etl_pipeline.py && python scripts/task3/prepare_knowledge_base.py"]
