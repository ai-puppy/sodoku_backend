from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, games

app = FastAPI(
    title="Sudoku Game API",
    description="A FastAPI backend for Sudoku game with user authentication",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(games.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to Sudoku Game API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
