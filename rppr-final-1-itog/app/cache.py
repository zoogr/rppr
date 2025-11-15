import redis
import json
import pickle
from typing import Any, Optional
from functools import wraps

# Настройки Redis
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
CACHE_EXPIRE_SECONDS = 300  # 5 минут


class RedisCache:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=False
        )

    def set(self, key: str, value: Any, expire: int = CACHE_EXPIRE_SECONDS) -> bool:
        """Сохранить значение в кеш"""
        try:
            serialized_value = pickle.dumps(value)
            return self.redis_client.setex(key, expire, serialized_value)
        except Exception:
            return False

    def get(self, key: str) -> Optional[Any]:
        """Получить значение из кеша"""
        try:
            cached_value = self.redis_client.get(key)
            if cached_value:
                return pickle.loads(cached_value)
            return None
        except Exception:
            return None

    def delete(self, key: str) -> bool:
        """Удалить значение из кеша"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception:
            return False

    def delete_pattern(self, pattern: str) -> bool:
        """Удалить все ключи по паттерну"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return bool(self.redis_client.delete(*keys))
            return True
        except Exception:
            return False

    def flush_all(self) -> bool:
        """Очистить весь кеш"""
        try:
            return self.redis_client.flushdb()
        except Exception:
            return False


# Создаем глобальный экземпляр кеша
cache = RedisCache()


def cached(key_pattern: str = None, expire: int = CACHE_EXPIRE_SECONDS):
    """
    Декоратор для кеширования результатов функций

    Args:
        key_pattern: Паттерн для ключа кеша (может содержать {args} для подстановки)
        expire: Время жизни кеша в секундах
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Генерируем ключ кеша
            if key_pattern:
                cache_key = key_pattern.format(**kwargs)
            else:
                # Автогенерация ключа на основе имени функции и аргументов
                cache_key = f"{func.__module__}:{func.__name__}:{str(args)}:{str(kwargs)}"

            # Пробуем получить из кеша
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Выполняем функцию если нет в кеше
            result = await func(*args, **kwargs)

            # Сохраняем в кеш
            cache.set(cache_key, result, expire=expire)

            return result

        return wrapper

    return decorator


def invalidate_cache(pattern: str):
    """
    Декоратор для инвалидации кеша после выполнения функции
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)

            # Инвалидируем кеш
            cache.delete_pattern(pattern)

            return result

        return wrapper

    return decorator