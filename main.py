from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.graphs import Neo4jGraph

import knowledgegraph
import bot


knowledgegraph.setup()

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bot.router)

@app.get("/")
async def root():
    return "The root api for the Knowledge Graph Bot"