import redis.asyncio as redis
from typing import Any, Optional, List
import json
import logging
from ..config import settings, get_redis_url

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self):
        self.redis_url = get_redis_url()
        self.redis_client = None
        self.default_expire = settings.cache_expire_minutes * 60  # Convert to seconds

    async def get_client(self) -> redis.Redis:
        """Get Redis client, creating connection if needed"""
        if self.redis_client is None:
            try:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30
                )
                
                # Test connection
                await self.redis_client.ping()
                logger.info(f"Connected to Redis at {self.redis_url}")
                
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self.redis_client = None
                raise
        
        return self.redis_client

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            client = await self.get_client()
            value = await client.get(key)
            
            if value is not None:
                return json.loads(value)
            return None
            
        except Exception as e:
            logger.error(f"Cache get failed for key '{key}': {e}")
            return None

    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a value in cache"""
        try:
            client = await self.get_client()
            expire_time = expire or self.default_expire
            
            serialized = json.dumps(value, default=str)  # default=str handles datetime objects
            result = await client.setex(key, expire_time, serialized)
            
            logger.debug(f"Cached key '{key}' for {expire_time} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Cache set failed for key '{key}': {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        try:
            client = await self.get_client()
            result = await client.delete(key)
            
            if result:
                logger.debug(f"Deleted cache key '{key}'")
            
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache delete failed for key '{key}': {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern"""
        try:
            client = await self.get_client()
            
            # Find all keys matching the pattern
            keys = await client.keys(pattern)
            
            if keys:
                # Delete all matching keys
                deleted = await client.delete(*keys)
                logger.info(f"Cleared {deleted} cache keys matching pattern '{pattern}'")
                return deleted
            
            return 0
            
        except Exception as e:
            logger.error(f"Cache clear pattern failed for '{pattern}': {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache"""
        try:
            client = await self.get_client()
            result = await client.exists(key)
            return bool(result)
            
        except Exception as e:
            logger.error(f"Cache exists check failed for key '{key}': {e}")
            return False

    async def ttl(self, key: str) -> int:
        """Get time-to-live for a key"""
        try:
            client = await self.get_client()
            return await client.ttl(key)
            
        except Exception as e:
            logger.error(f"Cache TTL check failed for key '{key}': {e}")
            return -1

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in cache"""
        try:
            client = await self.get_client()
            return await client.incrby(key, amount)
            
        except Exception as e:
            logger.error(f"Cache increment failed for key '{key}': {e}")
            return 0

    async def get_multiple(self, keys: List[str]) -> List[Optional[Any]]:
        """Get multiple values from cache"""
        try:
            client = await self.get_client()
            values = await client.mget(keys)
            
            result = []
            for value in values:
                if value is not None:
                    result.append(json.loads(value))
                else:
                    result.append(None)
            
            return result
            
        except Exception as e:
            logger.error(f"Cache mget failed for keys {keys}: {e}")
            return [None] * len(keys)

    async def set_multiple(self, mapping: dict, expire: Optional[int] = None) -> bool:
        """Set multiple key-value pairs"""
        try:
            client = await self.get_client()
            expire_time = expire or self.default_expire
            
            # Serialize all values
            serialized_mapping = {
                key: json.dumps(value, default=str) 
                for key, value in mapping.items()
            }
            
            # Use pipeline for efficiency
            async with client.pipeline() as pipe:
                await pipe.mset(serialized_mapping)
                
                # Set expiration for all keys
                for key in serialized_mapping.keys():
                    await pipe.expire(key, expire_time)
                
                await pipe.execute()
            
            logger.debug(f"Set {len(mapping)} cache keys with {expire_time}s expiration")
            return True
            
        except Exception as e:
            logger.error(f"Cache mset failed: {e}")
            return False

    async def health_check(self) -> dict:
        """Check Redis connection health"""
        try:
            client = await self.get_client()
            info = await client.info()
            
            return {
                "status": "healthy",
                "redis_version": info.get("redis_version"),
                "used_memory": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "total_commands_processed": info.get("total_commands_processed")
            }
            
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    async def flush_all(self) -> bool:
        """Flush all cache data (use with caution!)"""
        try:
            client = await self.get_client()
            await client.flushall()
            
            logger.warning("Flushed all cache data")
            return True
            
        except Exception as e:
            logger.error(f"Cache flush all failed: {e}")
            return False

    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            try:
                await self.redis_client.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Failed to close Redis connection: {e}")
            finally:
                self.redis_client = None