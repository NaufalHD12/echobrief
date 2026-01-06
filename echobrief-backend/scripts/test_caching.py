import asyncio
import json
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel
from enum import Enum

# Add parent directory to path to allow importing app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from app.core.cache import maintain_cache
from app.core.redis import RedisClient, redis_client

class TestEnum(Enum):
    A = "a"
    B = "b"

class SimpleModel(BaseModel):
    id: int
    name: str
    status: TestEnum = TestEnum.A

@pytest.mark.asyncio
async def test_redis_client_singleton():
    client1 = RedisClient()
    client2 = RedisClient()
    assert client1 is client2

@pytest.mark.asyncio
async def test_maintain_cache_hit():
    # Mock redis_client.get to return a cached value
    cached_data = {"id": 1, "name": "Test", "status": "a"}
    
    with patch.object(redis_client, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = json.dumps(cached_data)

        class TestService:
            @maintain_cache(prefix="test", ttl=60)
            async def get_data(self, id: int):
                return {"id": id, "name": "Real", "status": "b"}

        service = TestService()
        # Call the decorated method
        result = await service.get_data(1)

        # Verify result matches cached data
        assert result == cached_data
        # Verify redis.get was called with correct key
        mock_get.assert_called_with("test:1")

@pytest.mark.asyncio
async def test_maintain_cache_miss():
    
    with patch.object(redis_client, 'get', new_callable=AsyncMock) as mock_get, \
         patch.object(redis_client, 'set', new_callable=AsyncMock) as mock_set:
        
        # Mock redis_client.get to return None (cache miss)
        mock_get.return_value = None
        mock_set.return_value = True

        class TestService:
            @maintain_cache(prefix="test", ttl=60)
            async def get_data(self, id: int):
                return {"id": id, "name": "Real", "status": TestEnum.A}

        service = TestService()
        # Call the decorated method
        result = await service.get_data(1)

        # Verify result matches real data (check that enum is preserved in return, though in reality it might be whatever the function returns)
        # The function returns a dict with valid types
        assert result == {"id": 1, "name": "Real", "status": TestEnum.A}
        
        # Verify redis.get was called
        mock_get.assert_called_with("test:1")
        # Verify redis.set was called with SERIALIZED values
        # Expect enum to be serialized to its value "a"
        mock_set.assert_called_with(
            "test:1", json.dumps({"id": 1, "name": "Real", "status": "a"}), 60
        )

@pytest.mark.asyncio
async def test_maintain_cache_complex_serialization():
    # Test serialization of nested models and tuples
    with patch.object(redis_client, 'get', new_callable=AsyncMock) as mock_get, \
         patch.object(redis_client, 'set', new_callable=AsyncMock) as mock_set:
        
        mock_get.return_value = None
        mock_set.return_value = True

        class TestService:
            @maintain_cache(prefix="complex", ttl=60)
            async def get_complex(self):
                # Return tuple containing list of Pydantic models and an int
                items = [SimpleModel(id=1, name="One", status=TestEnum.A), SimpleModel(id=2, name="Two", status=TestEnum.B)]
                return (items, 2)

        service = TestService()
        result = await service.get_complex()

        # Check result is original objects
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0][0], SimpleModel)

        # Verify what was set in Redis
        # Expect Enums to be serialized to "a" and "b"
        expected_json = json.dumps([
            [{"id": 1, "name": "One", "status": "a"}, {"id": 2, "name": "Two", "status": "b"}],
            2
        ])
        
        args = mock_set.call_args[0]
        assert args[0] == "complex"
        # Compare loaded JSONs to ignore ordering/indentation diffs
        assert json.loads(args[1]) == json.loads(expected_json)
