from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from database import engine, Base
import userRoutes
import projectRoutes
import taskRoutes


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # Create all tables for the shared Base metadata (no-op if already exists).
        await conn.run_sync(Base.metadata.create_all)
        # Ensure `email` column exists on `users` table (safe for dev migrations).
        try:
            await conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS email VARCHAR
            """))
            # Create unique index if not exists (model expects unique index)
            await conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)
            """))
        except Exception:
            # If anything goes wrong here, don't prevent the app from starting.
            pass
    yield
    # Cleanup (optional)
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

app = FastAPI(lifespan=lifespan)

# CORS settings - Must be added before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Root
@app.get("/")
async def read_root():
    return {"message": "Task Management & Collaboration"}

# Include routers
app.include_router(userRoutes.router, prefix="/users", tags=["Users"])
app.include_router(projectRoutes.router, prefix="/projects", tags=["Projects"])
app.include_router(taskRoutes.router, prefix="/tasks", tags=["Tasks"])