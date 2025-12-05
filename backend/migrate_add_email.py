"""
Migration script to add email column to users table
"""
import asyncio
from sqlalchemy import text
from database import engine

async def add_email_column():
    async with engine.begin() as conn:
        # Add email column if it doesn't exist
        await conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS email VARCHAR UNIQUE
        """))
        
        # Create index on email
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_users_email ON users (email)
        """))
        
        print("✅ Email column added successfully")
        print("✅ Email index created successfully")

if __name__ == "__main__":
    asyncio.run(add_email_column())
