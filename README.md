# Textbook Question Answering System

### Prerequisites

- Install Ollama https://ollama.com/ then run:

  - `> ollama pull llama2`

- Neo4j Database with the APOC plugin installed https://neo4j.com/

- Conda or Miniconda reccomended https://conda.io

### Install

`> conda env create -f env.yml`

then

`> conda activate ir`

finally

`> pip install -r requirements.txt`

### Run

`> python uvicorn main:app`

### Interact

Question Answering App:

http://localhost:8000

Visualize the Knowledge Graph:

http://localhost:7474

Username: neo4j

Password: password
