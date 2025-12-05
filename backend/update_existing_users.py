"""
Check existing users and update them with placeholder emails if needed
"""
import asyncio
from sqlalchemy import text, select
from database import engine, get_db
from models import User

async def check_and_update_users():
    async with engine.begin() as conn:
        # Check for users without email
        result = await conn.execute(text("""
            SELECT id, username, email FROM users WHERE email IS NULL
        """))
        
        users_without_email = result.fetchall()
        
        if users_without_email:
            print(f"⚠️  Found {len(users_without_email)} users without email addresses")
            print("Updating with placeholder emails...")
            
            for user in users_without_email:
                placeholder_email = f"{user.username}@placeholder.local"
                await conn.execute(text("""
                    UPDATE users 
                    SET email = :email 
                    WHERE id = :user_id
                """), {"email": placeholder_email, "user_id": user.id})
                print(f"  ✅ Updated user '{user.username}' with email: {placeholder_email}")
            
            print("\n⚠️  IMPORTANT: These users should update their real email addresses!")
        else:
            print("✅ All users have email addresses")

if __name__ == "__main__":
    asyncio.run(check_and_update_users())
