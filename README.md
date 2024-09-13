# Textbook Question Answering System
![The web-based user interface](https://github.com/mjfduss/csc790/blob/main/Interface_Loading.PNG?raw=true)

This project supplements the natural language processing of LLMs with the reliability of a Knowledge Graph in order to prevent LLM hallucinations. This project also uses multiple choice question prompt-binding techniques to improve the succinctness of the answers. The knowledge graph is constructed by crawling the web version of an information retrieval textbook so that multiple choice questions on the subject of information retrieval can be answered with the system. The LLM’s pre-trained knowledge is ignored, and instead the LLM directly references the built knowledge graph when producing answers in natural language.

## Report
Read the report for the [Textbook Question Answering System via
Knowledge Graph](https://github.com/mjfduss/csc790/blob/main/Project%20Report.pdf)


## Installation
----------------------
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

`> python main.py`

### Interact

Question Answering App:

http://localhost:8000

Visualize the Knowledge Graph:

http://localhost:7474

Username: neo4j

Password: password
