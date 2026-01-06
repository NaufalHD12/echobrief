import asyncio
import sys
import os

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.redis import redis_client

async def flush_redis():
    print("Connecting to Redis...")
    await redis_client.connect()
    print("Flushing all data...")
    if redis_client.client:
        k = await redis_client.client.flushall()
        print(f"Flushed: {k}")
    else:
        print("Failed to connect.")
    await redis_client.close()
    print("Done.")

if __name__ == "__main__":
    asyncio.run(flush_redis())
