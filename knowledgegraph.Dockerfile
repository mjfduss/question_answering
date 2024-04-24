FROM langchain/langchain

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade -r requirements.txt

COPY knowledgegraph.py .
COPY utils.py .
COPY chains.py .
COPY crawler.py .
COPY images ./images

EXPOSE 8502

HEALTHCHECK CMD curl --fail http://localhost:8502/_stcore/health

ENTRYPOINT ["streamlit", "run", "knowledgegraph.py", "--server.port=8502", "--server.address=0.0.0.0"]