# app/redis_client.py

import redis
import os

# Lấy URL Redis từ biến môi trường hoặc gán trực tiếp
# Bạn có thể copy URL từ Upstash dashboard
REDIS_URL = os.getenv("REDIS_URL", "rediss://default:AaVdAAIncDJhMTQzMDBmNzEwZGI0ZTMxOGNmNjNhZjZkYjg5MGM2MnAyNDIzMzM@up-kitten-42333.upstash.io:6379")

# Tạo client Redis
r = redis.from_url(
    REDIS_URL,
    decode_responses=True  # luôn trả về string thay vì bytes
)

# Hàm tiện ích tạo cache key dựa trên prefix + các tham số
import json
import hashlib

def make_cache_key(prefix: str, **kwargs) -> str:
    """
    Tạo key duy nhất cho cache từ prefix và các tham số.
    Ví dụ:
        make_cache_key("search", name="abc", page=1)
    """
    raw = prefix + "_" + json.dumps(kwargs, sort_keys=True, default=str)
    return hashlib.md5(raw.encode()).hexdigest()


# Hàm tiện ích lưu cache với TTL (giây)
def set_cache(key: str, value, ttl: int = 300):
    """
    Lưu giá trị vào Redis dưới dạng JSON
    ttl: thời gian sống (giây)
    """
    r.setex(key, ttl, json.dumps(value, default=str))

# Hàm tiện ích lấy cache
def get_cache(key: str):
    """
    Lấy dữ liệu từ Redis, trả về dict/list đã decode JSON hoặc None
    """
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    return None
