import asyncio
import sys
import os

# Add the parent directory (project root) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database.engine import Base, db_engine


async def reset_db():
    print("WARNING: This will drop ALL tables and types in the database.")
    print("Proceeding in 3 seconds... (Ctrl+C to cancel)")
    await asyncio.sleep(3)

    async with db_engine.begin() as conn:
        print("Dropping tables...")
        await conn.run_sync(Base.metadata.drop_all)

        print("Dropping enum types...")
        await conn.execute(text("DROP TYPE IF EXISTS userrole CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS purchaseorderstatus CASCADE"))
        await conn.execute(text("DROP TYPE IF EXISTS inventorytransactiontype CASCADE"))

        print("Cleaning alembic version...")
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))

        print("Recreating tables...")
        await conn.run_sync(Base.metadata.create_all)

    print(
        "Database reset successfully! Now run 'alembic stamp head' to sync migrations."
    )


if __name__ == "__main__":
    asyncio.run(reset_db())
