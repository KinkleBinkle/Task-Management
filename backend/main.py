from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import userRoutes
import projectRoutes
import taskRoutes


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
    allow_origins=["*"],   # or specify e.g. ["http://localhost:5174"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root
@app.get("/")
async def read_root():
    return {"message": "Task Management & Collaboration"}

# Include routers
app.include_router(userRoutes.router, prefix="/users", tags=["Users"])
app.include_router(projectRoutes.router, prefix="/projects", tags=["Projects"])
app.include_router(taskRoutes.router, prefix="/tasks", tags=["Tasks"])