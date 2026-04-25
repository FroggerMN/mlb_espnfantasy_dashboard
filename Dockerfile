FROM python:3.11-slim

WORKDIR /app

# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Install dependencies first (layer cache-friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

EXPOSE 8501

# Run Streamlit in headless mode (no browser, suitable for containers)
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--server.address=0.0.0.0"]
