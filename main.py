"""
Nathan Hartzler
CSC790-SP24-Project

Configures the single API route, /query-stream,
and sets up static file serving to serve the 
index.html, chat.js, css, and image files from
the 'static' folder. 

App runs on port 8000
"""
import bot
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
app.mount("/", StaticFiles(directory="static", html=True), name="static")


async def main():
    config = uvicorn.Config("main:app", host="0.0.0.0",
                            port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
