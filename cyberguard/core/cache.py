import aiocache
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from cyberguard.core.config import settings

# Redis'e bağlanmaya çalış. Bağlanamazsa, sistemin çökmesini engellemek için bir 'Memory' cache kullan.
try:
    redis_cache = aiocache.Cache(
        Cache.REDIS,
        endpoint=settings.REDIS_URL,
        serializer=JsonSerializer(),
        namespace="aegismatrix"
    )
    print("✅ Redis bağlantısı başarıyla kuruldu!")
except Exception as e:
    print(f"⚠️ Redis bağlanamadığı için sistem yine de çalışıyor. Hata: {e}")
    # Geçici olarak basit bir bellek önbelleği kullan
    redis_cache = aiocache.Cache(
        Cache.MEMORY,
        serializer=JsonSerializer(),
        namespace="aegismatrix"
    )

def get_cache():
    return redis_cache
