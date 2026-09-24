import json
import os

import redis
from dotenv import load_dotenv


load_dotenv()


# =========================================================
# REDIS CONFIGURATION
# =========================================================

REDIS_HOST = os.getenv(
    "REDIS_HOST",
    "localhost",
)

REDIS_PORT = int(
    os.getenv(
        "REDIS_PORT",
        "6379",
    )
)

DEFAULT_CACHE_TTL_SECONDS = 3600


# =========================================================
# REDIS CLIENT
# =========================================================

def get_redis_client():
    """
    Create a Redis client using environment configuration.

    decode_responses=True ensures Redis returns normal
    Python strings instead of bytes.
    """

    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )


# =========================================================
# CONNECTION CHECK
# =========================================================

def test_redis_connection():
    """
    Test whether Redis is currently reachable.

    Returns True when Redis responds successfully.
    Returns False when Redis is unavailable.

    Redis is treated as a cache/session service, so an
    unavailable Redis instance should not crash the core
    credit-advisory workflow.
    """

    try:
        client = get_redis_client()
        return bool(client.ping())

    except redis.RedisError:
        return False


# =========================================================
# JSON CACHE OPERATIONS
# =========================================================

def set_json_cache(
    key,
    value,
    ttl_seconds=DEFAULT_CACHE_TTL_SECONDS,
):
    """
    Store a JSON-serializable value in Redis.

    Returns True when the value is stored successfully.
    Returns False if Redis is unavailable.
    """

    try:
        client = get_redis_client()

        serialized_value = json.dumps(
            value
        )

        client.setex(
            key,
            ttl_seconds,
            serialized_value,
        )

        return True

    except (
        redis.RedisError,
        TypeError,
        ValueError,
    ):
        return False


def get_json_cache(key):
    """
    Retrieve and deserialize a JSON value from Redis.

    Returns None when:
    - the key does not exist,
    - Redis is unavailable, or
    - the stored value cannot be decoded.
    """

    try:
        client = get_redis_client()

        cached_value = client.get(
            key
        )

        if cached_value is None:
            return None

        return json.loads(
            cached_value
        )

    except (
        redis.RedisError,
        json.JSONDecodeError,
    ):
        return None


def delete_cache(key):
    """
    Delete a Redis cache entry.

    Returns True when Redis processed the request.
    Returns False when Redis is unavailable.
    """

    try:
        client = get_redis_client()

        client.delete(
            key
        )

        return True

    except redis.RedisError:
        return False


# =========================================================
# DIRECT MODULE TEST
# =========================================================

if __name__ == "__main__":

    print(
        "Testing Redis connection..."
    )

    if test_redis_connection():

        print(
            "Redis connection successful."
        )

        test_key = (
            "credit_advisory:"
            "connection_test"
        )

        test_value = {
            "status": "working",
            "service": "redis",
        }

        stored = set_json_cache(
            test_key,
            test_value,
            ttl_seconds=60,
        )

        retrieved = get_json_cache(
            test_key
        )

        print(
            "Cache write successful:",
            stored,
        )

        print(
            "Cached value:",
            retrieved,
        )

        delete_cache(
            test_key
        )

        print(
            "Test cache entry deleted."
        )

    else:

        print(
            "Redis is currently unavailable."
        )