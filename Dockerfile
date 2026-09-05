# ─────────────────────────────────────────────────────────────────
# FinMate AI — Dockerfile
# Target: Render free-tier Docker Web Service
# ─────────────────────────────────────────────────────────────────

FROM python:3.11-slim

# ── System packages ───────────────────────────────────────────────
# tesseract-ocr  → pytesseract
# libgl1         → opencv-python-headless (cv2.imshow fallback)
# libglib2.0-0   → opencv internal GLib dependency
RUN apt-get update && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ───────────────────────────────────────────
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ──────────────────────────────────────────────
COPY . .

# ── Runtime ───────────────────────────────────────────────────────
# Render injects $PORT at runtime; we forward it to Streamlit.
# The shell form of CMD is intentional so $PORT is expanded.
EXPOSE 8501
CMD streamlit run app.py \
        --server.port=$PORT \
        --server.address=0.0.0.0 \
        --server.headless=true
