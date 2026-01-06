import functools
import json
import logging
from typing import Any, Callable, Optional

from .redis import redis_client

logger = logging.getLogger(__name__)


def maintain_cache(prefix: str, ttl: int = 300):
    """
    Decorator to cache function results in Redis.
    Key format: prefix:arg1:arg2:...
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Construct cache key
            # Skip 'self' argument for instance methods
            start_index = 1 if args and hasattr(args[0], "__class__") else 0
            
            key_parts = [prefix]
            
            # Add positional args
            key_parts.extend([str(arg) for arg in args[start_index:]])
            
            # Add kwargs (sorted by key for consistency)
            for k, v in sorted(kwargs.items()):
                 if v is not None: # Include non-null kwargs to make unique keys
                    key_parts.append(f"{k}={v}")
            
            key = ":".join(key_parts)

            # Try to get from cache
            cached_value = await redis_client.get(key)
            if cached_value:
                logger.debug(f"Cache HIT: {key}")
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to decode cached value for {key}")

            # Execute function
            result = await func(*args, **kwargs)

            # Serialize result
            try:
                from enum import Enum

                def serialize_obj(obj):
                    if hasattr(obj, "model_dump"):
                        return serialize_obj(obj.model_dump())
                    elif isinstance(obj, (list, tuple)):
                        return [serialize_obj(item) for item in obj]
                    elif isinstance(obj, dict):
                        return {k: serialize_obj(v) for k, v in obj.items()}
                    elif isinstance(obj, Enum):
                        return obj.value
                    return obj

                serialized_data = serialize_obj(result)
                serialized = json.dumps(serialized_data, default=str)

                # Store in cache
                await redis_client.set(key, serialized, ttl)
                logger.debug(f"Cache SET: {key}")
            except Exception as e:
                logger.error(f"Failed to serialize/cache result for {key}: {e}")

            return result

        return wrapper

    return decorator
