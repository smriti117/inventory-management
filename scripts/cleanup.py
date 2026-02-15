import asyncio
import sys
import os

# Add the parent directory (project root) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import delete
from database.engine import AsyncSessionLocal
from models.users import Users


from sqlalchemy import text
from database.engine import AsyncSessionLocal


async def cleanup_data():
    async with AsyncSessionLocal() as session:
        print("Cleaning up seeded data and resetting IDs...")

        # Use TRUNCATE with RESTART IDENTITY to reset autoincrement sequences
        tables = [
            "inventory_transactions",
            "stocks",
            "purchase_order_items",
            "purchase_orders",
            "vendor_product_mappings",
            "products",
            "categories",
            "vendor_locations",
            "vendor_bank_details",
            "vendors",
            "users",
        ]

        for table in tables:
            await session.execute(
                text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE")
            )

        await session.commit()
        print("Cleanup and ID reset completed successfully!")


if __name__ == "__main__":
    asyncio.run(cleanup_data())
