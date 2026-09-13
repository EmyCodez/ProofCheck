FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Download the embedding model during image build so Cloud Run
# does not depend on Hugging Face during container startup.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

ENV PYTHONPATH=/app/src
ENV PORT=8080

EXPOSE 8080

CMD ["python", "-m", "proofcheck.ui.app"]
