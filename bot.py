"""
Nathan Hartzler
CSC790-SP24-Project

Modified from https://github.com/docker/genai-stack/blob/main/bot.py
and https://github.com/docker/genai-stack/blob/main/api.py
"""
import json
from threading import Thread
from collections.abc import Generator
from queue import Queue, Empty
from langchain.callbacks.base import BaseCallbackHandler
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

import knowledgegraph
from chains import (
    load_embedding_model,
    load_llm,
    configure_qa_kg_chain
)

# Setup the Neo4j database connection
# And build the knowledge graph if needed
knowledgegraph.setup()


class QueueCallback(BaseCallbackHandler):
    """Callback handler for streaming LLM responses to a queue."""

    def __init__(self, q):
        self.q = q

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.q.put(token)

    def on_llm_end(self, *args, **kwargs) -> None:
        return self.q.empty()


class Question(BaseModel):
    text: str


def stream(cb, q) -> Generator:
    """Takes a callback function, cb, and a job queue, q, to
        corrdinate the streaming LLM answers from multiple threads
    """
    job_done = object()

    def task():
        x = cb()
        q.put(job_done)

    t = Thread(target=task)
    t.start()

    content = ""

    # Get each new token from the queue and yield for our generator
    while True:
        try:
            next_token = q.get(True, timeout=1)
            if next_token is job_done:
                break
            content += next_token
            yield next_token, content
        except Empty:
            continue


router = APIRouter()

# Get the embedding layer model
embeddings, _ = load_embedding_model()
# Get the llm loaded
llm = load_llm()
# Create the network connection between the knowledge graph
# and the ollama LLM
kg_chain = configure_qa_kg_chain(llm, embeddings)


@router.get("/query-stream")
def qstream(question: Question = Depends()):
    """Recieves an http request to the /query-stream endpoint
        and returns a text/event-stream media to the client
    """
    output_function = kg_chain

    q = Queue()

    def cb():
        output_function(
            {"question": question.text, "chat_history": []},
            callbacks=[QueueCallback(q)],
        )

    def generate():
        yield json.dumps({"init": True, "model": "llama2:latest"})
        for token, _ in stream(cb, q):
            yield json.dumps({"token": token})

    return EventSourceResponse(generate(), media_type="text/event-stream")
