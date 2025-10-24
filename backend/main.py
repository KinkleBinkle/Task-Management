from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from admin import adminRoutes


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # Create all tables for the shared Base metadata (no-op if already exists).
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup (optional)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

app = FastAPI(lifespan=lifespan)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # or specify e.g. ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root
@app.get("/")
async def read_root():
    return{"message": "Task Management & Collaboration"}

# Include router 

app.include_router(adminRoutes.router, prefix="/admin", tags=["Admin"])